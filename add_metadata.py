import argparse
import openslide
import pydicom 
import pandas as pd 
from pathlib import Path
from typing import List

from wsidicom.conceptcode import (
    AnatomicPathologySpecimenTypesCode,
    ContainerTypeCode,
    SpecimenCollectionProcedureCode,
    SpecimenSamplingProcedureCode,
    SpecimenStainsCode,
)
from wsidicom.metadata import (
    Collection,
    Equipment,
    Image,
    Objectives,
    OpticalPath,
    Patient,
    PatientSex,
    Series,
    Slide,
    SlideSample,
    Specimen,
    Staining,
    Study,
)
from wsidicomizer.metadata import WsiDicomizerMetadata

# open:
# lossy compression
# patient Id --> slide identifier?
# wsidicomizer not working in new version 

def build_metadata(slide_id: str, patient_id: str, mrxs_metadata: openslide._PropertyMap, clinical_data: pd.DataFrame) -> WsiDicomizerMetadata: 

    equipment = Equipment(
        manufacturer="Mirax",
        model_name= mrxs_metadata['mirax.NONHIERLAYER_1_SECTION.SCANNER_HARDWARE_VERSION'], 
        software_versions=[mrxs_metadata['mirax.NONHIERLAYER_1_SECTION.SCANNER_SOFTWARE_VERSION']]
    )

    image = Image(
        acquisition_datetime=mrxs_metadata['mirax.GENERAL.SLIDE_CREATIONDATETIME'],
        lossy_compressions="" # Compression ratio is wrong
    )

    objective = Objectives(
        objective_power=mrxs_metadata['mirax.GENERAL.OBJECTIVE_MAGNIFICATION']
    )

    optical_path = OpticalPath(
        objective=objective
    )

    # Note UID will be generated automatically
    study = Study(identifier=patient_id)

    # Note UID will be generated automatically, can be removed if we don't need to add anything else
    series = Series()
     
    patient = Patient(
        identifier=patient_id, 
        sex=PatientSex(clinical_data.loc[patient_id]['gender']),
        de_identification="" # could be mentioned that deidentification is used. 
    )
 
    specimen = Specimen(
        identifier=patient_id,
        extraction_step=Collection(method=SpecimenCollectionProcedureCode("Aspiration")), # P1-03130
        type=AnatomicPathologySpecimenTypesCode("Aspirate"), # G-8003
        container=ContainerTypeCode("Specimen vial") # A-01024 
    )
 
    slide_sample = SlideSample(
        identifier=patient_id,
        sampled_from=specimen.sample(method=SpecimenSamplingProcedureCode("Smear procedure")), # P1-0329D
    )

    slide = Slide(
        identifier=slide_id,
        stainings=[
            Staining(
                substances=[
                    SpecimenStainsCode("may-Grunwald giemsa stain"), # C-2281A
                ]
            )
        ],
        samples=[slide_sample],
    )

    return WsiDicomizerMetadata(
        image=image,
        study=study,
        series=series,
        patient=patient,
        equipment=equipment,
        optical_paths=[optical_path],
        slide=slide
    ) 


def manual_metadata_adding(patient_age: str, 
                           aquisition_duration: int, 
                           primary_diagnoses_code_seq: str, 
                           admitting_diagnoses_description: str, 
                           accession_number: str,
                           clinical_trial_coord_center: str, 
                           clinical_trial_protocol_name: str, 
                           clinical_trial_sponsor: str, 
                           dcm_files: List[Path]) -> List[Path]: 
    
    for dcm_file in dcm_files:
        ds = pydicom.dcmread(dcm_file)
        ds.PatientAge = patient_age 
        ds.add_new([0x0020, 0x0012], 'IS', aquisition_duration) 
        ds.add_new([0x0008, 0x1080], 'LO', admitting_diagnoses_description)
        ds.add_new([0x0012, 0x0060], 'LO', clinical_trial_coord_center) 
        ds.add_new([0x0012, 0x0021], 'LO', clinical_trial_protocol_name)
        ds.add_new([0x0012, 0x0010], 'LO', clinical_trial_sponsor)

        ds.diagnoses_code_seq = [pydicom.Dataset()]
        ds.diagnoses_code_seq[0].add_new([0x0008, 0x1084], 'LO', primary_diagnoses_code_seq) # has to be updated        
         
        ds.save_as(dcm_file)


if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description='Generate WsiDicomizerMetadata for testing.') 
    parser.add_argument('mrxs_file', type=Path, help='Path to MRXS file.')
    parser.add_argument('clinical_data', type=Path, help='Path to clinical data csv table.')
    args = parser.parse_args()

    mrxs_file = openslide.OpenSlide(args.mrxs_file)
    clinical_metadata = pd.read_csv(args.clinical_data, delimiter=';')
    print(clinical_metadata)
    clinical_metadata.set_index('patient_id', inplace=True)
    print(clinical_metadata)
    slide_id = args.mrxs_file.stem
    patient_id = slide_id.split('_')[0]
    print(patient_id)
    wsidicomizer_metadata = build_metadata(slide_id, patient_id, mrxs_file.properties, clinical_metadata)
    print(wsidicomizer_metadata)