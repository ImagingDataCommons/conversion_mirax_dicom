import json 
import argparse
import numpy as np 
import highdicom as hd
from typing import List

def get_annotations(ann: hd.ann.sop.MicroscopyBulkSimpleAnnotations) -> List[np.ndarray]:
    all_annotations = []
    for annotation_group in ann.get_annotation_groups():
        annotations_group = annotation_group.get_graphic_data(coordinate_type='2D')
        print('ann', annotations_group)
        all_annotations.extend(annotations_group)
    print('all', all_annotations)
    return all_annotations

def annotation_to_geojson_format(ann: np.ndarray) -> List[float]:
    ann = np.concatenate((ann, [ann[0]])) # add first coordinate to the end
    ann_3d = ann.reshape(1, *ann.shape) # return with extra dimension for GeoJSON compliance
    return ann_3d.tolist()

def ann_to_geojson(ann_path: str):
    geojson = {'type':'FeatureCollection', 'features':[]}

    ann_obj = hd.ann.annread(ann_path)
    annotations = get_annotations(ann_obj)
    annotations_ = [annotation_to_geojson_format(ann) for ann in annotations]

    feature = {'type':'Feature',
               'properties': {},
               'geometry':{'type': None,
                           'coordinates':[]}}
    feature['properties'] = {'name': 'Cell or ROI'}
    feature['geometry']['type'] = 'MultiPolygon'
    feature['geometry']['coordinates'] = annotations_
    geojson['features'].append(feature)

    return geojson

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert DICOM ANN annotations to GeoJSON format.')
    parser.add_argument('input', type=str, help='Path to input DICOM ANN file.')
    parser.add_argument('output', type=str, help='Path to output GeoJSON file.')
    args = parser.parse_args()

    geojson = ann_to_geojson(args.input)
    with open(args.output, 'w') as f:
        json.dump(geojson, f)