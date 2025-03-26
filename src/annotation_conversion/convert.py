"""Utilities for converting annotations. Clear of cloud-specific things."""
import logging
import openslide
import numpy as np
import highdicom as hd
from pathlib import Path
from wsidicomizer import WsiDicomizer
from pydicom import Dataset
from pydicom.sr.codedict import codes
from typing import List, Tuple, Union

import metadata_config
from data_utils import CellAnnotation, ROIAnnotation


def _get_spatial_information_from_mrxs(mrxs_image_path: Path) -> Tuple[list[float], list[float], list[float]]: 
    """ 
    Function to retrieve spatial information such as image position, image orientation and pixel spacing 
    of the base level from a MRXS slide. 
    """
    with WsiDicomizer.open(mrxs_image_path) as slide: 
        spatial_information_mrxs = (
            [slide.metadata.image.image_coordinate_system.origin.x, slide.metadata.image.image_coordinate_system.origin.y, 0.], 
            slide.metadata.image.image_coordinate_system.orientation.values,
            [slide.metadata.image.pixel_spacing.width, slide.metadata.image.pixel_spacing.height]
        )
    return spatial_information_mrxs
    

def process_annotation(
    ann: Union[CellAnnotation, ROIAnnotation],
    offset_transformer: Union[hd.spatial.ImageToImageTransformer,None], 
    bounds: Tuple[int], 
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
    offset_transformer: Union[hd.spatial.ImageToImageTransformer, None]
        Transformer object to account for the offset that is introduced during 
        conversion from MRXS to DICOM with wsidicomizer.  
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
    xmin, ymin, xmax, ymax = xmin-bounds[0], ymin-bounds[1], xmax-bounds[0], ymax-bounds[1] 
    
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
    
    if offset_transformer: 
        graphic_data = offset_transformer(graphic_data)
    
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

    # Conversion of images from MIRAX to DICOM with wsidicomizer introduces an offset,
    # by which we need to shift the annotations to match the DICOM images. 
    # See https://github.com/imi-bigpicture/wsidicomizer/issues/56 for more information.
    # TODO: make easier understandable with offset and x-off, y-off 
    with openslide.OpenSlide(mrxs_source_image_path) as slide: 
        mrxs_height, mrxs_width = slide.dimensions[1], slide.dimensions[0]
        x_off, y_off = int(slide.properties['openslide.bounds-x']), int(slide.properties['openslide.bounds-y'])

    if mrxs_height != source_image_metadata.TotalPixelMatrixRows or mrxs_width != source_image_metadata.TotalPixelMatrixColumns:
        spatial_information_mrxs = _get_spatial_information_from_mrxs(mrxs_source_image_path)
        spatial_information_dcm = hd.spatial._get_spatial_information(source_image_metadata, for_total_pixel_matrix=True)
        offset_transformer = hd.spatial.ImageToImageTransformer(
            image_position_from=spatial_information_mrxs[0],
            image_orientation_from=spatial_information_mrxs[1],
            pixel_spacing_from=spatial_information_mrxs[2],
            image_position_to=spatial_information_dcm[0],
            image_orientation_to=spatial_information_dcm[1],
            pixel_spacing_to=spatial_information_dcm[2], 
        )
    else: 
        offset_transformer = None 

    graphic_data = []
    for ann in annotations:
        print('bbb', ann.bounding_box)
        graphic_item = process_annotation(
            ann,
            offset_transformer, 
            (x_off, y_off),
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
        label='monolayer', 
        annotated_property_category=metadata_config.roi_labels['monolayer'][0], 
        annotated_property_type=metadata_config.roi_labels['monolayer'][1], 
        graphic_type=graphic_type,
        graphic_data=graphic_data,
        algorithm_type=metadata_config.algorithm_type,
        measurements=[
            hd.ann.Measurements(
                name=codes.DCM.ReferencedRegionOfInterestIdentifier,
                unit=codes.UCUM.NoUnits,
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

    groups = []
    group_number = 1
    for label in sorted(metadata_config.cell_labels): 
        indices = np.where(np.array(labels) == label)[0].tolist()
        if len(indices) > 0: 
            group = hd.ann.AnnotationGroup(
                number=group_number,
                uid=hd.UID(),
                label=label,
                annotated_property_category=metadata_config.cell_labels[label][0],
                annotated_property_type=metadata_config.cell_labels[label][1],
                graphic_type=graphic_type,
                graphic_data=[graphic_data[i] for i in indices],
                algorithm_type=metadata_config.algorithm_type,
                measurements=[
                    hd.ann.Measurements(
                        name=codes.DCM.Identifier,
                        unit=codes.UCUM.NoUnits,
                        values=np.array([cell_identifiers[i] for i in indices]),
                    ), 
                    hd.ann.Measurements(
                        name=codes.DCM.ReferencedRegionOfInterestIdentifier,
                        unit=codes.UCUM.NoUnits,
                        values=np.array([roi_identifiers[i] for i in indices]),
                    )
                ],
            )
            groups.append(group)
            group_number += 1

    annotations = hd.ann.MicroscopyBulkSimpleAnnotations(
        series_description=metadata_config.series_description_cell_anns,
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
    return annotations
