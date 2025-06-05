import os
import argparse 
import shutil
import openslide
import numpy as np 
import pandas as pd
from pathlib import Path
from datetime import datetime
from multiprocessing import Process
from typing import Dict, List

from convert import wsidicomizer_convert
from metadata_config import read_nci_thesaurus, find_property_by_suffix, build_metadata, build_additional_metadata


def copy_mrxs_from_gaia(gaia_mrxs_path: Path, local_mrxs_path: Path) -> None:
    shutil.copy(gaia_mrxs_path, local_mrxs_path)
    shutil.copytree(gaia_mrxs_path.with_suffix(''), local_mrxs_path.with_suffix(''), dirs_exist_ok=True) # copy corresponding folder with .dat and .ini files 


def get_mrxs_slide_properties(mrxs_file: Path) -> Dict: 
    mrxs_slide = openslide.OpenSlide(mrxs_file)
    mrxs_properties = dict(mrxs_slide.properties)
    mrxs_slide.close()
    return mrxs_properties


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


def run(local_work_dir: Path, gaia_work_dir: Path, metadata: Path, ) -> None:
    ''' Function to run complete image conversion pipeline '''

    # Configuration
    local_input = local_work_dir.joinpath('be_converted')
    local_output = local_work_dir.joinpath('is_converted')
    log_file = local_work_dir.joinpath('image_conversion_log.txt')
    gaia_results_dir = gaia_work_dir.joinpath('bmdeep_DICOM_converted') 
    for dir in [local_input, local_output, gaia_results_dir]: 
        dir.mkdir(parents=True, exist_ok=True)

    # Read clinical metadata and NCI Thesaurus
    clinical_metadata = pd.read_csv(metadata, delimiter=';')
    clinical_metadata.set_index('patient_id', inplace=True)
    nci_thesaurus = read_nci_thesaurus(Path(__file__).with_name('NCIt_Neoplasm_Core_Terminology.csv'))

    # Conversion loop
    for gaia_mrxs_file in sorted(args.gaia_work_dir.rglob('*_bm.mrxs')): 
        slide_id = gaia_mrxs_file.stem
        patient_id = slide_id.split('_')[0]
        
        # Check if already converted
        if os.path.exists(gaia_results_dir.joinpath(gaia_mrxs_file.name).with_suffix('')):
            with open(log_file, 'a') as log: 
                log.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Already converted {gaia_mrxs_file}. Continuing.\n')
            continue
        
        # Only convert if clinical data available
        if patient_id not in clinical_metadata.index.to_list():
            with open(log_file, 'a') as log: 
                log.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - No clinical metadata available for {gaia_mrxs_file}. Continuing.\n')
            continue

        # Ignore duplicates that reside in "Validation Set" folder
        if 'Validation' in str(gaia_mrxs_file): 
            continue
        # Don't convert 42A0E188F5033BC65BF8D78622277C4E_1_bm.mrxs, insted 42A0E188F5033BC65BF8D78622277C4E_3_bm.mrxs
        if slide_id == '42A0E188F5033BC65BF8D78622277C4E_1_bm': 
            continue
        
        local_mrxs_file = local_input.joinpath(gaia_mrxs_file.name)
        copy_mrxs_from_gaia(gaia_mrxs_file, local_mrxs_file)

        
        mrxs_properties = get_mrxs_slide_properties(local_mrxs_file)
        mrxs_properties.pop('mirax.GENERAL.SLIDE_ID') # might carry security risk, thus remove 

        print(patient_id)
        print(clinical_metadata.loc[patient_id]['ncit_concept_code'])
        # Build metadata to be supplied to wsidicomizer 
        slide_metadata = build_metadata(slide_id=slide_id, 
                                        patient_id=patient_id, 
                                        mrxs_metadata=mrxs_properties, 
                                        clinical_data=clinical_metadata)    
        
        # Build additional metadata that will be added outside of wsidicom's metadata scheme, but within the convert function
        # See issue: https://github.com/imi-bigpicture/wsidicomizer/issues/124
        aquisition_duration = float(find_property_by_suffix(mrxs_properties, 'scanning_time_in_sec'))
        primary_diagnoses_code = clinical_metadata.loc[patient_id]['ncit_concept_code']
        additional_metadata = build_additional_metadata(
            study_description='Bone marrow aspirate smear, pediatric leukemia', 
            image_series_description='Bone marrow aspirate smear, May-Gruenwald-Giemsa stain',
            patient_id=patient_id,
            patient_age=clinical_metadata.loc[patient_id]['age'], 
            aquisition_duration=aquisition_duration, 
            primary_diagnoses_code=primary_diagnoses_code,
            primary_diagnoses_code_meaning=nci_thesaurus.get(primary_diagnoses_code, np.nan),  
            clinical_trial_coord_center='University Hospital Erlangen', 
            clinical_trial_protocol_name='BoneMarrowWSI-PediatricLeukemia', 
            clinical_trial_sponsor='Uni Hospital Erlangen, Fraunhofer MEVIS, Uni Erlangen-Nuremberg', 
            other_clinical_trial_protocol_id='doi:10.5281/zenodo.14933087',
            other_clinical_trial_protocol_id_issuer='DOI',
            original_mirax_properties=mrxs_properties
        )

        converted_dicom_dir = local_output.joinpath(local_mrxs_file.stem)
        # Run in separate process to ensure release of RAM afterwards
        p = Process(target=wsidicomizer_convert, args=(local_mrxs_file, converted_dicom_dir, slide_metadata, additional_metadata))
        p.start()
        p.join()

        copy_dcm_to_gaia(converted_dicom_dir, gaia_results_dir)

        clean_up([local_mrxs_file, local_mrxs_file.with_suffix(''), converted_dicom_dir])
        with open(log_file, 'a') as log: 
            log.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Successfully converted {gaia_mrxs_file}\n')

    # Remove empty folders created for conversion 
    shutil.rmtree(local_input)
    shutil.rmtree(local_output)



if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Run BMDeep dataset conversion from MRXS to DICOM on a local machine, but retrieving dataset from mounted server.') 
    parser.add_argument('gaia_work_dir', type=Path, help='Path to directory on Gaia which should be searched for MRXS files and where resulting DICOM files can be stored.')
    parser.add_argument('local_work_dir', type=Path, help='Path to local directory where intermediate results can be stored.')
    parser.add_argument('metadata', type=Path, help='Path to clinical metadata CSV file.')
    args = parser.parse_args()

    run(args.local_work_dir, args.gaia_work_dir, args.metadata)