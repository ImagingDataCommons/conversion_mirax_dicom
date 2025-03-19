import pandas as pd
from pathlib import Path 
from dataclasses import dataclass
from typing import Dict, List


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


def _rename_cell_labels(cells: pd.DataFrame) -> pd.DataFrame: 
    
    def _replace_in_list(list_str: str, replacements: Dict[str, str]) -> str: 
        lst = list_str.split(',')
        return ','.join([replacements.get(item, item) for item in lst])
    
    replacements = {'lymphoblast': 'lymphoid_precursor_cell', 
                    'monoblast': 'immature_monoblast', 
                    'myeloblast': 'myeloid_precursor_cell'}
    
    cells['all_original_annotations'] = cells['all_original_annotations'].apply(lambda x: _replace_in_list(x, replacements))
    cells['original_consensus_label'].replace(replacements, inplace=True)
    return cells
 

def preprocess_annotation_csvs(cells_csv: Path, roi_csv: Path) -> pd.DataFrame: 
    """ 
    Function to massage the annotation data to fit the required format for the conversion process.
    Also includes re-naming of a few cell labels to better match our assigned ontology codes. 
    """

    cells = pd.read_csv(cells_csv)
    cells = _rename_cell_labels(cells)
    rois = pd.read_csv(roi_csv)
    return pd.merge(cells, rois[['id', 'slide_id']], 
                    left_on='rocellboxing_id', 
                    right_on = 'id', 
                    how='left').drop('id', axis=1), rois 


def filter_slide_annotations(annotations: pd.DataFrame, slide_id: str) -> List[CellAnnotation]: 
    return annotations[annotations['slide_id'] == slide_id] 
