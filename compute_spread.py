import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt

pathFacevecs = 'features'

species_choices = ['Arabidopsis', 'Cardamine']

growth_stages = ['2-III', '2-IV', '2-V', 
                 '3-I', '3-II', '3-III', '3-IV', '3-V', '3-VI']

# The tissues we consider are:
# chalaza, outer integument, inner integument, funiculus, and nucellus
tissue_choices = ['ch', 'oi', 'ii', 'fu', 'nu']

subcomplex_choices = {'ch' : 'subcomplex',
                      'oi' : 'subcomplex',
                      'ii' : 'subcomplex',
                      'fu' : 'subcomplex',
                      'nu' : 'subcomplex'}

volume_choice = 'no-gaps'

avg_distances = {}
dimensions = {}

for species in species_choices:
    for growth_stage in growth_stages:
        for tissue in tissue_choices:

            # load feature vectors
            sc = subcomplex_choices[tissue]
            feature_vector_id = '_'.join([tissue, volume_choice, 
                                          sc, species, growth_stage])
            file_name = pathFacevecs + '/' + feature_vector_id + '_features.csv'
            features = np.genfromtxt(file_name, dtype=np.float64, delimiter=',')

            # compute average distance
            distances = []
            for i in range(features.shape[0]):
                for j in range(features.shape[0]):
                    if i < j:
                        distances.append(
                            euclidean(features[i,:], features[j,:])
                            )
            
            avg = sum(distances) / len(distances)
            avg_distances[(species, growth_stage, tissue)] = avg

# plot results
            
# matplotlib settings
plt.rcParams.update({'font.size': 10})
plt.rcParams.update({'xtick.labelsize': 8})
plt.rcParams.update({'ytick.labelsize': 8})

growth_stage_curves = {}
for species in species_choices:
    for tissue in tissue_choices:
        growth_stage_curves[(species, tissue)] = []
        for growth_stage in growth_stages:
            growth_stage_curves[(species, tissue)].append(
                avg_distances[(species, growth_stage, tissue)]
            )

# Plot Arabidopsis
fig, ax = plt.subplots()
plt.xlabel("stage")
plt.ylabel("average pairwise distance (spread)")
plt.title("Arabidopsis")

for tissue in tissue_choices:
    ax.plot(growth_stages, 
            growth_stage_curves[('Arabidopsis', tissue)], 
            label=tissue)

ax.legend()
plt.savefig('arabidopsis-spread.pdf')
plt.close()

# Plot Cardamine
            
fig, ax = plt.subplots()
plt.xlabel("stage")
plt.ylabel("average pairwise distance (spread)")
plt.title("Cardamine")

for tissue in tissue_choices:
    ax.plot(growth_stages, 
            growth_stage_curves[('Cardamine', tissue)], 
            label=tissue)

ax.legend()

plt.savefig('cardamine-spread.pdf')
plt.close()

# Save results to csv

arabidopsis_data = {}
for tissue in tissue_choices:
    arabidopsis_data[tissue] = []
    for growth_stage in growth_stages:
        arabidopsis_data[tissue].append(
            avg_distances[('Arabidopsis', growth_stage, tissue)]
            )

cardamine_data = {}
for tissue in tissue_choices:
    cardamine_data[tissue] = []
    for growth_stage in growth_stages:
        cardamine_data[tissue].append(
            avg_distances[('Cardamine', growth_stage, tissue)]
            )
        
arabidopsis_df = pd.DataFrame(data=arabidopsis_data, index=growth_stages)
cardamine_df = pd.DataFrame(data=cardamine_data, index=growth_stages)

arabidopsis_df.to_csv('arabidopsis_spread.csv')
cardamine_df.to_csv('cardamine_spread.csv')