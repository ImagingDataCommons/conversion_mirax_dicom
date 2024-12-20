from wsidicom import WsiDicom 
import pydicom 

if __name__ == '__main__': 
    wsi = WsiDicom.open('/home/dschacherer/bmdeep_conversion/data/bmdeep_DICOM_converted/F7177163C833DFF4B38FC8D2872F1EC6_1_bm')
    print(wsi.metadata)
    for level in wsi.levels: 
        print(pydicom.Dataset(level.datasets[0])) # level metadata