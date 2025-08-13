import os 
import argparse
import subprocess
from pathlib import Path
from typing import List


def upload_to_gcs(local_path: Path, bucket_path: str, errors: List) -> None: 
    '''
    Upload a file or folder to Google Cloud Storage using gcloud storage cp.
    
    Parameters:
    - local_path: str, path to local file or folder to upload
    - bucket_path: str, destination GCS path, e.g. gs://your-bucket-name/folder/
    '''
    if os.path.isdir(local_path): 
        cmd = [
                "gcloud", "storage", "cp", "--recursive",
                local_path,
                bucket_path
            ]
    else:
        cmd = [
                "gcloud", "storage", "cp",
                local_path,
                bucket_path
            ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Upload error for {local_path}: {e.stderr.strip()}')
        errors.append(f'Upload error for {local_path}: {e.stderr.strip()}')


def run(source_dir: Path, bucket_name: str, error_log: Path) -> None:
    errors = []
    slide_ids = [item for item in os.listdir(source_dir) if 
                (os.path.isdir(source_dir/item) and item.endswith('_bm'))]
    for slide_id in slide_ids:
        try:
            mrxs_file = next(source_dir.parent.rglob(f'{slide_id}.mrxs'))
        except StopIteration:
            errors.append(f"No .mrxs file found for slide_id: {slide_id} (expected: {slide_id}.mrxs)")
            continue
        print(f'Uploading {mrxs_file} and its folder to {bucket_name}...')
        upload_to_gcs(mrxs_file, f'gs://{bucket_name}', errors)
        upload_to_gcs(mrxs_file.with_suffix(''), f'gs://{bucket_name}', errors)
    if errors:
        with open(error_log, 'w') as ef:
            for err in errors:
                ef.write(err + '\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create upload manifest for .') 
    parser.add_argument('source_dir', type=Path, help='Path to root dir that contains DICOM converted images.')
    parser.add_argument('bucket_name', type=str, help='Name of gcs bucket to upload to, e.g. gs://.')
    parser.add_argument('error_log', type=Path, help='Path to TXT file for error logging.')
    args = parser.parse_args()

    run(args.source_dir, args.bucket_name, args.error_log)