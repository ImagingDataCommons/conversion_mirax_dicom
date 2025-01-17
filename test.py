from wsidicom import WsiDicom 
import openslide
import pydicom 
import argparse 
from pathlib import Path


if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Run BMDeep dataset conversion from MRXS to DICOM on a local machine, but retrieving dataset from mounted server.') 
    parser.add_argument('mrxs_file', type=Path, help='Path to original mrxs file before conversion.')
    parser.add_argument('dcm_file', type=Path, help='Path to any dcm file (any level) of converted mrxs file.')
    args = parser.parse_args()

    mrxs_slide = openslide.OpenSlide(args.mrxs_file)
    
    dcm_slide = WsiDicom.open(args.dcm_file)
    print(dcm_slide.metadata)
    for level in dcm_slide.levels: 
        print(pydicom.Dataset(level.datasets[0])) # level metadata