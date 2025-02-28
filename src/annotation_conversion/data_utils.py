import pandas as pd
from pathlib import Path 
from dataclasses import dataclass
from typing import List


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


def preprocess_annotation_csvs(cells_csv: Path, roi_csv: Path) -> pd.DataFrame: 
    """ 
    Function to massage the annotation data to fit the required format for the conversion process.
    """

    cells = pd.read_csv(cells_csv)
    rois = pd.read_csv(roi_csv)
    return pd.merge(cells, rois[['id', 'slide_id']], 
                    left_on='rocellboxing_id', 
                    right_on = 'id', 
                    how='left').drop('id', axis=1), rois 


def filter_slide_annotations(annotations: pd.DataFrame, slide_id: str) -> List[CellAnnotation]: 
    return annotations[annotations['slide_id'] == slide_id] 
