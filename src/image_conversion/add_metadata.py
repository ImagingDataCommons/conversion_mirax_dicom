import math
import openslide
import pydicom 
import json
import pandas as pd 
from pathlib import Path
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
)
from wsidicomizer.metadata import WsiDicomizerMetadata


def read_nci_thesaurus(path: Path) -> Dict[str, str]: 
    df = pd.read_csv(path, sep=';', encoding="ISO-8859-1")
    ncit = df.set_index('Code')['Preferred Term'].to_dict()
    ncit['C3182'] = 'Acute Promyelocytic Leukemia with t(15;17)(q24.1;q21.2); PML-RARA' # manual adding of only code that is missing
    return ncit


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
     
    patient = Patient(
        identifier=patient_id, 
        sex=PatientSex(clinical_data.loc[patient_id]['gender'])
    )
 
    specimen = Specimen(
        identifier=patient_id,
        extraction_step=Collection(method=SpecimenCollectionProcedureCode('Aspiration')), # 14766002, SCT
        type=AnatomicPathologySpecimenTypesCode('Aspirate'), # 119295008, SCT
        container=ContainerTypeCode('Specimen vial') # 434746001, SCT 
    )
 
    slide_sample = SlideSample(
        identifier=patient_id,
        anatomical_sites=[pydicom.sr.coding.Code('14016003', 'SCT', 'Bone marrow')], # 14016003, SCT
        sampled_from=specimen.sample(method=SpecimenSamplingProcedureCode('Smear procedure')), # 448895004, SCT
    )

    slide = Slide(
        identifier=slide_id,
        stainings=[
            Staining(
                substances=[
                    SpecimenStainsCode('may-Grunwald giemsa stain'), # 255803006, SCT
                ]
            )
        ],
        samples=[slide_sample],
    )

    return WsiDicomizerMetadata(
        image=image,
        patient=patient,
        equipment=equipment,
        optical_paths=[optical_path],
        slide=slide
    ) 


def build_additional_metadata(
        study_description: str, 
        image_series_description: str, 
        patient_age: str,              
        aquisition_duration: float, 
        primary_diagnoses_code: Union[str, float],
        primary_diagnoses_code_meaning: Union[str, float],  
        admitting_diagnoses_description: Union[Tuple[str], Tuple[float]], 
        clinical_trial_coord_center: str, 
        clinical_trial_protocol_name: str, 
        clinical_trial_sponsor: str, 
        other_clinical_trial_protocol_id: str, 
        other_clinical_trial_protocol_id_issuer: str,
        original_mirax_properties: dict) -> pydicom.Dataset: 
    
    ds = pydicom.Dataset()
    ds.SeriesDescription = image_series_description
    ds.StudyDescription = study_description
    ds.PatientAge = patient_age 
    ds.add_new([0x0018, 0x9073], 'FD', aquisition_duration) 
    ds.add_new([0x0012, 0x0060], 'LO', clinical_trial_coord_center) 
    ds.add_new([0x0012, 0x0021], 'LO', clinical_trial_protocol_name)
    ds.add_new([0x0012, 0x0010], 'LO', clinical_trial_sponsor)

    if (isinstance(admitting_diagnoses_description[0], str) and isinstance(admitting_diagnoses_description[1], str)): # if not float, i.e., nan 
        admitting_diagnoses = ','.join(admitting_diagnoses_description[0], admitting_diagnoses_description[1])
        ds.add_new([0x0008, 0x1080], 'LO', admitting_diagnoses)


    if isinstance(primary_diagnoses_code, str): # if not float, i.e., nan 
        ds.add_new([0x0008, 0x1084], 'SQ', [pydicom.Dataset()]) # add AdmittingDiagnosesCodeSequence
        ds.AdmittingDiagnosesCodeSequence[0].add_new([0x0008, 0x0100], 'SH', primary_diagnoses_code) # CodeValue
        ds.AdmittingDiagnosesCodeSequence[0].add_new([0x0008, 0x0102], 'SH', 'NCIt') # CodingSchemeDesignator
        ds.AdmittingDiagnosesCodeSequence[0].add_new([0x0008, 0x0104], 'LO', primary_diagnoses_code_meaning) # CodeMeaning        

    ds.add_new([0x0012, 0x0023], 'SQ', [pydicom.Dataset()]) # add OtherClinicalTrialProtocolIDSequence
    ds.OtherClinicalTrialProtocolIDsSequence[0].add_new([0x0012, 0x0020], 'LO', other_clinical_trial_protocol_id)
    ds.OtherClinicalTrialProtocolIDsSequence[0].add_new([0x0012, 0x0022], 'LO', other_clinical_trial_protocol_id_issuer)

    ds.add_new([0x0040, 0x0555], 'SQ', [pydicom.Dataset()]) # add AcquisitionContextSequence
    ds.AcquisitionContextSequence[0].add_new([0x0040, 0xA040], 'CS', 'TEXT')
    ds.AcquisitionContextSequence[0].add_new([0x0040, 0xA043], 'SQ', [pydicom.Dataset()]) # add ConceptNameCodeSequence
    ds.AcquisitionContextSequence[0].ConceptNameCodeSequence[0].add_new([0x0008, 0x0100], 'SH', '121106') # CodeValue
    ds.AcquisitionContextSequence[0].ConceptNameCodeSequence[0].add_new([0x0008, 0x0100], 'SH', 'DCM') # CodingSchemeDesignator
    ds.AcquisitionContextSequence[0].ConceptNameCodeSequence[0].add_new([0x0008, 0x0100], 'LO', 'Comment') # CodeMeaning
    ds.AcquisitionContextSequence[0].add_new([0x0040, 0xA160], 'UT', json.dumps(original_mirax_properties))

    return ds 