import argparse
import pydicom 
from pathlib import Path

if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Run BMDeep dataset conversion from MRXS to DICOM on a local machine, but retrieving dataset from mounted server.') 
    parser.add_argument('dcm_file', type=Path, help='Path to one dcm file of the DICOM Series after conversion from mrxs file.')
    args = parser.parse_args()

    ds = pydicom.dcmread(args.dcm_file)
    if ds.ImageType[0] == 'ORIGINAL' and ds.ImageType[3] == 'RESAMPLED':
        print(ds.ImageType)
        ds.ImageType[0] = 'DERIVED'
        print(ds.ImageType)
        ds.save_as(args.dcm_file)
        
