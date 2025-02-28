import pydicom
from pydicom.sr.coding import Code
from git_utils import get_git_remote_url, get_git_commit_hash


# Basic Metadata
manufacturer = 'University Hospital Erlangen and Fraunhofer MEVIS'
manufacturer_model_name = 'BMDeep data conversion'
software_versions = get_git_remote_url(simplify=True)
device_serial_number = get_git_commit_hash()

# Labels 
roi_labels = {
    'monolayer': [Code('309825002', 'SCT', 'Spatial and relational concepts'), Code('111099', 'DCM', 'Selected region')],
}

cell_labels = {
    'artifact': [Code('91723000', 'SCT', 'Anatomical Stucture'), Code('91723000', 'SCT', 'Anatomical Stucture')], 
    'basophilic_band': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')], 
    'basophilic_erythroblast': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')], 
    'basophilic_metamyelocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'basophilic_myelocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')], 
    'damaged_cell': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')], 
    'degranulated_neutrophilic_metamyelocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')], 
    'degranulated_neutrophilic_myelocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'eosinophilic_band': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'eosinophilic_metamyelocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'eosinophilic_myelocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'erythrocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'giant_platelet': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'lymphoblast': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'lymphocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'lymphocytic_blast': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'lymphoidocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'macrophage': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'megakaryocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'micromegakaryocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'mitosis': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'monoblast': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'monocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'monocytic_blast': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'myeloblast': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'myelocytic_blast': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'neutrophil_extracellular_trap': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'neutrophilic_band': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'neutrophilic_metamyelocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'neutrophilic_myelocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'orthochromatic_erythroblast': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'phagocytosis': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'plasma_cell': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'polychromatic_erythroblast': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'proerythroblast': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'prolymphocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'promegakaryocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'promonocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'promyelocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'pseudo_gaucher_cell': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'segmented_basophil': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'segmented_eosinophil': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'segmented_neutrophil': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'smudge_cell': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'spicule': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'technically_unfit': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'thrombocyte': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'thrombocyte_aggregate': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')],
    'unknown_blast': [Code('tbd', 'tbd', 'tbd'), Code('tbd', 'tbd', 'tbd')]
}