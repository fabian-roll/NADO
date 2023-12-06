import os
import numpy as np
import pandas as pd
import gudhi
import json
from sklearn.decomposition import PCA
from fvec_features import *

pathAnnotations = 'data'
pathNerves = 'nerves'
pathFacevecs = 'features'

os.makedirs('features', exist_ok=True)

# read in dictionaries with data file name information
with open('nerveFileNames.json', 'r') as fp:
    nerveFileNames = json.load(fp)
with open('ovuleIDs.json', 'r') as fp:
    ovuleIDs = json.load(fp)

# read in geometry spreadsheets
df_C = pd.read_excel('data/Cardamine_2-III-to-3-VI_cell_attributes_withtissueandparent_labels.xlsx')
df_A = pd.read_excel('data/Arabidopsis Wild-type_All_Stages_High-quality_Long_File_Format.xlsx')

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

        # We exclude this because of missing data: 
        # many chalaza cells have neighbors in the nerve with no tissue type given
        if file == '534_parents.csv':
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
        species=pathSplit[1].split('_')[2]
        pathNerve = pathNerves + '/' + species + '/' + pathSplit[2] + '/' + nerveFileNames[file].split('.')[0] + '.csv'
        st = gudhi.SimplexTree()
        with open(pathNerve, 'r') as f:
            lines = f.readlines()
        for line in lines:
            data = line.split(',')
            st.insert(list(map(int, [element for element in data])))
        pathFacevec = species + '/' + pathSplit[2] + '/' + file.split('.')[0]
        
        
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

species = ['Arabidopsis', 'Cardamine']

growth_stages = ['2-III', '2-IV', '2-V', '3-I', '3-II', '3-III', '3-IV', '3-V', '3-VI']

# The tissues we consider are:
# chalaza, outer integument, inner integument, funiculus, nucellus, and the whole ovule
tissue_choices = ['ch', 'oi', 'ii', 'fu', 'nu', 'all-cells']

subcomplex_labels = {'ch' : [6, 10],
                     'oi' : [1, 2],
                     'ii' : [3, 4],
                     'fu' : [7],
                     'nu' : [5],
                     'all-cells' : [1,2,3,4,5,6,7,8,10,14]}

# for specific tissues, we compute face-vectors in the subcomplex of the nerve
# on vertices only of that tissue.
# When we compute feature vectors for the whole ovule, we compute
# face-vectors in the full nerve
subcomplex_choices = {'ch' : 'subcomplex',
                      'oi' : 'subcomplex',
                      'ii' : 'subcomplex',
                      'fu' : 'subcomplex',
                      'nu' : 'subcomplex',
                      'all-cells' : 'full-nerve'}

# We exclude low-volume gaps (which are not cells) when computing f-vectors
volume_choice = 'no-gaps'

##################################
# Compute and save feature vectors
##################################

for tissue in tissue_choices:
    sl = subcomplex_labels[tissue]
    fl = sl + [i * 100 for i in sl]

    # Compute feature vectors
    
    sc = subcomplex_choices[tissue]
    if sc == 'subcomplex':
        features, simplicial_complex_ids, sorted_facevecs = fv_features_subcomplex(labeledSimplicialComplexes, sl, fl)
    if sc == 'full-nerve':
        features, simplicial_complex_ids, sorted_facevecs = fv_features(labeledSimplicialComplexes, sl)

    # Get lower-dimensional representations using PCA and save feature vectors

    for gs in growth_stages:

        # get indices for the given growth stage
        indices = []
        for i in simplicial_complex_ids.keys():
            id_gs = simplicial_complex_ids[i].split('/')[1]
            if id_gs == gs:
                indices.append(i)

        comparison_features = features[indices, :]

        # apply PCA
        pca = PCA()
        pca_embedding = pca.fit_transform(comparison_features)

        # save feature vectors
        species_indices = {}
        for s in species:
            species_indices[s] = []
            for i, index in enumerate(indices):
                id = simplicial_complex_ids[index]
                if id[0] == s[0]:
                    species_indices[s].append(i)

            feature_vector_id = '_'.join([tissue, volume_choice, sc, s, gs])
            file_name = pathFacevecs + '/' + feature_vector_id + '_features.csv'
            np.savetxt(file_name, pca_embedding[species_indices[s],:], '%1f', delimiter=',')