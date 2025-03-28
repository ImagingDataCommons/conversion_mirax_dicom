import pandas as pd
from pathlib import Path 
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class CellAnnotation:
    cell_identifier: int
    roi_identifier: int 
    bounding_box: tuple # xmin, ymin, xmax, ymax 
    label: str

@dataclass
class ROIAnnotation: 
    identifier: int
    bounding_box: tuple # xmin, ymin, xmax, ymax


def reduce_enlarged_rois(x_min_enlarged: int, y_min_enlarged: int, size: int) -> Tuple[int]:  
    """ The ROIs that we have, have been enlarged by 10% (unidirectionally) from the orginal ones and need
    to be reduced again to their original size. """
    current_size_px, target_half_size_px = 2458, 1024
    x_max_enlarged, y_max_enlarged = x_min_enlarged + current_size_px, y_min_enlarged + current_size_px
    x_center = x_min_enlarged + (x_max_enlarged-x_min_enlarged)//2
    y_center = y_min_enlarged + (y_max_enlarged-y_min_enlarged)//2
    x_min, x_max, y_min, y_max = x_center-target_half_size_px, x_center+target_half_size_px, y_center-target_half_size_px, y_center+target_half_size_px
    return x_min, x_max, y_min, y_max


def _filter_rois_by_size(rois: pd.DataFrame) -> pd.DataFrame: 
    # Consider only ROIs with 2458x2458 pixel size
    return rois.loc[(rois['width'] == 2458) & (rois['height'] == 2458)]


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
        'other:Granula der kaputten Zelle': 'damaged_cell', 
        'other:Kernreste': 'damaged_cell', 
        'annotation_error': 'technically_unfit' 
    }
    
    cells['all_original_annotations'] = cells['all_original_annotations'].apply(lambda x: _replace_in_list(x, replacements_german_labels))
    cells['all_original_annotations'] = cells['all_original_annotations'].apply(lambda x: _replace_in_list(x, replacements))
    cells['original_consensus_label'] = cells['original_consensus_label'].replace(replacements)
    return cells
 

def preprocess_annotation_csvs(cells_csv: Path, roi_csv: Path) -> pd.DataFrame: 
    """ 
    Function to massage the annotation data to fit the required format for the conversion process.
    Also includes re-naming of a few cell labels to better match our assigned ontology codes. 
    """

    cells = pd.read_csv(cells_csv)
    cells = _rename_cell_labels(cells)
    rois = pd.read_csv(roi_csv)
    rois = _filter_rois_by_size(rois)
    return pd.merge(cells, rois[['id', 'slide_id']], 
                    left_on='rocellboxing_id', 
                    right_on = 'id', 
                    how='left').drop('id', axis=1), rois 


def filter_slide_annotations(annotations: pd.DataFrame, slide_id: str) -> List[CellAnnotation]: 
    return annotations[annotations['slide_id'] == slide_id] 
