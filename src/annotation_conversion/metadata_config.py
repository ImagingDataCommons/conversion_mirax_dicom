import highdicom as hd
from pydicom.sr.coding import Code
from git_utils import get_git_remote_url, get_git_commit_hash


# Basic Metadata
series_description_roi_anns = 'Regions of interest for cell classification (monolayer)'
series_description_cell_anns = 'Cell bounding boxes with cell type labels'
manufacturer = 'University Hospital Erlangen and Fraunhofer MEVIS'
manufacturer_model_name = 'BMDeep data conversion'
software_versions = get_git_remote_url(simplify=True)
device_serial_number = get_git_commit_hash()
algorithm_type = hd.ann.AnnotationGroupGenerationTypeValues.MANUAL

# Labels 
code_physical_object = Code('260787004', 'SCT', 'Physical object')
code_anatomical_structure = Code('91723000', 'SCT', 'Anatomical structure')
code_morphologic_abnormality = Code('49755003', 'SCT', 'Morphologically abnormal structure')
code_spatial_relational_concept = Code('309825002', 'SCT', 'Spatial and relational concepts')

roi_labels = {
    'monolayer': [code_spatial_relational_concept, Code('111099', 'DCM', 'Selected region')],
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
    'no_consensus_found': [code_anatomical_structure, Code('414387006', 'SCT', 'Structure of haematological system')]
}