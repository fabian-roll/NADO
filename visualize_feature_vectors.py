import numpy as np
import pandas as pd
import os
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

pathFacevecs = 'features'
pathPlots = 'scatter_visualizations'

os.makedirs('scatter_visualizations', exist_ok=True)

species = ['Arabidopsis', 'Cardamine']

growth_stage = '3-VI'

# The tissues we consider are:
# chalaza, outer integument, inner integument, funiculus, nucellus, and the whole ovule
tissue_choices = ['ch', 'oi', 'ii', 'fu', 'nu', 'all-cells']

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

# We exclude low-volume gaps (when computing
volume_choice = 'no-gaps'

# Arabidopsis samples are in blue, Cardamine in orange
species_to_color = {'Arabidopsis' : 'blue', 
                    'Cardamine' : 'orange'}

marker_size=20

# titles for plots
plot_titles = {'all-cells' : 'Ovule 3-VI',
            'oi' : 'Outer Integument 3-VI',
            'ii' : 'Inner Integument 3-VI',
            'ch' : 'Chalaza 3-VI',
            'nu' : 'Nucellus 3-VI',
            'fu' : 'Funiculus 3-VI'}

##################################
# Compute and save feature vectors
##################################

for tissue in tissue_choices:

    # load feature vectors

    sc = subcomplex_choices[tissue]
    features = {}

    for s in species:
        feature_vector_id = '_'.join([tissue, volume_choice, sc, s, growth_stage])
        file_name = pathFacevecs + '/' + feature_vector_id + '_features.csv'
        features[s] = np.genfromtxt(file_name, dtype=np.float64, delimiter=',')

    all_features = np.concatenate((features['Arabidopsis'], features['Cardamine']), axis=0)

    # apply PCA

    pca = PCA(n_components=2)
    pca_embedding = pca.fit_transform(all_features)

    n = features['Arabidopsis'].shape[0] # number of Arabidopsis points
    m = features['Cardamine'].shape[0] # number of Cardamine points

    Arabidopsis_points = pca_embedding[0:n, :]
    Cardamine_points = pca_embedding[n:n+m, :]

    # plot

    fig, ax = plt.subplots()
    title = plot_titles[tissue]
    plt.title(title)

    # plot Arabidopsis points
    ax.scatter(Arabidopsis_points[:,0],
               Arabidopsis_points[:,1],
               s=marker_size,
               c=species_to_color['Arabidopsis'], 
               label='Arabidopsis')
    
    # plot Cardamine points
    ax.scatter(Cardamine_points[:,0],
               Cardamine_points[:,1],
               s=marker_size,
               c=species_to_color['Cardamine'], 
               label='Cardamine')
    
    ax.legend()
    fig_name = '_'.join([tissue, volume_choice, sc, growth_stage, 'scatter'])
    plt.savefig(pathPlots + '/' + fig_name + '.pdf')
    plt.close()