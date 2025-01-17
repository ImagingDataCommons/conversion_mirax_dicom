from multiprocessing import Process
import os
import datetime
import argparse 
import shutil
from pathlib import Path
from wsidicomizer import WsiDicomizer
from typing import List


def copy_mrxs_from_gaia(gaia_mrxs_path: Path, local_mrxs_path: Path) -> None:
    shutil.copy(gaia_mrxs_path, local_mrxs_path)
    shutil.copytree(gaia_mrxs_path.with_suffix(''), local_mrxs_path.with_suffix(''), dirs_exist_ok=True) # copy corresponding folder with .dat and .ini files 


def run_conversion(input_file: Path, output_folder: Path) -> None: 
    _ = WsiDicomizer.convert(
        filepath=input_file,
        output_path=output_folder,
        metadata=None,
        workers=4, 
        include_label=False, 
        tile_size=240, 
        levels=[0,2,4,6]
    )


def copy_dcm_to_gaia(local_dir: Path, gaia_dir: Path) -> None: 
    for file in local_dir.iterdir(): 
        shutil.copy(file, gaia_dir.joinpath(local_dir.name))    
    #shutil.copytree(local_dir, gaia_dir.joinpath(local_dir.name), dirs_exist_ok=True)


def clean_up(files_or_dirs: List[Path]) -> None: 
    for path in files_or_dirs: 
        if os.path.exists(path):
            if os.path.isdir(path): 
                shutil.rmtree(path) 
            else: 
                os.remove(path)


if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Run BMDeep dataset conversion from MRXS to DICOM on a local machine, but retrieving dataset from mounted server.') 
    parser.add_argument('gaia_work_dir', type=Path, help='Path to directory on Gaia which should be searched for MRXS files and where resulting DICOM files can be stored.')
    parser.add_argument('local_work_dir', type=Path, help='Path to local directory where intermediate results can be stored.')
    parser.add_argument('--metadata', type=Path, help='Path to metadata CSV file.')
    args = parser.parse_args()

    # Configuration
    local_input = args.local_work_dir.joinpath('be_converted')
    local_output = args.local_work_dir.joinpath('is_converted')
    log_file = args.local_work_dir.joinpath('log.txt')
    gaia_results_dir = args.gaia_work_dir.joinpath('bmdeep_DICOM_converted') 
    for dir in [local_input, local_output, gaia_results_dir]: 
        dir.mkdir(parents=True, exist_ok=True)
    
    # Conversion workflow
    for gaia_mrxs_file in args.gaia_work_dir.rglob('*_bm.mrxs'): 
        
        # Check if already converted
        if os.path.exists(gaia_results_dir.joinpath(gaia_mrxs_file.name).with_suffix('')):
            continue

        local_mrxs_file = local_input.joinpath(gaia_mrxs_file.name)
        try: 
            copy_mrxs_from_gaia(gaia_mrxs_file, local_mrxs_file)
        except Exception as e: 
            now = datetime.datetime.now()
            with open(log_file, 'a') as log: 
                log.write(f'{now.strftime("%Y-%m-%d %H:%M:%S")} - Copy error while working on {gaia_mrxs_file} >>> {e}\n')
            # Clean-up  
            clean_up([local_mrxs_file, local_mrxs_file.with_suffix('')])
            continue 
        
        converted_dicom_dir = local_output.joinpath(local_mrxs_file.stem)
        try: 
          # Run in separate process to ensure release of RAM afterwards
          p = Process(target=run_conversion, args=(local_mrxs_file, converted_dicom_dir))
          p.start()
          p.join()
        except Exception as e: 
            now = datetime.datetime.now()
            with open(log_file, 'a') as log: 
                log.write(f'{now.strftime("%Y-%m-%d %H:%M:%S")} - Conversion error while working on {local_mrxs_file} >>> {e}\n')
            # Clean-up 
            clean_up([local_mrxs_file, local_mrxs_file.with_suffix(''), converted_dicom_dir])
            continue 
        
        try: 
            copy_dcm_to_gaia(converted_dicom_dir, gaia_results_dir)
        except Exception as e: 
            now = datetime.datetime.now()
            with open(log_file, 'a') as log: 
                log.write(f'{now.strftime("%Y-%m-%d %H:%M:%S")} - Copy error while working on {converted_dicom_dir} >>> {e}\n')
            # Clean-up 
            clean_up([local_mrxs_file, local_mrxs_file.with_suffix(''), converted_dicom_dir])
            continue

        clean_up([local_mrxs_file, local_mrxs_file.with_suffix(''), converted_dicom_dir])
        with open(log_file, 'a') as log: 
            log.write(f'{now.strftime("%Y-%m-%d %H:%M:%S")} - Successfully converted {gaia_mrxs_file}\n')
