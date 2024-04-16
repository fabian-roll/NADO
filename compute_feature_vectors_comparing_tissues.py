import numpy as np
import json
import pandas as pd
import gudhi
import os
from sklearn.decomposition import PCA

from fvec_features import *

pathAnnotations = 'data'
pathNerves = 'nerves'
pathFacevecs = 'features/comparing_tissues'

os.makedirs('features/comparing_tissues', exist_ok=True)

# read in dictionaries with data file name information
with open('nerveFileNames.json', 'r') as fp:
    nerveFileNames = json.load(fp)
with open('ovuleIDs.json', 'r') as fp:
    ovuleIDs = json.load(fp)

###############################
# read in geometry spreadsheets
###############################

df_C = pd.read_excel('Ovule/geometry_data/Chi_cell_attributes_2-III_to_3-VI_exclvol_less_than_30_withlabels_exclplacenta_final.xlsx')
df_A = pd.read_excel('Ovule/geometry_data/Arabidopsis Wild-type_All_Stages_High-quality_Long_File_Format.xlsx')

#############################################################
# read in data to create list of labeled simplicial complexes
# marking low-volume gaps by multiplying their label by 100
#############################################################

labeledSimplicialComplexes = []

for path, subdirs, files in os.walk(pathAnnotations):
    for file in files:
        if (not file.endswith('.csv')):
            continue

        # we don't have geometry information,
        # so we exclude these files
        if (not file in ovuleIDs):
            continue

        # Teja said to exclude this
        if file == '1663_parents_v6.csv': 
            continue
        # We exclude this because of missing data: 
        # many chalaza cells have neighbors in the nerve with no tissue type given
        if file == '534_mesh_parents.csv':
            continue
        # We exclude this because the grayscale values in the segmentation do not encode cells
        if file == '436_parents.csv': 
            continue

        pathAnnotation = os.path.join(path, file)
        with open(pathAnnotation, 'r') as f:
            lines = f.readlines()
        vertexLabels = {}
        for i in range(1, len(lines)):
            data = lines[i].split(',')
            vertexLabels[int(data[0])] = int(data[1])

        pathSplit = path.split('/')
        pathNerve = pathNerves + '/' + pathSplit[2] + '/' + pathSplit[4] + '/' + nerveFileNames[file].split('.')[0] + '.csv'
        st = gudhi.SimplexTree()
        with open(pathNerve, 'r') as f:
            lines = f.readlines()
        for line in lines:
            data = line.split(',')
            st.insert(list(map(int, [element for element in data])))
        pathFacevec = pathSplit[2] + '/' + pathSplit[4] + '/' + file.split('.')[0]

        # specify low-volume gaps by multiplying their label by 100
        (ovule_id, species) = ovuleIDs[file]
        if species == 'C':
            labels = list(df_C.loc[(df_C['Sample'] == ovule_id)]['Label'])
        if species == 'A':
            labels = list(df_A.loc[(df_A['ovule_id'] == ovule_id)]['cell_id'])

        for v in vertexLabels.keys():
            if (not v in labels):
                vertexLabels[v] = int(vertexLabels[v] * 100)

        labeledSimplicialComplexes.append((pathFacevec, st, vertexLabels))

#########################################################
# Compute feature vectors for chalaza vs outer integument
#########################################################

group_labels = [(6,10), (1,2)]
facevec_labels = {(6,10) : [6, 10, 600, 1000], 
                  (1,2) : [1, 2, 100, 200]}
tissue_names = {(6,10) : 'ch', (1,2) : 'oi'}

# compute features
features, simplicial_complex_ids, sorted_facevecs = fv_features_subcomplex_groups(labeledSimplicialComplexes, group_labels, facevec_labels)

n = len(simplicial_complex_ids.keys()) # number of simplicial complexes
simplicial_complex_ids_list = [simplicial_complex_ids[i] 
                               for i in range(n)]

# we compute face-vectors in the subcomplex of the nerve
# not in the full nerve
subcomplex_choice = 'subcomplex'

# we excluded low-volume gaps when computing labeledSimplicialComplexes
volume_choice = 'no-gaps'

species = ['Arabidopsis', 'Cardamine']
growth_stages = ['2-III', '2-IV', '2-V', 
                 '3-I', '3-II', '3-III', '3-IV', '3-V', '3-VI']

# apply PCA and save features

for s in species:
    for growth_stage in growth_stages:

        # get indices for the given growth stages and species
        indices = []
        for i, id in enumerate(simplicial_complex_ids_list):
            id_growth_stage = id.split('/')[1]
            id_s = id.split('/')[0]
            if (id_growth_stage == growth_stage and id_s == s):
                indices.append(i)

        current_features = {}
        for tissue_label in group_labels:
            current_features[tissue_label] = features[tissue_label][indices, :]

        comparison_features = np.concatenate(
            [current_features[tissue_label] for tissue_label in group_labels], 
            axis=0
            )

        # apply PCA
        pca = PCA()
        pca_embedding = pca.fit_transform(comparison_features)

        # save processed feature vectors
        n = len(indices)
        for i, tissue_label in enumerate(group_labels):

            tissue_name = tissue_names[tissue_label]
            feature_vector_id = '_'.join([tissue_name, volume_choice, 
                                          subcomplex_choice, s, growth_stage])
            file_name = pathFacevecs + '/' + feature_vector_id + '_features.csv'
            np.savetxt(file_name, 
                       pca_embedding[i*n:(i+1)*n, :], 
                       '%1f', delimiter=',')

experiment_id = '_'.join(['ch', 'oi', volume_choice, 
                          subcomplex_choice])

# save simplicial_complex_ids to a csv file
file_name = pathFacevecs + '/' + experiment_id + '_simplicial_complex_ids.csv'
x = pd.DataFrame({'file' : simplicial_complex_ids.values()})
x.to_csv(file_name)

# save sorted face vectors to a csv file
file_name = pathFacevecs + '/' + experiment_id + '_sorted_facevecs.csv'
x = pd.DataFrame({'fv' : sorted_facevecs})
x.to_csv(file_name)