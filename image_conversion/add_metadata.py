import openslide
import pydicom 
import pandas as pd 
from datetime import datetime
from typing import Dict, Tuple, Union

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
    Slide,
    SlideSample,
    Specimen,
    Staining,
    Study,
)
from wsidicomizer.metadata import WsiDicomizerMetadata

def find_property_by_suffix(properties: Dict, suffix: str) -> Union[str, None]:
    for key in properties.keys():
        if key.lower().endswith(suffix):
            return properties[key]
    return None

def build_metadata(slide_id: str, patient_id: str, mrxs_metadata: openslide._PropertyMap, clinical_data: pd.DataFrame) -> WsiDicomizerMetadata: 

    equipment = Equipment(
        manufacturer="Mirax",
        model_name=find_property_by_suffix(mrxs_metadata, 'scanner_hardware_version'),
        software_versions=[find_property_by_suffix(mrxs_metadata, 'scanner_software_version')]
    )

    image = Image(
        acquisition_datetime=datetime.strptime(mrxs_metadata['mirax.GENERAL.SLIDE_CREATIONDATETIME'], '%d/%m/%Y %H:%M:%S')
    )

    objective = Objectives(
        objective_power=mrxs_metadata['mirax.GENERAL.OBJECTIVE_MAGNIFICATION']
    )

    optical_path = OpticalPath(
        objective=objective
    )

    study = Study(accession_number=patient_id[:8]) # SH thus take only first 8 characters 
     
    patient = Patient(
        identifier=patient_id, 
        sex=PatientSex(clinical_data.loc[patient_id]['gender'])
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
        patient=patient,
        equipment=equipment,
        optical_paths=[optical_path],
        slide=slide
    ) 


def build_additional_metadata(patient_age: str, 
                           aquisition_duration: float, 
                           primary_diagnoses_code: str,
                           primary_diagnoses_code_meaning: str,  
                           admitting_diagnoses_description: str, 
                           clinical_trial_coord_center: str, 
                           clinical_trial_protocol_name: str, 
                           clinical_trial_sponsor: str) -> pydicom.Dataset: 
    
    ds = pydicom.Dataset()
    ds.PatientAge = patient_age 
    ds.add_new([0x0018, 0x9073], 'FD', aquisition_duration) 
    ds.add_new([0x0008, 0x1080], 'LO', admitting_diagnoses_description)
    ds.add_new([0x0012, 0x0060], 'LO', clinical_trial_coord_center) 
    ds.add_new([0x0012, 0x0021], 'LO', clinical_trial_protocol_name)
    ds.add_new([0x0012, 0x0010], 'LO', clinical_trial_sponsor)

    ds.add_new([0x0008, 0x1084], 'SQ', [pydicom.Dataset()]) # add AdmittingDiagnosesCodeSequence
    ds.AdmittingDiagnosesCodeSequence[0].add_new([0x0008, 0x0100], 'SH', primary_diagnoses_code) # CodeValue
    ds.AdmittingDiagnosesCodeSequence[0].add_new([0x0008, 0x0102], 'SH', 'NCIt') # CodingSchemeDesignator
    ds.AdmittingDiagnosesCodeSequence[0].add_new([0x0008, 0x0104], 'LO', primary_diagnoses_code_meaning) # TODO: CodeMeaning        
        
    return ds 