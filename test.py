from wsidicom import WsiDicom 
import openslide
import pydicom 
import argparse 
from pathlib import Path
import numpy as np 


if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Run BMDeep dataset conversion from MRXS to DICOM on a local machine, but retrieving dataset from mounted server.') 
    parser.add_argument('mrxs_file', type=Path, help='Path to original mrxs file before conversion.')
    parser.add_argument('dcm_folder', type=Path, help='Path to dcm folder of DICOM Series after conversion from mrxs file.')
    args = parser.parse_args()

    mrxs_slide = openslide.OpenSlide(args.mrxs_file)
    print('MRXS slide opened with Openslide:')
    print(mrxs_slide.level_count)
    print(mrxs_slide.level_dimensions)
    tile_mrxs = mrxs_slide.read_region(location=(0, 0), level=0, size=(512,512))
    tile_mrxs.save(args.dcm_folder.joinpath('tile_mrxs.png'))
    thumbnail_mrxs = mrxs_slide.get_thumbnail(size=(300,300))
    thumbnail_mrxs.save(args.dcm_folder.joinpath('thumbnail_mrxs.png'))

    dcm_slide = openslide.OpenSlide(args.dcm_folder.joinpath('1.2.826.0.1.3680043.8.498.16190737556081117099974819785314706847.dcm'))
    print('DCM slide opened with Openslide:')
    print(dcm_slide.level_count)
    print(dcm_slide.level_dimensions)
    tile = dcm_slide.read_region(location=(0, 0), level=0, size=(512,512))
    tile.save(args.dcm_folder.joinpath('tile.png'))
    thumbnail = dcm_slide.get_thumbnail(size=(300,300))
    thumbnail.save(args.dcm_folder.joinpath('thumbnail.png'))

    #print('DCM slide opened with wsidicom:')
    #pydcm_file = pydicom.dcmread(args.dcm_folder.joinpath('1.2.826.0.1.3680043.8.498.20871125252501301118948072333207029079.dcm'))
    #print(pydcm_file)
    #dcm_slide = WsiDicom.open(args.dcm_folder)
    #print(dcm_slide.levels)

    #print(dcm_slide.levels[0].image_origin.origin) # not working
    #print(pydicom.Dataset(dcm_slide.levels[0].datasets[0])) # level metadata
    #print('reading some region')
    #tile = dcm_slide.read_region(location=(15000,15000), level=0, size=(1000,1000))
    #tile.save(args.dcm_folder.joinpath('tile.png'))
    #thumbnail = dcm_slide.read_thumbnail()
    #thumbnail.save(args.dcm_folder.joinpath('thumbnail.png'))
    