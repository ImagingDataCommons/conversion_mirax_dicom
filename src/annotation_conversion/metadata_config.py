import pydicom
import pydicom.dataelem 
import highdicom as hd
from pydicom.sr.coding import Code
from pydicom.sr.codedict import codes
from typing import Tuple
from git_utils import get_git_remote_url, get_git_commit_hash


# Basic Metadata
series_description_roi_anns = 'Monolayer regions of interest for cell classification'
manufacturer = 'University Hospital Erlangen and Fraunhofer MEVIS'
manufacturer_model_name = 'BMDeep data conversion'
software_versions = get_git_remote_url(simplify=True)
device_serial_number = get_git_commit_hash()
algorithm_type = hd.ann.AnnotationGroupGenerationTypeValues.MANUAL


# Metadata functions
def series_description_cell_anns(annotation_session: str) -> str: 
    if annotation_session == 'consensus': 
        return f'Consensus: cell bounding boxes with cell type labels'
    elif annotation_session == 'detection-only':
        return f'Unlabeled cell bounding boxes'
    else: 
        return f'Session {annotation_session}: Cell bounding boxes with cell type labels'

def add_clinical_trial_series_id(annotation_session: str) -> Tuple[pydicom.dataelem.DataElement]:
    return (pydicom.dataelem.DataElement(0x00120071, 'LO', annotation_session),
    pydicom.dataelem.DataElement(0x00120060, 'LO', ''))


# Ontology codes 
code_physical_object = Code('260787004', 'SCT', 'Physical object')
code_anatomical_structure = Code('91723000', 'SCT', 'Anatomical structure')
code_morphologic_abnormality = Code('49755003', 'SCT', 'Morphologically abnormal structure')
code_spatial_relational_concept = Code('309825002', 'SCT', 'Spatial and relational concepts')

roi_labels = {
    'region_of_interest': [code_spatial_relational_concept, Code('111099', 'DCM', 'Selected region')],
}

cell_labels = {
    'artifact': [code_physical_object, Code('47973001', 'SCT', 'Artifact')], 
    'basophilic_band': [code_anatomical_structure, Code('LP65588-3', 'LN', 'Basophils.band form')], 
    'basophilic_erythroblast': [code_anatomical_structure, Code('464005', 'SCT', 'Basophilic erythroblast')], 
    'basophilic_metamyelocyte': [code_anatomical_structure, Code('63369000', 'SCT', 'Basophilic metamyelocyte')],
    'basophilic_myelocyte': [code_anatomical_structure, Code('17295002', 'SCT', 'Basophilic myelocyte')], 
    'damaged_cell': [code_morphologic_abnormality, Code('37782003', 'SCT', 'Damage')], 
    'degranulated_neutrophilic_metamyelocyte': [code_anatomical_structure, Code('C37174', 'NCIt', 'Neutrophil with Cytoplasmic Hypogranularity')], 
    'degranulated_neutrophilic_myelocyte': [code_anatomical_structure, Code('250292003', 'SCT', 'Hypogranular white blood cell')],
    'eosinophilic_band': [code_anatomical_structure, Code('LP65365-6', 'LN', 'Eosinophils.band form')],
    'eosinophilic_metamyelocyte': [code_anatomical_structure, Code('80036001', 'SCT', 'Eosinophilic metamyelocyte')],
    'eosinophilic_myelocyte': [code_anatomical_structure, Code('90961003', 'SCT', 'Eosinophilic myelocyte')],
    'erythrocyte': [code_anatomical_structure, Code('41898006', 'SCT', 'Erythrocyte')],
    'giant_platelet': [code_morphologic_abnormality, Code('44687006', 'SCT', 'Giant platelet')],
    'lymphoid_precursor_cell': [code_anatomical_structure, Code('127910003', 'SCT', 'Lymphoid precursor cell') ],
    'lymphocyte': [code_anatomical_structure, Code('56972008', 'SCT', 'Lymphocyte')],
    'lymphocytic_blast': [code_anatomical_structure, Code('15433008', 'SCT', 'Lymphoblast')],
    'lymphoidocyte': [code_anatomical_structure, Code('C12847', 'NCIt', 'Reactive Lymphocyte')],
    'macrophage': [code_anatomical_structure, Code('58986001', 'SCT', 'Macrophage')],
    'megakaryocyte': [code_anatomical_structure, Code('23592000', 'SCT', 'Megakaryocyte')],
    'micromegakaryocyte': [code_anatomical_structure, Code('33196003', 'SCT', 'Micromegakaryocyte')],
    'mitosis': [code_anatomical_structure, Code('75167008', 'SCT', 'Mitotic cell')],
    'immature_monocyte': [code_anatomical_structure, Code('C13120', 'NCIt', 'Immature Monocyte')],
    'monocyte': [code_anatomical_structure, Code('55918008', 'SCT', 'Monocyte')],
    'monocytic_blast': [code_anatomical_structure, Code('53945006', 'SCT', 'Monoblast')],
    'myeloid_precursor_cell': [code_anatomical_structure, Code('127914007', 'SCT', 'Myeloid precursor cell')],
    'myelocytic_blast': [code_anatomical_structure, Code('15622002', 'SCT', 'Myeloblast')],
    'neutrophil_extracellular_trap': [code_anatomical_structure, Code('C180931', 'NCIt', 'Neutrophil Extracellular Trap')],
    'neutrophilic_band': [code_anatomical_structure, Code('702697008', 'SCT', 'Band neutrophil')],
    'neutrophilic_metamyelocyte': [code_anatomical_structure, Code('50134008', 'SCT', 'Neutrophilic metamyelocyte')],
    'neutrophilic_myelocyte': [code_anatomical_structure, Code('4717004', 'SCT', 'Neutrophilic myelocyte')],
    'orthochromatic_erythroblast': [code_anatomical_structure, Code('113334004', 'SCT', 'Orthochromic erythroblast')],
    'phagocytosis': [code_anatomical_structure, Code('56639005', 'SCT', 'Phagocytosis')],
    'plasma_cell': [code_anatomical_structure, Code('113335003', 'SCT', 'Plasma cell')],
    'polychromatic_erythroblast': [code_anatomical_structure, Code('16779009', 'SCT', 'Polychromatophilic erythroblast')],
    'proerythroblast': [code_anatomical_structure, Code('16671004', 'SCT', 'Proerythroblast')],
    'prolymphocyte': [code_anatomical_structure, Code('19394005', 'SCT', 'Prolymphocyte')],
    'promegakaryocyte': [code_anatomical_structure, Code('50284009', 'SCT', 'Promegakaryocyte')],
    'promonocyte': [code_anatomical_structure, Code('1075005', 'SCT', 'Promonocyte')],
    'promyelocyte': [code_anatomical_structure, Code('43446009', 'SCT', 'Promyelocyte')],
    'pseudo_gaucher_cell': [code_anatomical_structure, Code('59870003', 'SCT', 'Gaucher-like cell')],
    'segmented_basophil': [code_anatomical_structure, Code('30061004', 'SCT', 'Basophil, segmented')],
    'segmented_eosinophil': [code_anatomical_structure, Code('14793004', 'SCT', 'Eosinophil, segmented')],
    'segmented_neutrophil': [code_anatomical_structure, Code('80153006', 'SCT', 'Segmented neutrophil')],
    'smudge_cell': [code_morphologic_abnormality, Code('34717007', 'SCT', 'Smudge cell')],
    'spicule': [code_anatomical_structure, Code('C82998', 'NCIt', 'Spicule')],
    'technically_unfit': [code_spatial_relational_concept, Code('111235', 'DCM', 'Unusable - Quality renders image unusable')],
    'thrombocyte': [code_anatomical_structure, Code('16378004', 'SCT', 'Thrombocyte')],
    'thrombocyte_aggregate': [code_anatomical_structure, Code('60649002', 'SCT', 'Platelet aggregation')],
    'unknown_blast': [code_anatomical_structure, Code('312256009', 'SCT', 'Blast cell')], 
    'no_consensus_found': [code_anatomical_structure, Code('414387006', 'SCT', 'Structure of haematological system')],
    'haematological_structure': [code_anatomical_structure, Code('414387006', 'SCT', 'Structure of haematological system')]
}

code_cell_identifier = Code('0010197', 'EFO', 'single cell identifier')
code_roi_identifier = Code('111030', 'DCM', 'Image Region')
code_ref_to_roi_identifier = codes.DCM.ReferencedRegionOfInterestIdentifier
unit_identifier = codes.UCUM.NoUnits

roi_color_code ='#ffffff'
cell_color_codes = {
    'artifact': '#dadada',
    'basophilic_band': '#f9ae37',
    'basophilic_erythroblast': '#fc8ea2',
    'basophilic_metamyelocyte': '#f9b84d',
    'basophilic_myelocyte': '#fac063',
    'damaged_cell': '#d7d2d1',
    'degranulated_neutrophilic_metamyelocyte': '#d5ccc9',
    'degranulated_neutrophilic_myelocyte': '#d6cecc',
    'eosinophilic_band': '#f9ae37',
    'eosinophilic_metamyelocyte': '#f9b84d',
    'eosinophilic_myelocyte': '#fac063',
    'erythrocyte': '#fa5674',
    'giant_platelet': '#d7d4d2',
    'lymphoid_precursor_cell': '#94b8cf',
    'lymphocyte': '#699cbb',
    'lymphocytic_blast': '#c8b8b7',
    'lymphoidocyte': '#d8d6d5', 
    'macrophage': '#f58355',
    'megakaryocyte': '#fbc783',
    'micromegakaryocyte': '#d7d2d0',
    'mitosis': '#d6cecd',
    'immature_monocyte': '#f9b195',
    'monocyte': '#f6926b',
    'monocytic_blast': '#c9bdbb',
    'myeloid_precursor_cell': '#fcc090',
    'myelocytic_blast': '#cbc1c0',
    'neutrophil_extracellular_trap': '#d4cbc9',
    'neutrophilic_band': '#f9ae37',
    'neutrophilic_metamyelocyte': '#f9b84d',
    'neutrophilic_myelocyte': '#fac063',
    'orthochromatic_erythroblast': '#fa6983',
    'phagocytosis': '#d3c8c5',
    'plasma_cell': '#538eb2',
    'polychromatic_erythroblast': '#fb7b93',
    'proerythroblast': '#fca1a3',
    'prolymphocyte': '#7eaac5',
    'promegakaryocyte': '#fbcf95',
    'promonocyte': '#f8a280',
    'promyelocyte': '#fbca79',
    'pseudo_gaucher_cell': '#d6d0ce', 
    'segmented_basophil': '#f8a31e',
    'segmented_eosinophil': '#f8a31e',
    'segmented_neutrophil': '#f8a31e',
    'smudge_cell': '#d9d8d7',
    'spicule': '#d2c4c1',
    'technically_unfit': '#d6cfce',
    'thrombocyte': '#fabf71',
    'thrombocyte_aggregate': '#d2c4c1',
    'unknown_blast': '#c6b4b2',
    'no_consensus_found': '#d4cac7', # color taken from 'unsure' in BMDeep color codes
    'haematological_structure': '#ffffff' # color white for general structure (unlabeled)
}

