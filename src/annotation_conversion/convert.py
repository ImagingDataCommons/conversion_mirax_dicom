"""Utilities for converting annotations. Clear of cloud-specific things."""
import logging
import openslide
import numpy as np
import highdicom as hd
from pathlib import Path
from pydicom import Dataset
from typing import List, Tuple, Union

import metadata_config
from data_utils import CellAnnotation, ROIAnnotation


def process_annotation(
    ann: Union[CellAnnotation, ROIAnnotation],
    openslide_bounds: Tuple[int], 
    img_to_ref_transformer: hd.spatial.ImageToReferenceTransformer,
    graphic_type: hd.ann.GraphicTypeValues,
    annotation_coordinate_type: hd.ann.AnnotationCoordinateTypeValues
    ) -> np.ndarray:
    """
    Process a single annotation to be in the format required for DICOM ANN files.

    Parameters
    ----------
    ann: CellAnnotation, ROIAnnotation
        Single annotation.  
    openslide_bounds: Tuple[int]
        Openslide image bounds to be subtracted from the annotation coordinates.  
    img_to_ref_transformer: hd.spatial.ImageToReferenceTransformer
        Transformer object to map image coordinates to reference coordinates
        for the image.
    graphic_type: hd.ann.GraphicTypeValues, optional 
        Graphic type to use to store all nuclei. Allowed options are 'RECTANGLE' (default)
        or 'POINT'. 
    annotation_coordinate_type: hd.ann.AnnotationCoordinateTypeValues, optional
        Store coordinates in the Bulk Microscopy Bulk Simple Annotations in the
        (3D) frame of reference (SCOORD3D), or the (2D) total pixel matrix
        (SCOORD, default).

    Returns
    -------
    graphic_data: np.ndarray
        Numpy array of float32 coordinates to include in the Bulk Microscopy
        Simple Annotations.
    """      
    xmin, ymin, xmax, ymax = ann.bounding_box 
    xmin, ymin, xmax, ymax = xmin-openslide_bounds[0], ymin-openslide_bounds[1], xmax-openslide_bounds[0], ymax-openslide_bounds[1]
    
    if graphic_type == hd.ann.GraphicTypeValues.RECTANGLE:
        graphic_data = np.array(
            [
                [xmin, ymin],
                [xmax, ymin],
                [xmax, ymax],
                [xmin, ymax],
            ]
        )
    elif graphic_type == hd.ann.GraphicTypeValues.POINT:
        graphic_data = np.array(
            [
                [xmin + (xmax-xmin)//2, ymin + (ymax-ymin)//2]
            ]
        )
    else:
        raise ValueError(
            f'Graphic type "{graphic_type.value}" not supported.'
        )

    use_3d = (
        annotation_coordinate_type ==
        hd.ann.AnnotationCoordinateTypeValues.SCOORD3D
    )
    if use_3d:
        graphic_data = img_to_ref_transformer(graphic_data)

    return graphic_data.astype(np.float32)


def get_graphic_data(
    annotations: List[CellAnnotation],
    source_image_metadata: Dataset,
    mrxs_source_image_path: Path, 
    graphic_type: str = 'RECTANGLE',
    annotation_coordinate_type: str = 'SCOORD'
    ) -> List[np.ndarray]:
    """
    Parse annotations to construct graphic data.

    Parameters
    ----------
    annotations: List[CellAnnotations]
        List of annotations for the slide. 
    source_image_metadata: pydicom.Dataset
        Pydicom datasets containing the metadata of the reference image (already
        converted to DICOM format). This can be the full image datasets, but the
        PixelData attributes are not required.
    mrxs_source_image_path: Path
        Path to MRXS source image. 
    graphic_type: str, optional 
        Graphic type to use to store all nuclei. Allowed options are 'RECTANGLE' (default)
        or 'POINT'.
    annotation_coordinate_type: str, optional
        Store coordinates in the Bulk Microscopy Bulk Simple Annotations in the
        (3D) frame of reference (SCOORD3D), or the (2D) total pixel matrix
        (SCOORD, default).

    Returns
    -------
    graphic_data: list[np.ndarray]
        List of graphic data as numpy arrays in the format required for the
        MicroscopyBulkSimpleAnnotations object. These are correctly formatted
        for the requested graphic type and annotation coordinate type. 
    """  
    graphic_type = hd.ann.GraphicTypeValues[graphic_type]
    annotation_coordinate_type = hd.ann.AnnotationCoordinateTypeValues[
        annotation_coordinate_type
    ]

    img_to_ref_transformer = hd.spatial.ImageToReferenceTransformer.for_image(
        source_image_metadata,
        for_total_pixel_matrix=True,
    )

    # The original annotations were created from the original MRXS slide corner. Since wsidicomizer crops the 
    # images based on the openslide bounds, we need to subtract the openslide bounds also from the annotation coordinates. 
    with openslide.OpenSlide(mrxs_source_image_path) as slide: 
        openslide_bounds = int(slide.properties['openslide.bounds-x']), int(slide.properties['openslide.bounds-y'])

    graphic_data = []
    for ann in annotations:
        graphic_item = process_annotation(
            ann,
            openslide_bounds, 
            img_to_ref_transformer,
            graphic_type,
            annotation_coordinate_type,
        )
        graphic_data.append(graphic_item)   
    logging.info(f'Parsed {len(graphic_data)} annotations.')
    return graphic_data


def create_bulk_annotations_for_rois(
    source_image_metadata: Dataset,
    graphic_data: list[np.ndarray],
    identifiers: list[int],
    series_uid: hd.UID, 
    sop_instance_number: int,
    graphic_type: str = 'RECTANGLE',
    annotation_coordinate_type: str = 'SCOORD', 
 

    ) -> hd.ann.MicroscopyBulkSimpleAnnotations:
    """
    Create DICOM Microscopy Bulk Simple Annotation objects. 

    Parameters
    ----------
    source_image_metadata: pydicom.Dataset
        Metadata of the image from which annotations were derived.
    graphic_data: list[np.ndarray]
        Pre-computed graphic data for the graphic type and annotation
        coordinate type.
    identifiers: list[int]
        Identifier for each ROI annotation taken as is from input. 
    series_uid: hd.UID
        DICOM SeriesInstanceUID. All annotation steps, plus consensus and ROIs go into the same Series. 
    sop_instance_number: 
        Number of the SOPInstance within the DICOM Series. 
    graphic_type: str, optional 
        Graphic type to use to store all nuclei. Allowed options are 'RECTANGLE' (default)
        or 'POINT'.
    annotation_coordinate_type: hd.ann.AnnotationCoordinateTypeValues, optional
        Store coordinates in the Bulk Microscopy Bulk Simple Annotations in the
        (3D) frame of reference (SCOORD3D), or the (2D) total pixel matrix
        (SCOORD, default).
    
        
    Returns
    -------
    annotation: hd.ann.MicroscopyBulkSimpleAnnotations:
        DICOM bulk microscopy annotation encoding the original annotations in
        vector format.

    """
    graphic_type = hd.ann.GraphicTypeValues[graphic_type]
    annotation_coordinate_type = hd.ann.AnnotationCoordinateTypeValues[
        annotation_coordinate_type
    ]
    
    group = hd.ann.AnnotationGroup(
        number=1,
        uid=hd.UID(),
        label='region_of_interest', 
        annotated_property_category=metadata_config.roi_labels['region_of_interest'][0], 
        annotated_property_type=metadata_config.roi_labels['region_of_interest'][1], 
        graphic_type=graphic_type,
        graphic_data=graphic_data,
        algorithm_type=metadata_config.algorithm_type,
        measurements=[
            hd.ann.Measurements(
                name=metadata_config.code_roi_identifier,
                unit=metadata_config.unit_identifier,
                values=np.array(identifiers),
            )
        ],
    )

    annotations = hd.ann.MicroscopyBulkSimpleAnnotations(
        series_description=metadata_config.series_description_roi_anns,
        source_images=[source_image_metadata],
        annotation_coordinate_type=annotation_coordinate_type,
        annotation_groups=[group],
        series_instance_uid=series_uid,  
        series_number=33, # no deeper meaning, just higher number in case other series with images might be added   
        sop_instance_uid=hd.UID(),
        instance_number=sop_instance_number, 
        manufacturer=metadata_config.manufacturer,
        manufacturer_model_name=metadata_config.manufacturer_model_name,
        software_versions=metadata_config.software_versions,
        device_serial_number=metadata_config.device_serial_number,
    )

    return annotations


def create_bulk_annotations_for_cells(
    source_image_metadata: Dataset,
    graphic_data: list[np.ndarray],
    cell_identifiers: list[int],
    roi_identifiers: list[int], 
    labels: list[str],
    ann_session: str, 
    series_uid: hd.UID, 
    sop_instance_number: int,
    graphic_type: str = 'RECTANGLE',
    annotation_coordinate_type: str = 'SCOORD'
    ) -> hd.ann.MicroscopyBulkSimpleAnnotations:
    """
    Create DICOM Microscopy Bulk Simple Annotation objects. 

    Parameters
    ----------
    source_image_metadata: pydicom.Dataset
        Metadata of the image from which annotations were derived.
    graphic_data: list[np.ndarray]
        Pre-computed graphic data for the graphic type and annotation
        coordinate type.
    cell_identifiers: list[int]
        Identifier for each cell annotation taken as is from input. 
    roi_identifiers: list[int]
        Identifier for each cell annotation indicating which ROI they are part of. 
    labels: list[str]
        Label for each annotation taken as is from input. 
    ann_session: str 
        Identifier of the step in the annotation process.
    series_uid: hd.UID
        DICOM SeriesInstanceUID. Each annotation steps, consensus and ROIs go into a separate Series. 
    sop_instance_number: 
        Number of the SOPInstance within the DICOM Series. 
    graphic_type: str, optional 
        Graphic type to use to store all nuclei. Allowed options are 'RECTANGLE' (default)
        or 'POINT'.
    annotation_coordinate_type: hd.ann.AnnotationCoordinateTypeValues, optional
        Store coordinates in the Bulk Microscopy Bulk Simple Annotations in the
        (3D) frame of reference (SCOORD3D), or the (2D) total pixel matrix
        (SCOORD, default).

    Returns
    -------
    annotation: hd.ann.MicroscopyBulkSimpleAnnotations:
        DICOM bulk microscopy annotation encoding the original annotations in
        vector format.

    """
    graphic_type = hd.ann.GraphicTypeValues[graphic_type]
    annotation_coordinate_type = hd.ann.AnnotationCoordinateTypeValues[
        annotation_coordinate_type
    ]

    groups = []
    group_number = 1
    for label in sorted(metadata_config.cell_labels):
        # Encode cells which are within a ROI
        indices_in_roi = np.where((np.array(labels) == label) & (np.array(roi_identifiers) != -1))[0].tolist()
        if len(indices_in_roi) > 0: 
            group = hd.ann.AnnotationGroup(
                number=group_number,
                uid=hd.UID(),
                label=label,
                annotated_property_category=metadata_config.cell_labels[label][0],
                annotated_property_type=metadata_config.cell_labels[label][1],
                graphic_type=graphic_type,
                graphic_data=[graphic_data[i] for i in indices_in_roi],
                algorithm_type=metadata_config.algorithm_type,
                measurements=[
                    hd.ann.Measurements(
                        name=metadata_config.code_cell_identifier, 
                        unit=metadata_config.unit_identifier,
                        values=np.array([cell_identifiers[i] for i in indices_in_roi]),
                    ), 
                    hd.ann.Measurements(
                        name=metadata_config.code_ref_to_roi_identifier,
                        unit=metadata_config.unit_identifier,
                        values=np.array([roi_identifiers[i] for i in indices_in_roi]),
                    )
                ],
            )
            groups.append(group)
            group_number += 1

        # Encode cells which are outside of a ROI
        indices_out_of_roi = np.where((np.array(labels) == label) & (np.array(roi_identifiers) == -1))[0].tolist()
        if len(indices_out_of_roi) > 0: 
            group = hd.ann.AnnotationGroup(
                number=group_number,
                uid=hd.UID(),
                label=label,
                annotated_property_category=metadata_config.cell_labels[label][0],
                annotated_property_type=metadata_config.cell_labels[label][1],
                graphic_type=graphic_type,
                graphic_data=[graphic_data[i] for i in indices_out_of_roi],
                algorithm_type=metadata_config.algorithm_type,
                measurements=[
                    hd.ann.Measurements(
                        name=metadata_config.code_cell_identifier, 
                        unit=metadata_config.unit_identifier,
                        values=np.array([cell_identifiers[i] for i in indices_out_of_roi]),
                    ),
                ],
            )
            groups.append(group)
            group_number += 1

    annotations = hd.ann.MicroscopyBulkSimpleAnnotations(
        series_description=metadata_config.series_description_cell_anns(ann_session),
        source_images=[source_image_metadata],
        annotation_coordinate_type=annotation_coordinate_type,
        annotation_groups=groups,
        series_instance_uid=series_uid, 
        series_number=33, # no deeper meaning, just higher number in case other series with images might be added
        sop_instance_uid=hd.UID(),
        instance_number=sop_instance_number, 
        manufacturer=metadata_config.manufacturer,
        manufacturer_model_name=metadata_config.manufacturer_model_name,
        software_versions=metadata_config.software_versions,
        device_serial_number=metadata_config.device_serial_number,
    )

    # adding indicator for annotation session
    for elem in metadata_config.add_clinical_trial_series_id(str(ann_session)): 
        annotations.add(elem) 

    return annotations