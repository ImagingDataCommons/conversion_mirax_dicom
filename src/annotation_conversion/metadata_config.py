from pydicom.sr.coding import Code

from idc_annotation_conversion.git_utils import (
    get_git_remote_url,
    get_git_commit_hash,
)

# Basic Metadata
manufacturer = 'University Hospital Erlangen and Fraunhofer MEVIS'
manufacturer_model_name = 'BMDeep data conversion'
software_versions = 'tbd' #get_git_remote_url(simplify=True)
device_serial_number = 'tbd' #get_git_commit_hash()

# Labels description
labels = ['neutrophilic_metamyelocyte']
finding_categories = [Code('91723000', 'SCT', 'Anatomical Stucture')]
finding_types = [Code('118957004', 'SCT', 'Normal cell')]
labels_dict = dict(
    label=labels, 
    finding_category=finding_categories, 
    finding_type=finding_types
)