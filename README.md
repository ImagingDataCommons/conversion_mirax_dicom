# MRXS to DICOM
Code for BMDeep dataset conversion from MRXS to DICOM on a local machine, while retrieving actual data and returning converted results from/to a mounted server called Gaia.

## Requirements 
- pip install wsidicomizer 
- for verification: installation of dicom3tools
    1. wget https://dclunie.com/dicom3tools/workinprogress/dicom3tools_1.00.snapshot.20241114112559.tar.bz2,
    2. bunzip2 dicom3tools_1.00.snapshot.20241114112559.tar.bz2
    3. tar xf dicom3tools_1.00.snapshot.20241114112559.tar
    4. mv dicom3tools_1.00.snapshot.20241114112559 dicom3tools
    5. sudo apt-get install xutils-dev
    6. cd dicom3tools && ./Configure && imake -I./config -DInstallInTopDir -DUseXXXXID && make World && make install

## Documentation 
- see [BMDeep Conversion notes](https://docs.google.com/document/d/1yobF48SQlx4rMwwsj-T324Nfu25PJt5CFDlQB9E1Z-8/edit?tab=t.0)
- see PW42 Project Page: [Conversion of bone marrow smear dataset from MIRAX format into DICOM](https://projectweek.na-mic.org/PW42_2025_GranCanaria/Projects/ConversionOfBoneMarrowSmearDatasetFromMiraxFormatIntoDicom/)

### Potential problems (identified by manual inspection)
- Specimen UID different for each SOPInstance in Series -> should be the same
- Default ICC profile valid? 
- AnatomicPathologySpecimenTypesCode -> could not even find that attribute
- Photometric Interpretation? 
- Is compression method ISO_10918_1 fine? 
- X Offset in Slide Coordinate System --> how can I check that? 
- Are 10 DICOM levels too much? How can this be influenced during conversion? 
