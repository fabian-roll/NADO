import os
import pandas as pd
import json


pathAnnotations = 'data'
pathNerves = 'nerves'
logFile = 'compute_feature_vectors_json_creation_log.txt'

# for each annotation, the name of the corresponding nerve file
nerveFileNames = {}

for path, subdirs, files in os.walk(pathAnnotations):
    for folder in subdirs:
        folder_path = os.path.join(path, folder)
        files_in_folder = os.listdir(folder_path)
        
        if folder_path.count(os.sep) == 3:
            if files_in_folder[0].endswith('.csv'):
                tiff_name=files_in_folder[1].split('.')[0]
                nerveFileNames[files_in_folder[0]] = tiff_name + '.csv'
            elif files_in_folder[1].endswith('.csv'):
                tiff_name=files_in_folder[0].split('.')[0]
                nerveFileNames[files_in_folder[1]] = tiff_name + '.csv'


# Create json for nerveFileNames
with open('nerveFileNames.json', 'w') as fp:
    json.dump(nerveFileNames, fp)

###############################
# read in geometry spreadsheets
###############################

df_C = pd.read_excel('data/Cardamine_2-III-to-3-VI_cell_attributes_withtissueandparent_labels.xlsx')
df_A = pd.read_excel('data/Wild-type_HQ_source_data.xlsx')

# Create a dictionary that associates to each annotation file name 
# its ovule id from the geometry spreadsheets, if one is available, 
# as well as the species.

growth_stages = ['2-III', '2-IV', '2-V', '3-I', '3-II', '3-III', '3-IV', '3-V', '3-VI']
ovuleIDs = {}

log = open(logFile, 'w') # we print information to a log file
print('Reading geometry spreadsheets', file=log)

# Cardamine

print('Cardamine', file=log)

ovule_ids = df_C['Sample'].unique()

for id in ovule_ids:
    growth_stage = df_C.loc[df_C['Sample'] == id]['Stage'].iloc[0]
    if growth_stage in growth_stages:
        
        # find corresponding annotations file
        id_str = str(id)

        # We do some by hand...
        if id_str == '1783_B':
            ovuleIDs['1783B_parents.csv'] = ('1783_B', 'C')
            continue
        if id_str == '1783a':
            ovuleIDs['1783A_parents.csv'] = ('1783a', 'C')
            continue
        if id_str == '1788a':
            ovuleIDs['1788A_parents.csv'] = ('1788a', 'C')
            continue      


        n = len(id_str)
        matching_annFileName = [item for item in nerveFileNames.keys() if item[0:n] == id_str]
        # if we found a matching annotations file
        if len(matching_annFileName) == 1:
            annFileName = matching_annFileName[0]
            ovuleIDs[annFileName] = (id, 'C')
            print('Matching ' + id_str + ' with ' + annFileName, file=log)
        else:
            print('Did not find a matching annotations file for ' + str(id_str))
            print('Did not find a matching annotations file for ' + str(id_str), file=log)

# Arabidopsis

print('Arabidopsis', file=log)

ovule_ids = df_A['ovule_id'].unique()

for id in ovule_ids:
    growth_stage = df_A.loc[df_A['ovule_id'] == id]['stage'].iloc[0]
    if growth_stage in growth_stages:
        
        # find corresponding annotations file
        id_str = str(id)

        # We do some by hand...
        if id_str == '617_B':
            ovuleIDs['617B_parents.csv'] = ('617_B', 'A')
            continue
        if id_str == '474_C':
            ovuleIDs['474C_parents.csv'] = ('474_C', 'A')
            continue
        if id_str == '424_B':
            ovuleIDs['424B_parents.csv'] = ('424_B', 'A')
            continue
        if id_str == '424_C':
            ovuleIDs['424C_parents.csv'] = ('424_C', 'A')
            continue
        if id_str == '472_B':
            ovuleIDs['472B_parents.csv'] = ('472_B', 'A')
            continue
        if id_str == '490_A':
            ovuleIDs['490A_parents.csv'] = ('490_A', 'A')
            continue
        if id_str == '490_B':
            ovuleIDs['490B_parents.csv'] = ('490_B', 'A')
            continue
        if id_str == '473_C':
            ovuleIDs['473C_parents.csv'] = ('473_C', 'A')
            continue
        if id_str == '474_A':
            ovuleIDs['474A_parents.csv'] = ('474_A', 'A')
            continue
        if id_str == '474_E':
            ovuleIDs['474E_parents.csv'] = ('474_E', 'A')
            continue
        if id_str == '424_A':
            ovuleIDs['424A_Parent.csv'] = ('424_A', 'A')
            continue
        if id_str == '490_C':
            ovuleIDs['490C_parents.csv'] = ('490_C', 'A')
            continue
        if id_str == '407_A':
            ovuleIDs['407A_parents.csv'] = ('407_A', 'A')
            continue
        if id_str == '486_A':
            ovuleIDs['486A_parents.csv'] = ('486_A', 'A')
            continue
        if id_str == '507_B':
            ovuleIDs['507B_parents.csv'] = ('507_B', 'A')
            continue
        if id_str == '495_A':
            ovuleIDs['495A_parents.csv'] = ('495_A', 'A')
            continue
        if id_str == '495_B':
            ovuleIDs['495B_parents.csv'] = ('495_B', 'A')
            continue
        if id_str == '507_A':
            ovuleIDs['507A_parents.csv'] = ('507_A', 'A')
            continue
        if id_str == '513_A':
            ovuleIDs['513A_parents.csv'] = ('513_A', 'A')
            continue

        n = len(id_str)
        matching_annFileName = [item for item in nerveFileNames.keys() if item[0:n] == id_str]
        if len(matching_annFileName) == 1:
            annFileName = matching_annFileName[0]
            ovuleIDs[annFileName] = (id, 'A')
            print('Matching ' + id_str + ' with ' + annFileName, file=log)
        else:
            print('Did not find a matching annotations file for ' + str(id_str))
            print('Did not find a matching annotations file for ' + str(id_str), file=log)

# Create json for ovuleIDs
with open('ovuleIDs.json', 'w') as fp:
    json.dump(ovuleIDs, fp)