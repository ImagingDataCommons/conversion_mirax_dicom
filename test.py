from wsidicom import WsiDicom 
import openslide
import argparse 
from pathlib import Path

if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Run BMDeep dataset conversion from MRXS to DICOM on a local machine, but retrieving dataset from mounted server.') 
    parser.add_argument('mrxs_file', type=Path, help='Path to original mrxs file before conversion.')
    parser.add_argument('dcm_file', type=Path, help='Path to one dcm file of the DICOM Series after conversion from mrxs file.')
    args = parser.parse_args()

    print('MRXS slide opened with Openslide:')
    mrxs_slide = openslide.OpenSlide(args.mrxs_file)
    print('Level count:', mrxs_slide.level_count)
    print('Level dimensions:', mrxs_slide.level_dimensions)
    tile_mrxs = mrxs_slide.read_region(location=(80000, 190000), level=0, size=(512,512))
    tile_mrxs.save(args.dcm_file.parents[1].joinpath('tile_mrxs_openslide.png'))
    thumbnail_mrxs = mrxs_slide.get_thumbnail(size=(300,300))
    thumbnail_mrxs.save(args.dcm_file.parents[1].joinpath('thumbnail_mrxs_openslide.png'))

    print('DCM slide opened with Openslide:')
    dcm_slide = openslide.OpenSlide(args.dcm_file)
    
    print('Level count:', dcm_slide.level_count)
    print('Level dimensions:', dcm_slide.level_dimensions)
    tile = dcm_slide.read_region(location=(80000, 190000), level=0, size=(512,512))
    tile.save(args.dcm_file.parents[1].joinpath('tile_dcm_openslide.png'))
    try: 
        thumbnail = dcm_slide.get_thumbnail(size=(300,300))
        thumbnail.save(args.dcm_file.parents[1].joinpath('thumbnail_dcm_openslide.png'))
    except Exception as e: 
        print('Generating thumbnail with openslide failed:', e)

    print('DCM slide opened with wsidicom:')
    wsi_dcm = WsiDicom.open(args.dcm_file.parent)
    #print(pydicom.Dataset(wsi_dcm.levels[0].datasets[0])) # level metadata
    print(wsi_dcm.levels)
    tile = wsi_dcm.read_region(location=(80000, 190000), level=0, size=(512,512))
    tile.save(args.dcm_file.parents[1].joinpath('tile_dcm_wsidicom.png'))
    thumbnail = wsi_dcm.read_thumbnail()
    thumbnail.save(args.dcm_file.parents[1].joinpath('thumbnail_dcm_wsidicom.png'))
    