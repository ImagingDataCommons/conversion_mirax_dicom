from multiprocessing import Process
import os
from datetime import datetime
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
        tile_size=512 # wsidicom seems to not be able to infer tile size from mrxs automatically, so will use this one provided here.
        #include_levels=[0,2,4,6], 
        #offset_table=None
    )


def copy_dcm_to_gaia(local_dir: Path, gaia_dir: Path) -> None: 
    dest_dir = gaia_dir.joinpath(local_dir.name)
    dest_dir.mkdir(parents=True, exist_ok=True)
    for file in list(local_dir.iterdir()): 
        shutil.copyfile(file, dest_dir.joinpath(file.name))    


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
    for gaia_mrxs_file in sorted(args.gaia_work_dir.rglob('*_bm.mrxs')): 
        
        # Check if already converted
        if os.path.exists(gaia_results_dir.joinpath(gaia_mrxs_file.name).with_suffix('')):
            with open(log_file, 'a') as log: 
                log.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Already converted {gaia_mrxs_file}. Continuing.\n')
            continue

        local_mrxs_file = local_input.joinpath(gaia_mrxs_file.name)
        copy_mrxs_from_gaia(gaia_mrxs_file, local_mrxs_file)
               
        converted_dicom_dir = local_output.joinpath(local_mrxs_file.stem)
        # Run in separate process to ensure release of RAM afterwards
        p = Process(target=run_conversion, args=(local_mrxs_file, converted_dicom_dir))
        p.start()
        p.join()
    
        copy_dcm_to_gaia(converted_dicom_dir, gaia_results_dir)

        clean_up([local_mrxs_file, local_mrxs_file.with_suffix(''), converted_dicom_dir])
        with open(log_file, 'a') as log: 
            log.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Successfully converted {gaia_mrxs_file}\n')
