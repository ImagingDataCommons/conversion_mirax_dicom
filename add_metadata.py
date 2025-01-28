import argparse
import openslide
import pandas as pd 
from pathlib import Path
from enum import Enum

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
    Patient,
    PatientSex,
    Sample,
    Series,
    Slide,
    SlideSample,
    Specimen,
    Staining,
    Study,
)
from wsidicomizer.metadata import WsiDicomizerMetadata


# TODO: add private tag with original filename to enable later problem tracking. Not necessary, filename=patient id
def build_metadata(patient_id: str, mrxs_metadata: openslide._PropertyMap, clinical_data: pd.DataFrame) -> WsiDicomizerMetadata: 

    equipment = Equipment(
        manufacturer="Mirax",
        model_name= mrxs_metadata['mirax.NONHIERLAYER_1_SECTION.SCANNER_HARDWARE_VERSION'], 
        device_serial_number="Scanner serial number", # not available to my knowledge
        software_versions=[mrxs_metadata['mirax.NONHIERLAYER_1_SECTION.SCANNER_SOFTWARE_VERSION']]
    )

    image = Image(
        acquisition_datetime=mrxs_metadata['mirax.GENERAL.SLIDE_CREATIONDATETIME'],
        # objective power 'openslide.objective-power' or mirax.GENERAL.OBJECTIVE_MAGNIFICATION # not inferred automatically
        # camera type mirax.GENERAL.CAMERA_TYPE': 'CIS_VCC_F52U25CL'
        # 'mirax.GENERAL.OBJECTIVE_NAME': 'Plan-Apochromat
        lossy_compressions="" # how to handle compression, uncompression, recompression
    )

    # Note UID will be generated automatically
    study = Study(identifier="Study identifier") # necessary?

    # Note UID will be generated automatically, can be removed if we don't need to add anything else
    series = Series()
     
    patient = Patient(
        identifier=patient_id, 
        sex=PatientSex(clinical_data.loc[patient_id]['gender']),
        de_identification="" # 
    )
 
    specimen = Specimen(
        identifier="Aspirate", # necessary?
        extraction_step=Collection(method=SpecimenCollectionProcedureCode("Aspiration")), # P1-03130
        type=AnatomicPathologySpecimenTypesCode("Aspirate"), # G-8003
        container=ContainerTypeCode("Specimen vial") # A-01024 
    )

    smear = Sample(
        identifier="Smear", # necessary?
        sampled_from=[specimen.sample(method=SpecimenSamplingProcedureCode("Smear procedure"))],# P1-0329D
        type=AnatomicPathologySpecimenTypesCode("Smear sample"), # G-803C
        container=ContainerTypeCode("Microscope slide")
    )
 
    slide_sample = SlideSample(
        identifier="Slide sample", # necessary? 
        sampled_from=smear.sample(method=SpecimenSamplingProcedureCode("Smear procedure")), # P1-0329D
    )

    slide = Slide(
        identifier="Slide",
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
        slide=slide
    ) 

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
    patient_id = args.mrxs_file.stem.split('_')[0]
    print(patient_id)
    wsidicomizer_metadata = build_metadata(patient_id, mrxs_file.properties, clinical_metadata)
    print(wsidicomizer_metadata)