import argparse
import pandas as pd
import highdicom as hd
from pathlib import Path


def get_rois(ann_groups) -> pd.DataFrame:
    rois = pd.DataFrame(columns=['roi_id', 'roi_label', 'roi_coordinates'])
    for ann_group in ann_groups:
        coords = ann_group.get_graphic_data(coordinate_type='2D')
        m_names, m_values, m_units = ann_group.get_measurements()
        for c, m in zip(coords, m_values):
            rois.loc[len(rois)] = [m[0], ann_group.label, c]
    return rois


def get_cells(ann_groups) -> pd.DataFrame:
    cells = pd.DataFrame(columns=['cell_id', 'roi_id', 'cell_label', 'cell_coordinates'])
    for ann_group in ann_groups:
        coords = ann_group.get_graphic_data(coordinate_type='2D')
        m_names, m_values, m_units = ann_group.get_measurements()
        try: 
            for c, m in zip(coords, m_values):
                cells.loc[len(cells)] = [m[0], m[1], ann_group.label, c]
        except: 
            for c, m in zip(coords, m_values):
                cells.loc[len(cells)] = [m[0], -1, ann_group.label, c]
    return cells


def quick_overview(data_dir: Path): 
    for ann_file in data_dir.rglob('*_roi*.dcm'): 
        print(ann_file)
        ann = hd.ann.annread(ann_file)
        ann_groups = ann.get_annotation_groups()
        print('Number of annotation groups', len(ann_groups))
        rois = get_rois(ann_groups)
        print(rois)

    for ann_file in sorted(data_dir.rglob('*_ann_*.dcm')): 
        print(ann_file)
        ann = hd.ann.annread(ann_file)
        ann_groups = ann.get_annotation_groups()
        print('Number of annotation groups', len(ann_groups))
        cells = get_cells(ann_groups)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='blablabla') 
    parser.add_argument('ann', type=Path, help='Path to ann files.')
    args = parser.parse_args()

    quick_overview(args.ann)
