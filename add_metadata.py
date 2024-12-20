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


if __name__ == '__main__': 
    path_to_clinical_metadata = '/home/dschacherer/bmdeep_conversion/data/clinical_data.csv'
    clinical_metadata = pd.read_csv(path_to_clinical_metadata, delimiter=';')
    print(clinical_metadata)
    path_to_input_file = '/home/dschacherer/bmdeep_conversion/data/F7177163C833DFF4B38FC8D2872F1EC6_1_bm.mrxs'
    path_to_output_folder = '/home/dschacherer/bmdeep_conversion/data_converted/' # include subfolder 
    tile_size = 512 # TODO: decide with Henning 


    wsi = WsiDicomizer.open(path_to_input_file)
    print(type(wsi.metadata), wsi.metadata) # WSI metadata
    print(type(wsi.levels))
    print(wsi.levels[1].datasets[0]) # level metadata
    
    
    # Add clinical metadata from csv 


    # Do we want to set any of these metadata as well? 
    study = Study(identifier="Study identifier")
    series = Series(number=1)
    patient = Patient(name="FamilyName^GivenName")
    label = Label(text="Label text")
    equipment = Equipment(
        manufacturer="Scanner manufacturer",
        model_name="Scanner model name",
        device_serial_number="Scanner serial number",
        software_versions=["Scanner software versions"],
    )

    specimen = Specimen(
        identifier="Specimen",
        extraction_step=Collection(method=SpecimenCollectionProcedureCode("Excision")),
        type=AnatomicPathologySpecimenTypesCode("Gross specimen"),
        container=ContainerTypeCode("Specimen container"),
        steps=[Fixation(fixative=SpecimenFixativesCode("Neutral Buffered Formalin"))],
    )

    block = Sample(
        identifier="Block",
        sampled_from=[specimen.sample(method=SpecimenSamplingProcedureCode("Dissection"))],
        type=AnatomicPathologySpecimenTypesCode("tissue specimen"),
        container=ContainerTypeCode("Tissue cassette"),
        steps=[Embedding(medium=SpecimenEmbeddingMediaCode("Paraffin wax"))],
    )

    slide_sample = SlideSample(
        identifier="Slide sample",
        sampled_from=block.sample(method=SpecimenSamplingProcedureCode("Block sectioning")),
    )

    slide = Slide(
        identifier="Slide",
        stainings=[
            Staining(
                substances=[
                    SpecimenStainsCode("hematoxylin stain"),
                    SpecimenStainsCode("water soluble eosin stain"),
                ]
            )
        ],
        samples=[slide_sample],
    )
    metadata = WsiDicomizerMetadata(
        study=study,
        series=series,
        patient=patient,
        equipment=equipment,
        slide=slide,
        label=label,
    )