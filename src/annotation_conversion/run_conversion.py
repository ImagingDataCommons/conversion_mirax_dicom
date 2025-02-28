"""Entrypoint for annotation conversion."""
import os
import datetime
import pydicom 
import logging
import argparse
import pandas as pd
import highdicom as hd
from pathlib import Path
from time import time
from typing import Any, Dict, Union  

from data_utils import CellAnnotation, ROIAnnotation, preprocess_annotation_csvs, filter_slide_annotations
from convert import get_graphic_data, create_bulk_annotations_for_rois, create_bulk_annotations_for_cells


def get_source_image_metadata(slide_dir: Path) -> Dict[str, Any]: 
    """ 
    Function that finds the source image file (base level) and extracts relevant metadata. 
    
    Parameters
    ----------
    slide_dir: Path
        Folder containing image data for the respective slide

    Returns
    -------
    data: dict[str, Any]
        Output data packed into a dict. This will contain 
        - slide_id: str 
        - source_image: pydicom.Dataset 
            pydicom-read metadata excluding pixel data
    """

    def find_base_level(dcm_dir: Path) -> Path:
        """ Find base level (i.e. largest file) in folder. """ 
        base_level = None
        largest_size = 0
        for level in [p.resolve() for p in dcm_dir.iterdir()]: 
            level_size = os.path.getsize(level)
            if level_size > largest_size: 
                largest_size = level_size
                base_level = level
        return base_level

    base_level = find_base_level(slide_dir)
    ds = pydicom.dcmread(base_level, stop_before_pixels=True)
    
    data = dict( 
        slide_id = slide_dir.stem, 
        source_image = ds
    )
    return data 


def parse_roi_annotations(data: Dict[str, Any], annotations: pd.DataFrame) -> Dict[str, Any]: 
    """ 
    Parses annotations from pd.DataFrame into a list of ROIAnnotations. 

    Parameters
    ----------
    data: dict[str, Any]
        Input data packed into a dict, including at least:
        - slide_id: str
            Slide ID for the case.
        - source_image: pydicom.Dataset
            Base level source image for this case.

    Returns
    -------
    data: dict[str, Any]
        Output data packed into a dict. This will contain the same keys as
        the input dictionary, plus the following additional keys:
        - ann_type: str
            Whether it's ROI or cell annotations.
        - ann: list[ROIAnnotation]
            List of annotations. 
    """

    ann = []
    for _, row in annotations.iterrows(): 
        x_min, y_min = row['x_in_slide'], row['y_in_slide']
        x_max, y_max = x_min + row['width'], y_min + row['height']
        ann.append(ROIAnnotation(
            identifier=row['id'], 
            bounding_box=(x_min, y_min, x_max, y_max), 
        ))

    data['ann_type'] = 'roi'
    data['ann'] = ann
    return data


def parse_cell_annotations(data: Dict[str, Any], annotations: pd.DataFrame, ann_step: Union[int, str]) -> Dict[str, Any]: 
    """ 
    Parses annotations from pd.DataFrame into a list of CellAnnotations. 

    Parameters
    ----------
    data: dict[str, Any]
        Input data packed into a dict, including at least:
        - slide_id: str
            Slide ID for the case.
        - source_image: pydicom.Dataset
            Base level source image for this case.

    Returns
    -------
    data: dict[str, Any]
        Output data packed into a dict. This will contain the same keys as
        the input dictionary, plus the following additional keys:
        - ann_type: str
            Whether it's ROI or cell annotations.
        - ann: list[CellAnnotation]
            List of annotations. 
    """

    ann = []
    for _, row in annotations.iterrows(): 
        x_min, y_min = row['x_in_slide'], row['y_in_slide']
        x_max, y_max = x_min + row['cell_width'], y_min + row['cell_height']
        if ann_step == 'consensus': 
            cell_label = row['original_consensus_label']
        else: 
            cell_label = row['all_original_annotations'].split(',')[ann_step]
        ann.append(CellAnnotation(
            cell_identifier=row['cell_id'], 
            roi_identifier=row['rocellboxing_id'],
            bounding_box=(x_min, y_min, x_max, y_max), 
            label=cell_label
        ))

    data['ann_type'] = 'cell'
    data['ann'] = ann
    return data


def parse_annotations_to_graphic_data(
    data: Dict[str, Any],
    graphic_type: str, 
    annotation_coordinate_type: str,
    output_dir: Path
    ) -> Dict[str, Any]:

    """
    Parse cell or ROI annotations to highdicom graphic data.

    Parameters
    ----------
    data: dict[str, Any]
        Input data packed into a dict, including at least:
        - slide_id: str
            Slide ID for the case.
        - source_image: pydicom.Dataset
            Base level source image for this case.
        - ann: Union[list[CellAnnotations], list[ROIAnnotations]]
            List of cell annotations or ROI annotations. 
    graphic_type: hd.ann.GraphicTypeValues
        Graphic type to use to store all nuclei. Allowed options are 'RECTANGLE' (default)
        or 'POINT' (will be bounding box centroid). 
    annotation_coordinate_type: hd.ann.AnnotationCoordinateTypeValues
        Store coordinates in the Bulk Microscopy Bulk Simple Annotations in
        the (3D) frame of reference (SCOORD3D), or the (2D) total pixel
        matrix (SCOORD, default).
    output_dir: pathlib.Path
        A local output directory to store error logs.

    Returns
    -------
    data: dict[str, Any]
        Output data packed into a dict. This will contain the same keys as
        the input dictionary, plus the following additional keys:

        - graphic_data: list[np.ndarray]
            List of graphic data as numpy arrays in the format required for
            the MicroscopyBulkSimpleAnnotations object. These are correctly
            formatted for the requested graphic type and annotation
            coordinate type.
        
        In case of ROI annotations, these keys are also added: 
        - identifiers: list[int]
            Identifier for each of the ROI.

        In case of cell annotations, these keys are added: 
        - cell_identifiers: list[int]
            Identifier for each of the bounding boxes. The identifier is a consecutive number 
            going over the whole dataset (not only a single slide).
        - roi_identifiers: list[int]
            Identifier for each of the bounding boxes. The identifier indicates the ROI that this 
            bounding box is contained in, i.e. in which ROI the cell annotation can be found. 
        - labels: list[str]
            Label for each bounding box.
    """

    errors = []
    slide_id = data['slide_id']

    start_time = time()
    logging.info(f'Parsing annotations for slide: {slide_id}')
    try:
        graphic_data = get_graphic_data(
            annotations=data['ann'],
            source_image_metadata=data['source_image'],
            graphic_type=graphic_type,
            annotation_coordinate_type=annotation_coordinate_type,
        )
    except Exception as e:
        logging.error(f'Error {str(e)}')
        errors.append(
            {
                'slide_id': slide_id,
                'error_message': str(e),
                'datetime': str(datetime.datetime.now()),
            }
        )
        errors_df = pd.DataFrame(errors)
        errors_df.to_csv(output_dir / 'conversion_error_log.txt')
        return None

    stop_time = time()
    duration = stop_time - start_time
    logging.info(
        f'Processed annotations for slide {slide_id} in {duration:.2f}s'
    )
    
    data['graphic_data'] = graphic_data
    if isinstance(data['ann'][0], ROIAnnotation): 
        data['identifiers'] = [ann.identifier for ann in data['ann']]
    else: 
        data['cell_identifiers'] = [ann.cell_identifier for ann in data['ann']]
        data['roi_identifiers'] = [ann.roi_identifier for ann in data['ann']]
        data['labels'] = [ann.label for ann in data['ann']]
    del data['ann'] # save some memory
    return data


def create_dcm_annotations(
    data: Dict[str, Any],
    series_uid: hd.UID, 
    sop_instance_number: int,
    graphic_type: str,
    annotation_coordinate_type: str,
    output_dir: Path, 
    ) -> Dict[str, Any]:

    """
    Creates bulk annotations DICOM objects.

    Parameters
    ----------
    data: dict[str, Any]
        Input data packed into a dict, including at least:
        - slide_id: str
            Slide ID for the case.
        - graphic_data: list[np.ndarray]
            List of graphic data as numpy arrays in the format required for
            the MicroscopyBulkSimpleAnnotations object. These are correctly
            formatted for the requested graphic type and annotation
            coordinate type.
        - source_image: pydicom.Dataset
            Base level source image for this case.
        In case of ROI annotations, also including: 
        - identifiers: list[str]
            Identifier for each ROI. 
        In case of cell annotations, also including: 
        - cell_identifiers: list[int]
            Identifier for each of the bounding boxes. The identifier is a consecutive number 
            going over the whole dataset (not only a single slide).
        - roi_identifiers: list[int]
            Identifier for each of the bounding boxes. The identifier indicates the ROI that this 
            bounding box is contained in, i.e. in which ROI the cell annotation can be found. 
        - labels: list[str]
            Label for each bounding box. 
    series_uid: hd.UID
        DICOM SeriesInstanceUID. All annotation steps, plus consensus and ROIs go into the same Series. 
    sop_instance_number: 
        Number of the SOPInstance within the DICOM Series.
    graphic_type: str
        Graphic type to use to store all nuclei. Allowed options are 'RECTANGLE' (default)
        or 'POINT'.
    annotation_coordinate_type: str
        Store coordinates in the Bulk Microscopy Bulk Simple Annotations in
        the (3D) frame of reference (SCOORD3D), or the (2D) total pixel
        matrix (SCOORD, default).
    output_dir: pathlib.Path
        A local output directory to store error logs.

    Returns
    -------
    data: dict[str, Any]
        Output data packed into a dict. This will contain the same keys as
        the input dictionary, plus the following additional keys:

        - ann_dcm: hd.ann.MicroscopyBulkSimpleAnnotations:
            DICOM bulk microscopy annotation encoding the original
            annotations in vector format.

    """

    errors = []
    slide_id = data['slide_id']
    start_time = time()
    logging.info(f'Creating annotation for slide: {slide_id}')

    try:
        if data['ann_type'] == 'roi':
            ann_dcm = create_bulk_annotations_for_rois(
                source_image_metadata=data['source_image'],
                graphic_data=data['graphic_data'],
                identifiers=data['identifiers'],
                series_uid=series_uid,
                sop_instance_number=sop_instance_number, 
                graphic_type=graphic_type,
                annotation_coordinate_type=annotation_coordinate_type
            )
        else:  
            ann_dcm = create_bulk_annotations_for_cells(
                source_image_metadata=data['source_image'],
                graphic_data=data['graphic_data'],
                cell_identifiers=data['cell_identifiers'],
                roi_identifiers=data['roi_identifiers'],
                labels=data['labels'],
                series_uid=series_uid, 
                sop_instance_number=sop_instance_number,
                graphic_type=graphic_type,
                annotation_coordinate_type=annotation_coordinate_type
            )
    except Exception as e:
        logging.error(f"Error {str(e)}")
        errors.append(
            {
                'slide_id': slide_id,
                'error_message': str(e),
                'datetime': str(datetime.datetime.now()),
            }
        )
        errors_df = pd.DataFrame(errors)
        errors_df.to_csv(output_dir / 'annotation_creator_error_log.txt')
        return None

    stop_time = time()
    duration = stop_time - start_time
    logging.info(
        f'Created annotation for for slide {slide_id} in {duration:.2f}s'
    )

    data['ann_dcm'] = ann_dcm
    if data['ann_type'] == 'roi': 
        del data['identifiers']
    else: 
        del data['graphic_data'] # Save some memory
        del data['cell_identifiers'] # Save some memory
        del data['roi_identifiers'] # Save some memory
        del data['labels'] # Save some memory
    
    return data


def save_annotations(
    data: dict[str, Any],
    output_dir: Path, 
    ann_step: Union[int, str] = None
    ) -> None: 

    """
    Store files.

    Parameters
    ----------
    data: dict[str, Any]
        Input data packed into a dictionary, containing at least:

        - slide_id: str
            Slide ID for the case.
        - ann_dcm: highdicom.ann.MicroscopyBulkSimpleAnnotations
            Bulk Annotation DICOM object.

    output_dir: pathlib.Path
        A local output directory to store the downloaded files and error logs. 
    ann_step: Union[int, str, None]
        Annotation step in case of cell annotations. 
    """
    errors = []
    slide_id = data['slide_id']
    
    image_start_time = time()
    logging.info(f'Saving annotations for slide {slide_id}')
    
    slide_ann_dir = output_dir / slide_id
    slide_ann_dir.mkdir(exist_ok=True)

    try:
        if data['ann_type'] == 'roi': 
            ann_path = f'{slide_ann_dir}/{slide_id}_rois.dcm'
        else: 
            # Increase ann_step to be 1-indexed instead of 0-indexed in the output files 
            if isinstance(ann_step, int): 
                ann_step += 1
            ann_path = f'{slide_ann_dir}/{slide_id}_cells_ann_step_{ann_step}.dcm'
        
        logging.info(f'Writing annotation to {str(ann_path)}.')
        data['ann_dcm'].save_as(ann_path)

        image_stop_time = time()
        time_for_image = image_stop_time - image_start_time
        logging.info(
            f'Saved annotations for slide {slide_id} in {time_for_image:.2f}s'
        )
        
    except Exception as e:
        logging.error(f"Error {str(e)}")
        errors.append(
            {
                'slide_id': slide_id,
                'error_message': str(e),
                'datetime': str(datetime.datetime.now()),
            }
        )
        errors_df = pd.DataFrame(errors)
        errors_df.to_csv(output_dir / 'save_error_log.txt')
        return None


def run(
    csv_cells: Path, 
    csv_rois: Path, 
    source_image_root_dir: Path,
    output_dir: Path,
    graphic_type: str = 'RECTANGLE',
    annotation_coordinate_type: str = 'SCOORD',
) -> None: 
    
    logging.basicConfig(level=logging.INFO)

    # Suppress highdicom logging (very talkative)
    logging.getLogger('highdicom.base').setLevel(logging.WARNING)
    logging.getLogger('highdicom.seg.sop').setLevel(logging.WARNING)
    
    if output_dir is not None:
        output_dir.mkdir(exist_ok=True)
    
    cells, rois = preprocess_annotation_csvs(csv_cells, csv_rois)

    for slide_id in os.listdir(source_image_root_dir):
        ann_series_uid = hd.UID() # create unique identifier for the DICOM Series holding all annotation objects created here 
        image_data = get_source_image_metadata(source_image_root_dir/slide_id)

        # Create DICOM objects for ROI annotations 
        slide_rois = filter_slide_annotations(rois, slide_id)
        if len(slide_rois) > 0: 
            data = parse_roi_annotations(image_data, slide_rois)
            data = parse_annotations_to_graphic_data(data, graphic_type, annotation_coordinate_type, output_dir)
            data = create_dcm_annotations(data=data, 
                                          series_uid=ann_series_uid, 
                                          sop_instance_number=1, 
                                          graphic_type=graphic_type, 
                                          annotation_coordinate_type=annotation_coordinate_type, 
                                          output_dir=output_dir)  
            save_annotations(data, output_dir)

        # Create DICOM objects for cell annotations
        slide_cells = filter_slide_annotations(cells, slide_id)
        if len(slide_cells) > 0: 
            # Loop over all the different steps / consensus 
            slide_cells['ann_steps'] = slide_cells['all_original_annotations'].apply(lambda x: len(x.split(',')))
            ann_steps = list(range(slide_cells['ann_steps'].max()))
            for ann_step in ann_steps: 
                slide_cells_this_ann_step = slide_cells[slide_cells['ann_steps'] > ann_step] 
                data = parse_cell_annotations(image_data, slide_cells_this_ann_step, ann_step)
                data = parse_annotations_to_graphic_data(data, graphic_type, annotation_coordinate_type, output_dir)
                data = create_dcm_annotations(data=data, 
                                              series_uid=ann_series_uid, 
                                              sop_instance_number=ann_step+1, 
                                              graphic_type=graphic_type, 
                                              annotation_coordinate_type=annotation_coordinate_type, 
                                              output_dir=output_dir)  
                save_annotations(data, output_dir, ann_step)

            # Also encode the final consensus 
            data = parse_cell_annotations(image_data, slide_cells, ann_step='consensus')
            data = parse_annotations_to_graphic_data(data, graphic_type, annotation_coordinate_type, output_dir)
            data = create_dcm_annotations(data=data, 
                                          series_uid=ann_series_uid, 
                                          sop_instance_number=ann_steps[-1]+1, 
                                          graphic_type=graphic_type, 
                                          annotation_coordinate_type=annotation_coordinate_type, 
                                          output_dir=output_dir)
            save_annotations(data, output_dir, ann_step='consensus')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run BMDeep dataset conversion from MRXS to DICOM on a local machine, but retrieving dataset from mounted server.') 
    parser.add_argument('image_data_dir', type=Path, help='Path to folder with converted DICOM image files. Each slide is supposed to be in a separate folder named after the slide ID.')
    parser.add_argument('cell_csv', type=Path, help='Path to CSV file holding cell annotation information.')
    parser.add_argument('roi_csv', type=Path, help='Path to CSV file holding ROI annotation information.')
    args = parser.parse_args()

    run(args.cell_csv, args.roi_csv, source_image_root_dir=args.image_data_dir, output_dir=args.image_data_dir)

