from pydicom.sr.coding import Code
from git_utils import get_git_remote_url, get_git_commit_hash


# Basic Metadata
manufacturer = 'University Hospital Erlangen and Fraunhofer MEVIS'
manufacturer_model_name = 'BMDeep data conversion'
software_versions = get_git_remote_url(simplify=True)
device_serial_number = get_git_commit_hash()

# Labels 
roi_labels = {
    'monolayer': [Code('85756007', 'SCT', 'Tissue'), Code('tbd', 'SCT', 'tbd')],
}

cell_labels = {
    'artifact': [Code('91723000', 'SCT', 'Anatomical Stucture'), Code('91723000', 'SCT', 'Anatomical Stucture')], 
    'basophilic_band': [], 
    'basophilic_erythroblast': [], 
    'basophilic_metamyelocyte': [], 
    'basophilic_myelocyte': [], 
    'damaged_cell': [], 
    'degranulated_neutrophilic_metamyelocyte': [], 
    'degranulated_neutrophilic_myelocyte': [], 
    'eosinophilic_band': [], 
    'eosinophilic_metamyelocyte': [], 
    'eosinophilic_myelocyte': [], 
    'erythrocyte': [], 
    'giant_platelet': [], 
    'lymphoblast': [], 
    'lymphocyte': [], 
    'lymphocytic_blast': [], 
    'lymphoidocyte': [], 
    'macrophage': [], 
    'megakaryocyte': [], 
    'micromegakaryocyte': [], 
    'mitosis': [], 
    'monoblast': [], 
    'monocyte': [], 
    'monocytic_blast': [], 
    'myeloblast': [], 
    'myelocytic_blast': [], 
    'neutrophil_extracellular_trap': [], 
    'neutrophilic_band': [], 
    'neutrophilic_metamyelocyte': [], 
    'neutrophilic_myelocyte': [], 
    'orthochromatic_erythroblast': [], 
    'phagocytosis': [], 
    'plasma_cell': [], 
    'polychromatic_erythroblast': [], 
    'proerythroblast': [], 
    'prolymphocyte': [], 
    'promegakaryocyte': [], 
    'promonocyte': [], 
    'promyelocyte': [], 
    'pseudo_gaucher_cell': [], 
    'segmented_basophil': [], 
    'segmented_eosinophil': [], 
    'segmented_neutrophil': [], 
    'smudge_cell': [], 
    'spicule': [], 
    'technically_unfit': [], 
    'thrombocyte': [], 
    'thrombocyte_aggregate': [], 
    'unknown_blast': []
}

