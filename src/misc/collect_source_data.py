import os
import argparse
from pathlib import Path
from typing import List
import shutil


def copy_path(local_path: Path, dest_path: Path, errors: List) -> None:
    '''
    Copy a file or folder to the destination path.
    '''
    try:
        if local_path.is_file():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(local_path, dest_path)
        elif local_path.is_dir():
            if dest_path.resolve() == local_path.resolve():
                errors.append(f"Refusing to delete/copy: source and destination are the same: {local_path}")
                print(f"Refusing to delete/copy: source and destination are the same: {local_path}")
                return
            if dest_path.exists():
                shutil.rmtree(dest_path)
            shutil.copytree(local_path, dest_path)
        else:
            print(f'Source path is neither file nor directory: {local_path}')
            #raise ValueError(f'Source path is neither file nor directory: {local_path}')
    
    
    except Exception as e:
        print(f'Copy error for {local_path}: {str(e)}')
        errors.append(f'Copy error for {local_path}: {str(e)}')


def run(source_dir: Path, output_dir: Path, error_log: Path) -> None:
    errors = []
    slide_ids = [item for item in os.listdir(source_dir) if 
                (os.path.isdir(source_dir/item) and item.endswith('_bm'))]
    for slide_id in slide_ids:
        try:
            mrxs_file = next(source_dir.parent.rglob(f'{slide_id}.mrxs'))
        except StopIteration:
            errors.append(f"No .mrxs file found for slide_id: {slide_id} (expected: {slide_id}.mrxs)")
            continue
        print(f'Copying {mrxs_file} and its folder to output directory...')
        dest_file = output_dir / mrxs_file.name
        dest_folder = output_dir / mrxs_file.with_suffix('')
        copy_path(mrxs_file, dest_file, errors)
        copy_path(mrxs_file.with_suffix(''), dest_folder, errors)
    if errors:
        with open(error_log, 'w') as ef:
            for err in errors:
                ef.write(err + '\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Copy source data to output directory.')
    parser.add_argument('source_dir', type=Path, help='Path to root dir that contains DICOM converted images.')
    parser.add_argument('output_dir', type=Path, help='Path to output directory for copied data.')
    parser.add_argument('error_log', type=Path, help='Path to TXT file for error logging.')
    args = parser.parse_args()

    run(args.source_dir, args.output_dir, args.error_log)