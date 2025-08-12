import os 
import argparse
from pathlib import Path

def run(source_dir: Path) -> None:
    manifest_file = source_dir.joinpath('source_data_upload_manifest.txt')
    slide_ids = [item for item in os.listdir(source_dir) if 
                (os.path.isdir(source_dir/item) and item.endswith('_bm'))]
    for slide_id in slide_ids:
        mrxs_file = next(source_dir.parent.rglob(f'{slide_id}.mrxs'))

    #with open(manifest_file, 'w') as f:      
         
            #f.write(f"{file.relative_to(source_dir)}\n")
    #print(f"Upload manifest created at {manifest_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create upload manifest for .') 
    parser.add_argument('source_dir', type=Path, help='Path to root dir that contains DICOM converted images.')
    args = parser.parse_args()

    run(args.source_dir)