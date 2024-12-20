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

## TODOs
1. Test basic conversion and investigate automatically filled metadata (including pixel spacing)
    - Default values are across this code directory: https://github.com/imi-bigpicture/wsidicom/tree/ab16e38c678b4bb6eb8e2c670d4c7278c67edf03/wsidicom/metadata
    - Contact wsidicom author with questions. 
2. Include additional available metadata (via wsidicom API or JSON)
3. Verify correct conversion with dciodvfy on every file and dcentvfy on every set of files in a series. 
4. Create BigQuery tables for lab and genetic data

### Investigation of automatically filled metadata
Overview on attributes: https://dicom.innolitics.com/ciods/vl-whole-slide-microscopy-image 


#### Potential problems (identified by manual inspection)
- Specimen UID different for each SOPInstance in Series -> should be the same
- Default ICC profile valid? 
- AnatomicPathologySpecimenTypesCode -> could not even find that attribute
- Photometric Interpretation? 
- Is compression method ISO_10918_1 fine? 
- X Offset in Slide Coordinate System --> how can I check that? 
- Are 10 DICOM levels too much? How can this be influenced during conversion ? 
