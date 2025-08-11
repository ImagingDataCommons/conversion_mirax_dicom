import os 
import argparse 
import subprocess
from pathlib import Path
from datetime import datetime


def run_dciodvfy(dicom3tools: Path, slide_dir: Path) -> None: 
    dcm_files = [f for f in os.listdir(slide_dir) if f.endswith('.dcm')]
    for dcm_file in dcm_files: 
        result = subprocess.run([f'{dicom3tools}/dciodvfy', f'{slide_dir/dcm_file}'], capture_output=True, text=True)
        # if error/warning: make extra log file 
        with open(f'{slide_dir.parent}/{slide_dir.stem}_dciodcfy_output.txt', 'a') as log: 
            log.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {dcm_file}\n')
            log.write(result.stderr)


def run_dcentvfy(dicom3tools: Path, slide_dir: str): 
    result = subprocess.run([f'{dicom3tools}/dcentvfy', f'{slide_dir}/*'], capture_output=True, text=True, shell=True)
    with open(f'{slide_dir.parent}/{slide_dir.stem}_dcentvfy_output.txt', 'a') as log: 
        if len(result.stderr) > 0: 
            log.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            log.write(result.stderr)
        else: 
            log.write('No errors/warnings occurred.')


def run(dicom3tools: Path, data_dir: Path) -> None:     
    slide_ids = [item for item in os.listdir(data_dir) if 
                (os.path.isdir(data_dir/item) and item.endswith('_bm'))]
    for slide_id in slide_ids: 
        run_dcentvfy(dicom3tools, data_dir/slide_id)
        run_dciodvfy(dicom3tools, data_dir/slide_id) 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run verification of converted dataset.') 
    parser.add_argument('image_data_dir', type=Path, help='Path to folder with converted DICOM image files. Each slide is supposed to be in a separate folder named after the slide ID.')
    parser.add_argument('dicom3tools', type=Path, help='Path to dicom3tools bin containing all different subtools.')
    args = parser.parse_args()

    run(args.dicom3tools, args.image_data_dir)