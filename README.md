# MRXS to DICOM
Code for BMDeep dataset conversion from MRXS to DICOM. 

This repository includes:  
1) code for image conversion 
2) code for annotation conversion 
Both are implemented to be run on a local machine, while retrieving actual data and returning converted results from/to a mounted server called Gaia.

## Requirements
- see requirements.txt 
- for verification: installation of dicom3tools
    1. wget https://dclunie.com/dicom3tools/workinprogress/dicom3tools_1.00.snapshot.20250128115421.tar.bz2
    2. bzcat <dicom3tools_1.00.snapshot.20250128115421.tar.bz2 | tar -xf -
    3. mv dicom3tools_1.00.snapshot.20250128115421 dicom3tools
    4. sudo apt-get install xutils-dev
    5. cd dicom3tools && ./Configure && imake -I./config -DInstallInTopDir && make World && make install

## Documentation
- see [BMDeep Conversion notes](https://docs.google.com/document/d/1yobF48SQlx4rMwwsj-T324Nfu25PJt5CFDlQB9E1Z-8/edit?tab=t.0)