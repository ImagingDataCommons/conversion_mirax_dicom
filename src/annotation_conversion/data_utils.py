import pandas as pd
from pathlib import Path 
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union 


@dataclass
class CellAnnotation:
    cell_identifier: int
    roi_identifier: int 
    bounding_box: Tuple[int] # xmin, ymin, xmax, ymax 
    label: str

@dataclass
class ROIAnnotation: 
    identifier: int
    bounding_box: Tuple[int] # xmin, ymin, xmax, ymax


def preprocess_annotation_csvs(cell_csvs: List[Path], roi_csvs: List[Path]) -> Tuple[pd.DataFrame]: 
    """ 
    Function to massage the annotation data to fit the required format for the conversion process.
    Also includes re-naming of a few cell labels to better match our assigned ontology codes. 
    """
    cells_dfs = []
    for c in cell_csvs: 
        df_c = pd.read_csv(c)
        # If no original_consensus_label column is present, we are dealing with the detection dataset and all cells get the label 'haematological_structure'
        if not 'original_consensus_label' in df_c.columns:
            df_c['all_original_annotations'] = '' 
            df_c['original_consensus_label'] = 'haematological_structure'       
        cells_dfs.append(df_c)
    
    cells = pd.concat(cells_dfs, axis=0, ignore_index=True)
    cells = _rename_cell_labels(cells)
    cells = _add_number_of_annotation_steps(cells)
    rois = pd.concat([pd.read_csv(r) for r in roi_csvs], axis=0, ignore_index=True)
    return cells, rois 


def _rename_cell_labels(cells: pd.DataFrame) -> pd.DataFrame: 
    
    def _replace_in_list(list_str: str, replacements: Dict[str, str]) -> str: 
        lst = list_str.split(',')
        return ','.join([replacements.get(item, item) for item in lst])
    
    replacements = {
        'lymphoblast': 'lymphoid_precursor_cell', 
        'monoblast': 'immature_monoblast', 
        'myeloblast': 'myeloid_precursor_cell'}
    
    replacements_german_labels = {
        'other:basophiler Erythroblast': 'basophilic_erythroblast', 
        'other:Dichter Zellhaufen': 'technically_unfit', 
        'other:Zellhaufen': 'technically_unfit',
        'other:degranulierter Promyelozyt': 'degranulated_neutrophilic_myelocyte', 
        'other:Hämophagozytose': 'phagocytosis', 
        'other:Riesenthrombozyt': 'giant_platelet', 
        'other:Osteoblast': 'unknown_blast', # loosing information here, accepted because of rare occurence
        'other:osteoblast': 'unknown_blast', # loosing information here, accepted because of rare occurence
        'other:Mikrogerinsel': 'thrombocyte_aggregate', 
        'other:Plasma eines Megakaryozyten': 'damaged_cell', 
        'other:Makrothrombozyt': 'giant_platelet', 
        'other:Kernreste': 'damaged_cell', 
        'annotation_error': 'technically_unfit' 
    }
    
    cells['all_original_annotations'] = cells['all_original_annotations'].apply(lambda x: _replace_in_list(x, replacements_german_labels))
    cells['all_original_annotations'] = cells['all_original_annotations'].apply(lambda x: _replace_in_list(x, replacements))
    cells['original_consensus_label'] = cells['original_consensus_label'].replace(replacements)
    return cells


def _add_number_of_annotation_steps(annotations: pd.DataFrame) -> pd.DataFrame:
    annotations['ann_sessions'] = annotations['all_original_annotations'].apply(lambda x: 0 if x == '' else len(x.split(',')))
    return annotations

def filter_slide_annotations(annotations: pd.DataFrame, slide_id: str) -> List[CellAnnotation]: 
    return annotations[annotations['slide_id'] == slide_id] 


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
        - mrxs_source_image_path: 
            Path to MRXS source image. 

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
        x_min, x_max, y_min, y_max = row['x1'], row['x2'], row['y1'], row['y2']
        ann.append(ROIAnnotation(
            identifier=row['roi_id'], 
            bounding_box=(x_min, y_min, x_max, y_max), 
        ))

    data['ann_type'] = 'roi'
    data['ann'] = ann
    return data


def parse_cell_annotations(data: Dict[str, Any], annotations: pd.DataFrame, ann_session: Union[int, str]) -> Dict[str, Any]: 
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
        - mrxs_source_image_path: 
            Path to MRXS source image. 
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
        x_min, x_max, y_min, y_max = row['x1'], row['x2'], row['y1'], row['y2']

        if ann_session == 'consensus' or 'detection-only': 
            cell_label = row['original_consensus_label']
        else: 
            cell_label = row['all_original_annotations'].split(',')[ann_session]
        ann.append(CellAnnotation(
            cell_identifier=row['cell_id'], 
            roi_identifier=row['roi_id'],
            bounding_box=(x_min, y_min, x_max, y_max), 
            label=cell_label
        ))

    data['ann_type'] = 'cell'
    data['ann'] = ann
    return data