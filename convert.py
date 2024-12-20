import os
import argparse 
import shutil
from pathlib import Path
from wsidicomizer import WsiDicomizer


def copy_from_gaia(gaia_file_path: Path, local_image_folder: Path) -> Path:
    local_file_path = local_image_folder.joinpath(gaia_file_path.name)
    shutil.copy(gaia_file_path, local_file_path)
    shutil.copytree(gaia_file_path.with_suffix(''), local_file_path.with_suffix('')) # copy corresponding folder with .dat and .ini files 
    return local_file_path

def run_conversion(input_file: Path, output_folder: Path) -> Path: 
    created_files = WsiDicomizer.convert(
        filepath=input_file,
        output_path=output_folder.joinpath(input_file.stem),
        metadata=None
    )
    created_files_dir = Path(created_files[0]).parent
    return created_files_dir

def copy_to_gaia(local_dir: Path, gaia_dir: Path) -> None: 
    shutil.copytree(local_dir, gaia_dir.joinpath(local_dir.name))


if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Run BMDeep dataset conversion from MRXS to DICOM on a local machine, but retrieving dataset from mounted server.') 
    parser.add_argument('gaia_work_dir', type=Path, help='Path to directory on Gaia which should be searched for MRXS files and where resulting DICOM files can be stored.')
    parser.add_argument('local_work_dir', type=Path, help='Path to local directory where intermediate results can be stored.')
    args = parser.parse_args()

    # Configuration
    local_input = args.local_work_dir.joinpath('be_converted')
    local_output = args.local_work_dir.joinpath('is_converted')
    log_file = args.local_work_dir.joinpath('log.txt')
    gaia_results_dir = args.gaia_work_dir.joinpath('bmdeep_DICOM_converted') #Path("/home/dschacherer/mnt/gaia/publicProjects/BMDeep/data/")
    for dir in [local_input, local_output, gaia_results_dir]: 
        dir.mkdir(parents=True, exist_ok=True) 

    # Conversion workflow
    for gaia_file_path in args.gaia_work_dir.rglob('*_bm.mrxs'): 
        try: 
            local_mrxs_file = copy_from_gaia(gaia_file_path, local_input)
        except Exception as e: 
            with open(log_file, 'a') as log: 
                log.write(f'Copy error {e}: {gaia_file_path}\n') 
            continue 
        
        try: 
            created_dicom_dir = run_conversion(local_mrxs_file, local_output)
        except Exception as e: 
            with open(log_file, 'a') as log: 
                log.write(f'Conversion error {e}: {local_mrxs_file}\n')
            os.remove(local_mrxs_file)
            continue 
        
        try: 
            copy_to_gaia(created_dicom_dir, gaia_results_dir)
        except Exception as e: 
            with open(log_file, 'a') as log: 
                log.write(f'Copy error {e}: {created_dicom_dir}\n')
            # Clean-up 
            os.remove(local_mrxs_file)
            shutil.rmtree(local_mrxs_file.with_suffix(''))
            shutil.rmtree(created_dicom_dir)
            continue

        # Clean-up 
        os.remove(local_mrxs_file)
        shutil.rmtree(local_mrxs_file.with_suffix(''))
        shutil.rmtree(created_dicom_dir)