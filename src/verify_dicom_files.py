import os 
import argparse 
import logging
import subprocess
from pathlib import Path
from datetime import datetime


def run_dciodvfy(dicom3tools: Path, slide_dir: Path, log: Path): 
    for dcm_file in os.listdir(slide_dir): 
        print(slide_dir/dcm_file)
        result = subprocess.run([f'{dicom3tools}/dciodvfy', f'{slide_dir/dcm_file}'], capture_output=True, text=True)
        print(result.stdout)


def run_dcentvfy(dicom3tools: Path, slide_dir: str, log: Path): 
    pass 


def run(dicom3tools: Path, data_dir: Path): 
    log_file = data_dir / 'dicom3tools_verification_log.txt'
    
    slide_ids = [item for item in os.listdir(data_dir) if os.path.isdir(data_dir/item)]
    for slide_id in slide_ids: 
        run_dciodvfy(dicom3tools, data_dir/slide_id, log_file) 
        run_dcentvfy(dicom3tools, data_dir/slide_id, log_file)

    
    with open(log_file, 'a') as log: 
        log.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Successfully converted {gaia_mrxs_file}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run verification of BMDeep converted dataset.') 
    parser.add_argument('image_data_dir', type=Path, help='Path to folder with converted DICOM image files. Each slide is supposed to be in a separate folder named after the slide ID.')
    parser.add_argument('dicom3tools', type=Path, help='Path to dicom3tools bin containing all different subtools.')
    args = parser.parse_args()

    run(args.dicom3tools, args.image_data_dir)