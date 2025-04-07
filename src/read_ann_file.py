import argparse
import highdicom as hd
from pathlib import Path

def test(data_dir: Path): 
    for ann_file in sorted(data_dir.rglob('*_ann_*.dcm')): 
        print(ann_file)
        ann = hd.ann.annread(ann_file)
        ann_groups = ann.get_annotation_groups()
        print('Number of annotation groups', len(ann_groups))
        try: 
            group = ann.get_annotation_group(uid='1.2.826.0.1.3680043.10.511.3.13075055992462833457323203609626225')
            graphic_data = group.get_graphic_data(coordinate_type=ann.annotation_coordinate_type)
            print('Graphic data', graphic_data, len(graphic_data))
            names, values, units = group.get_measurements()
            print(names)
            print(values)
            print(units)
        except: 
            continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run BMDeep dataset conversion from MRXS to DICOM on a local machine, but retrieving dataset from mounted server.') 
    parser.add_argument('ann', type=Path, help='Path to ann files.')
    args = parser.parse_args()

    test(args.ann)
