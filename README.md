# BoneMarrowWSI-PediatricLeukemia dataset conversion
**--- This repository is still work in progress ---**

This repository contains the code that was used for the conversion of the [BoneMarrowWSI-PediatricLeukemia](https://doi.org/10.5281/zenodo.14933088) (aka BMDeep) dataset into DICOM format for ingestion into IDC. 

This repository includes:  
1) code for image conversion from MRXS to DICOM.
2) code for annotation conversion from CSV to DICOM.

Both are implemented to be run on a local machine, while retrieving actual data and returning converted results from/to a mounted server called Gaia.

## Requirements
- see requirements.txt 
- for running the verification scripts: installation of dicom3tools required 
    1. wget https://dclunie.com/dicom3tools/workinprogress/dicom3tools_1.00.snapshot.20250128115421.tar.bz2 (or the most recent version available at https://dclunie.com/dicom3tools/workinprogress/index.html)
    2. bzcat <dicom3tools_1.00.snapshot.20250128115421.tar.bz2 | tar -xf 
    3. mv dicom3tools_1.00.snapshot.20250128115421 dicom3tools
    4. sudo apt-get install xutils-dev
    5. cd dicom3tools && ./Configure && imake -I./config -DInstallInTopDir && make World && make install

## Documentation
