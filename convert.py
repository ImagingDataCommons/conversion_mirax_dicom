import os
import argparse 
import shutil
import openslide
import pandas as pd
from pathlib import Path
from wsidicomizer import WsiDicomizer
from wsidicomizer.metadata import WsiDicomizerMetadata
from datetime import datetime
from multiprocessing import Process
from typing import Dict, List
from conversion_mirax_dicom.image_conversion.add_metadata import find_property_by_suffix, build_metadata, manual_metadata_adding


def copy_mrxs_from_gaia(gaia_mrxs_path: Path, local_mrxs_path: Path) -> None:
    shutil.copy(gaia_mrxs_path, local_mrxs_path)
    shutil.copytree(gaia_mrxs_path.with_suffix(''), local_mrxs_path.with_suffix(''), dirs_exist_ok=True) # copy corresponding folder with .dat and .ini files 


def get_mrxs_slide_properties(mrxs_file: Path) -> Dict: 
    mrxs_slide = openslide.OpenSlide(mrxs_file)
    mrxs_properties = dict(mrxs_slide.properties)
    mrxs_slide.close()
    return mrxs_properties


def run_conversion(input_file: Path, output_folder: Path, metadata: WsiDicomizerMetadata) -> None: 
    _ = WsiDicomizer.convert(
        filepath=input_file,
        output_path=output_folder,
        metadata=metadata,
        tile_size=1024, # wsidicom seems to not be able to infer tile size from mrxs automatically, so will use this one provided here.
        #include_levels=, 
        include_label=False, 
        workers=4, 
        offset_table='eot'
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
    parser.add_argument('metadata', type=Path, help='Path to clinical metadata CSV file.')
    args = parser.parse_args()

    # Configuration
    local_input = args.local_work_dir.joinpath('be_converted')
    local_output = args.local_work_dir.joinpath('is_converted')
    log_file = args.local_work_dir.joinpath('log.txt')
    gaia_results_dir = args.gaia_work_dir.joinpath('bmdeep_DICOM_converted') 
    for dir in [local_input, local_output, gaia_results_dir]: 
        dir.mkdir(parents=True, exist_ok=True)
    
    clinical_metadata = pd.read_csv(args.metadata, delimiter=';')
    clinical_metadata.set_index('patient_id', inplace=True)

    for gaia_mrxs_file in sorted(args.gaia_work_dir.rglob('*_bm.mrxs')): 
        # Check if already converted
        if os.path.exists(gaia_results_dir.joinpath(gaia_mrxs_file.name).with_suffix('')):
            with open(log_file, 'a') as log: 
                log.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Already converted {gaia_mrxs_file}. Continuing.\n')
            continue
        
        local_mrxs_file = local_input.joinpath(gaia_mrxs_file.name)
        copy_mrxs_from_gaia(gaia_mrxs_file, local_mrxs_file)

        slide_id = gaia_mrxs_file.stem
        patient_id = slide_id.split('_')[0]
        mrxs_properties = get_mrxs_slide_properties(local_mrxs_file)
        slide_metadata = build_metadata(slide_id=slide_id, 
                                        patient_id=patient_id, 
                                        mrxs_metadata=mrxs_properties, 
                                        clinical_data=clinical_metadata)    
        print(slide_metadata)
        converted_dicom_dir = local_output.joinpath(local_mrxs_file.stem)
        # Run in separate process to ensure release of RAM afterwards
        p = Process(target=run_conversion, args=(local_mrxs_file, converted_dicom_dir, slide_metadata))
        p.start()
        p.join()

        # Add additional metadata not automatically accessible during conversion
        slide_id = gaia_mrxs_file.stem
        patient_id = slide_id.split('_')[0]
        aquisition_duration = find_property_by_suffix(mrxs_properties, 'scanning_time_in_sec')
        
        manual_metadata_adding(patient_age=clinical_metadata.loc[patient_id]['age'], 
                               aquisition_duration=aquisition_duration, 
                               primary_diagnoses_code_seq=clinical_metadata.loc[patient_id]['ncit_concept_code'], 
                               admitting_diagnoses_description=','.join([clinical_metadata.loc[patient_id]['leukemia_type'], clinical_metadata.loc[patient_id]['leukemia_subtype']]),  
                               clinical_trial_coord_center='University Hospital Erlangen', 
                               clinical_trial_protocol_name='BMDeep', 
                               clinical_trial_sponsor='Fraunhofer MEVIS', 
                               dcm_files=list(converted_dicom_dir.iterdir()))
        
        copy_dcm_to_gaia(converted_dicom_dir, gaia_results_dir)

        clean_up([local_mrxs_file, local_mrxs_file.with_suffix(''), converted_dicom_dir])
        with open(log_file, 'a') as log: 
            log.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Successfully converted {gaia_mrxs_file}\n')
