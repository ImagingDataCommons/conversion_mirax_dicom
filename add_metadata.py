import pandas as pd 

from wsidicom.conceptcode import (
    AnatomicPathologySpecimenTypesCode,
    ContainerTypeCode,
    SpecimenCollectionProcedureCode,
    SpecimenEmbeddingMediaCode,
    SpecimenFixativesCode,
    SpecimenSamplingProcedureCode,
    SpecimenStainsCode,
)
from wsidicom.metadata import (
    Collection,
    Embedding,
    Equipment,
    Fixation,
    Label,
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
from wsidicomizer import WsiDicomizer


# TODO: add private tag with original filename to enable later problem tracking

def build_collection_wide_metadata() -> WsiDicomizerMetadata: 
    study = Study(uid="Study Instance UID", 
                  identifier="Study identifier"
    )
    
    series = Series(uid="Series Instance UID",
                    number=1
    )
     
    patient = Patient(
        identifier="Patient", 
        sex=PatientSex, 
        species_description="" # , 
        de_identification="" # 
    )
    
    # for two patients a different scanner was used
    # Camera type etc. and more available in Mirax file's attributes 
    equipment = Equipment(
        manufacturer="Mirax",
        model_name="Scanner model name", # 'mirax.NONHIERLAYER_1_SECTION.SCANNER_HARDWARE_VERSION'
        device_serial_number="Scanner serial number", # not available to my knowledge
        software_versions=["Scanner software versions"], #'mirax.NONHIERLAYER_1_SECTION.SCANNER_SOFTWARE_VERSION': '1,18,2,51404',
    )
 
    specimen = Specimen(
        identifier="Specimen",
        extraction_step=Collection(method=SpecimenCollectionProcedureCode("Aspiration")), # P1-03130
        type=AnatomicPathologySpecimenTypesCode("Aspirate"), # G-8003
        container=ContainerTypeCode("Specimen vial"), # A-01024 
    )

    slide_sample = SlideSample(
        identifier="Slide sample",
        type=AnatomicPathologySpecimenTypesCode("Smear sample"), # G-803C
        sampled_from=specimen.sample(method=SpecimenSamplingProcedureCode("Smear procedure")), # P1-0329D
        container=ContainerTypeCode("Microscope slide"), # A-0101B
        steps=[Fixation(fixative=SpecimenFixativesCode("Neutral Buffered Formalin"))], # is there any?
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
    
    # TODO: 
    # Image, OpticalPath

    return WsiDicomizerMetadata(
        study=study,
        series=series,
        patient=patient,
        equipment=equipment,
        slide=slide
    ) 

def fill_missing_metadata(metadata: WsiDicomizerMetadata) -> WsiDicomizerMetadata: 
    pass 

if __name__ == '__main__': 
    path_to_clinical_metadata = '/home/dschacherer/bmdeep_conversion/data/clinical_data.csv'
    clinical_metadata = pd.read_csv(path_to_clinical_metadata, delimiter=';')    