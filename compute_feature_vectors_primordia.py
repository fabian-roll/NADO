import os
import pandas as pd
import numpy as np
import gudhi
from sklearn.decomposition import PCA
import math
from fvec_features import *


path_features = 'features'

# print information to a log file
log_file = 'primordia_compute_feature_vectors_log.txt'
log = open(log_file, 'w')

# read geometry spreadsheets
geom_C = pd.read_excel(
         'data/topological_analysis_Cardamine_data/1-I to 2-II/Cardamine_1-I_to_2-II_cell_attributes_parentlabels.xlsx'
         )
geom_A = pd.read_excel(
         'data/topological_analysis_Arabidopsis_data/1-I to 2-II/Arabidopsis primordia_cellvolume.xlsx'
         )

# get ovule information
ovule_IDs = []

for ovule_ID in pd.unique(geom_A['ovule_id']):
    growth_stage = geom_A[geom_A['ovule_id'] == ovule_ID]['Stage '].iloc[0]
    ovule_IDs.append((ovule_ID, 'Arabidopsis', growth_stage))

for ovule_ID in pd.unique(geom_C['Ovule_ID']):
    if not pd.isnull(ovule_ID):
        growth_stage = geom_C[geom_C['Ovule_ID'] == ovule_ID]['Ovule_Stage'].iloc[0]
        ovule_IDs.append((ovule_ID, 'Cardamine', growth_stage))

# this file contains all ovule IDs,
# together with their genotype and growth stage
#df_primordia_IDs = pd.read_csv('data/primordia_IDs.csv')
#ovuleIDs = df_primordia_IDs['Ovule_ID']

# Create dictionaries that map ovule IDs to 
# the location of the corresponding nerve file,
# and the location of the corresponding parents file,
# which contains tissue IDs.

#genotype_to_species = {'ChiOX':'Cardamine', 'AthCol-0':'Arabidopsis'}

nerve_locations = {}
parent_locations = {}
for (id, species, growth_stage) in ovule_IDs:

    # get growth stage
    # gs = df_primordia_IDs[df_primordia_IDs['Ovule_ID'] 
    #                       == ovuleID]['Ovule_Stage'].iloc[0]
    
    # get leading number in the id, as a string
    if isinstance(id, str):
        id_num = id.split('_')[0]
    else:
        id_num = str(id)

    #IDnum = ovuleID.split('_')[0]

    # assign nerve location
    if species == 'Arabidopsis':
        path = '/'.join(['nerves', species, '1-I to 2-II', growth_stage])
    if species == 'Cardamine':
        path = '/'.join(['nerves', species, '1-I to 2-II'])
    nerve_locations[id] = path + '/' + id_num + '_segmentation.csv'

    # assign parent location
    if id_num == '1950': # the file labels are different in this case
        assert species == 'Cardamine'
        path = '/'.join(['data', 'topological_analysis_Cardamine_data', '1-I to 2-II'])
        part_label = id.split('_')[1]
        parent_locations[id] = (path + '/' 
                                + id_num + '_' + part_label 
                                + '_parents.csv'
        )
    else:
        if species == 'Arabidopsis':
            path = '/'.join(['data', 'topological_analysis_Arabidopsis_data', '1-I to 2-II', growth_stage])
        if species == 'Cardamine':
            path = '/'.join(['data', 'topological_analysis_Cardamine_data', '1-I to 2-II'])
        parent_locations[id] = path + '/' + id_num + '_parents.csv'


#############################################################
# read in data to create list of labeled simplicial complexes
# marking low-volume gaps by multiplying their label by 100
#############################################################

possible_parent_label_sets = [
    set([1,2,3]),
    set([11,12,13]),
    set([21,22,23]),
    set([31,32,33]),
    set([41,42,43]),
    set([51,52,53]),
    set([61,62,63]),
    set([71,72,73])
]

# For these ovules, 
# we will take the tissue labels from the geometry spreadsheet,
# since the labels in the parents file disagree 
# with the labels in the geometry spreadsheet, or are missing
geom_label_ovules = ['786_E', '589_B', '601_B', '783_E']
label_from_geom = {'L1':1, 'L2':2, 'L3':3}

labeled_simplicial_complexes = []

for (id, species, growth_stage) in ovule_IDs:

    print(id, file=log)

    # # for now we exclude this,
    # # since greyscale values don't correspond to segmentations
    # if ovuleID[:3] == '396':
    #     continue

    # # get ID used in the geometry spreadsheet
    # if ovuleID in geometry_data_ovuleIDs:
    #     geom_ovuleID = geometry_data_ovuleIDs[ovuleID]
    # else:
    #     geom_ovuleID = ovuleID

    # Read parents file
    with open(parent_locations[id], 'r') as f:
        lines = f.readlines()
    parent_labels = {}
    for line in lines[1:]:
        (x,y) = line.split(',')
        parent_labels[int(x)] = int(y)

    # Now we will find the vertex labels.
    # For the vertices of the nerve that correspond to cells of this ovule, 
    # we label them with their tissue type.
    # Low-volume gaps are marked by multiplying this label by 100.

    vertex_labels = {}

    # For Arabidopsis, low-volume gaps are already excluded
    # from the geometry spreadsheet.
    if species == 'Arabidopsis':

        # get the cells from the geometry spreadsheet
        cells = geom_A.loc[geom_A['ovule_id'] == id]

        # get the cell ids and the cell type labels 
        # from the geometry spreadsheet
        cell_ids = list(cells['cell_id'])
        cell_types = cells['cell_type']

    # For Cardamine, we must exclude items with volume <= 30 um^3
    if species == 'Cardamine':

        # get the cells from the geometry spreadsheet
        items = geom_C.loc[geom_C['Ovule_ID'] == id]
        cells = items.loc[items['Geometry.Volume'] >= 30]

        # get the cell ids and the cell type labels 
        # from the geometry spreadsheet
        cell_ids = list(cells['Label'])
        cell_types = cells['ParentLabel']

    # get the cell parent labels from the parents file
    missing_parents_label = 0
    cell_parent_labels = []
    for cell_id in cell_ids:
        if cell_id in parent_labels:
            cell_parent_labels.append(parent_labels[cell_id])
        else:
            missing_parents_label += 1

    if missing_parents_label > 0:
        print('missing parents label : ', missing_parents_label, file=log)

    # check that cell types are as expected
    if not set(cell_types) == set(['L1', 'L2', 'L3']):
        print('Cell types : ', set(cell_types), file=log)

    # check that parent labels are as expected
    if not set(cell_parent_labels) in possible_parent_label_sets:
        print('Parent labels : ', set(cell_parent_labels), file=log)

    # check that the final digits of the cell type labels
    # from the geometry spreadsheet and the parents file agree
    for i, cell_type in enumerate(cell_types):
        if len(cell_parent_labels) <= i:
            print('Less parent labels than cell types', file=log)
            break
        elif not str(cell_type)[-1] == str(cell_parent_labels[i])[-1]:
            print('Geometry spreadsheet and parents file disagree!', file=log)
            break

    # label the cells
            
    # For these ovules, we take the labels from the geometry spreadsheet.
    # Note that this code uses the structure of the Arabidopsis geometry sheet
    # since all of these ovules are Arabidopsis. 
    if id in geom_label_ovules:
        for i in range(cells.shape[0]):
            cell_id = cells.iloc[i,1]
            cell_type = label_from_geom[cells.iloc[i,2]]
            vertex_labels[cell_id] = cell_type
    
    # For these ovules, we take the labels from the parents file
    else:
        for cell_id in cell_ids:
            vertex_labels[cell_id] = parent_labels[cell_id]

    # count cells
    counts = cell_types.value_counts()
    print(counts, file=log)

    # get low-volume gaps and label them,
    # as long as we got the cell labels from the parents file
    if not(id in geom_label_ovules):
        count = 0
        for item in parent_labels.keys():

            # if the parent label of the item 
            # is one of the cell labels for this ovule,
            # but the item is not a cell  
            if (parent_labels[item] in set(cell_parent_labels) and
                (not item in cell_ids)):
                vertex_labels[item] = int(parent_labels[item] * 100)
                count += 1    
        print('Number of gaps : ', count, file=log)

    # Read nerve file and create gudhi simplex tree
    st = gudhi.SimplexTree()
    with open(nerve_locations[id], 'r') as f:
        lines = f.readlines()
    for line in lines:
        data = line.split(',')
        st.insert([int(element) for element in data])

    # Check that all cells and gaps are in the simplicial complex
    vertices = set()
    for v in st.get_skeleton(0):
        vertices.add(v[0][0])
    labeled_vertices = set(vertex_labels.keys())
    if not labeled_vertices.issubset(vertices):
        print('Not all labeled vertices are in the simplex tree!', file=log)
        x = labeled_vertices.intersection(vertices)
        n = len(x)
        print('Only ', n, 'labeled vertices are in the simplex tree', file=log)

    # Create id for the labeled simplicial complex
    sc_id = '_'.join([species, growth_stage, str(id)])

    labeled_simplicial_complexes.append((sc_id, st, vertex_labels))

##################################################
# Specify which sets of feature vectors to compute
##################################################
    
species_choices = ['Arabidopsis', 'Cardamine']

growth_stages = ['1-I', '1-II', '2-I', '2-II']

tissue_choices = ['L1', 'L2', 'L3', 'all-cells']

subcomplex_labels = {'L1' : [1, 11, 21, 31, 41, 51, 61, 71],
                     'L2' : [2, 12, 22, 32, 42, 52, 62, 72],
                     'L3' : [3, 13, 23, 33, 43, 53, 63, 73],
                     'all-cells' : []}
for tissue in ['L1', 'L2', 'L3']:
    subcomplex_labels['all-cells'].extend(subcomplex_labels[tissue])

# Verify that, for each labeled simplicial complex,
# the set of vertex labels contains only one L1 (resp. L2,L3) label
print('Verifying vertex labels contain only one L1 (resp. L2,L3) label...', 
      file=log)
for (sc_id, st, vertex_labels) in labeled_simplicial_complexes:
    label_set = set(vertex_labels.values())
    for tissue in ['L1', 'L2', 'L3']:
        count = 0
        for label in subcomplex_labels[tissue]:
            if label in label_set:
                count += 1
        if not count == 1:
            print('For : ', sc_id, tissue, ' found ', count, file=log)
            print(label_set, file=log)

# for specific tissues, we compute face-vectors in the subcomplex of the nerve
# on vertices only of that tissue.
# When we compute feature vectors for the whole ovule, we compute
# face-vectors in the full nerve
subcomplex_choices = {'L1' : 'subcomplex',
                      'L2' : 'subcomplex',
                      'L3' : 'subcomplex',
                      'all-cells' : 'subcomplex'}

# We exclude low-volume gaps (which are not cells) when computing f-vectors
volume_choice = 'no-gaps'

##################################
# Compute and save feature vectors
##################################

print('Computing feature vectors...', file=log)

for tissue in tissue_choices:

    print(tissue, file=log)

    sl = subcomplex_labels[tissue]
    fl = sl + [i * 100 for i in sl]

    # Compute feature vectors
    sc = subcomplex_choices[tissue]
    if sc == 'subcomplex':
        features, sc_ids, fvecs = fv_features_subcomplex(
                                  labeled_simplicial_complexes, sl, fl)
    if sc == 'full-nerve':
        features, sc_ids, fvecs = fv_features(
                                  labeled_simplicial_complexes, sl)

    print('feature shape : ', features.shape, file=log)

    # check for rows of zeroes
    for i in range(features.shape[0]):
        S = np.sum(features[i,:])
        if not math.isclose(S, 1, rel_tol=1e-3):
            sc_id = sc_ids[i]
            growth_stage = sc_id.split('_')[1]
            assert tissue == 'L3'
            assert growth_stage == '1-I'

    # Get lower-dimensional representations using PCA and save feature vectors

    for gs in growth_stages:

        if not(tissue == 'L3' and gs == '1-I'):

            print(gs, file=log)

            # get indices for the given growth stage
            indices = []
            for i in sc_ids.keys():
                id_gs = sc_ids[i].split('_')[1]
                if id_gs == gs:
                    indices.append(i)

            comparison_features = features[indices, :]

            print('Comparison features shape : ', 
                comparison_features.shape, file=log)

            # apply PCA
            pca = PCA()
            pca_embedding = pca.fit_transform(comparison_features)

            # save feature vectors
            species_indices = {}
            for s in species_choices:
                species_indices[s] = []
                for i, index in enumerate(indices):
                    id = sc_ids[index]
                    if id[0] == s[0]:
                        species_indices[s].append(i)

                print('Number of ', s, ' samples : ', len(species_indices[s]), 
                    file=log)

                feature_id = '_'.join([tissue, volume_choice, sc, s, gs])
                file_name = path_features + '/' + feature_id + '_features.csv'
                np.savetxt(file_name, 
                        pca_embedding[species_indices[s],:], 
                        '%1f', delimiter=',')