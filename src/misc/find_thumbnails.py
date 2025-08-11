import os
import argparse
import shutil
import pydicom
from pathlib import Path


def find_and_move_thumbnails(source_dir, thumbnail_dir):
    if not os.path.exists(thumbnail_dir):
        os.makedirs(thumbnail_dir)
    # Walk through the source directory and find DICOM files
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.dcm'):
                filepath = os.path.join(root, file)
                ds = pydicom.dcmread(filepath)
                try: 
                    image_type = ds.ImageType 
                    if image_type[2] == 'THUMBNAIL':
                        shutil.move(filepath, os.path.join(thumbnail_dir, file))
                except: 
                    continue 

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Search folders of DICOM series and find and move THUMBNAIL images.') 
    parser.add_argument('source_dir', type=Path, help='Path to root dir that should be searched.')
    parser.add_argument('thumbnail_dir', type=Path, help='Path to directory where THUMBNAILS should be moved to.')
    args = parser.parse_args()

    find_and_move_thumbnails(args.source_dir, args.thumbnail_dir)
