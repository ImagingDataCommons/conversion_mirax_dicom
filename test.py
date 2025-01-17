from wsidicom import WsiDicom 
import openslide
import pydicom 
import argparse 
from pathlib import Path


if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Run BMDeep dataset conversion from MRXS to DICOM on a local machine, but retrieving dataset from mounted server.') 
    parser.add_argument('mrxs_file', type=Path, help='Path to original mrxs file before conversion.')
    parser.add_argument('dcm_folder', type=Path, help='Path to dcm folder of DICOM Series after conversion from mrxs file.')
    args = parser.parse_args()

    mrxs_slide = openslide.OpenSlide(args.mrxs_file)
    print('MRXS slide')
    print(mrxs_slide.level_count)
    print(mrxs_slide.level_dimensions)

    dcm_slide = WsiDicom.open(args.dcm_folder)
    print(dcm_slide.levels)
    print(dcm_slide.levels[0].image_origin.origin)
    print(pydicom.Dataset(dcm_slide.levels[0].datasets[0])) # level metadata