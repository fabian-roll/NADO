import subprocess
import os

pathData = 'data'
pathNerves = 'nerves'

for path, subdirs, files in os.walk(pathData):
    for file in files:
        if (file.endswith('.tif') or file.endswith('.tiff')):
            pathInput = os.path.join(path, file)
            pathSplit = path.split('/')
            species=pathSplit[1].split('_')[2]

            # if the file belongs to primordia
            if pathSplit[2] == '1-I to 2-II':
                if species == 'Arabidopsis':
                    growth_stage = pathSplit[3]
                    pathSaveDir = (pathNerves + '/'
                                   + species + '/' 
                                   + '1-I to 2-II' + '/'
                                   + growth_stage)
                    pathSaveDirTerminal = (pathNerves + '/'
                                           + species + '/' 
                                           + '1-I\ to\ 2-II' + '/'
                                           + growth_stage)
                elif species == 'Cardamine':
                    pathSaveDir = (pathNerves + '/'
                                   + species + '/' 
                                   + '1-I to 2-II')
                    pathSaveDirTerminal = (pathNerves + '/'
                                           + species + '/' 
                                           + '1-I\ to\ 2-II')
                else:
                    raise ValueError('unrecognized species')
                
            else:
                pathSaveDir = pathNerves + '/' + species + '/' + pathSplit[2]
                pathSaveDirTerminal = pathSaveDir
            
            if (not os.path.exists(pathSaveDir)):
                os.makedirs(pathSaveDir)
            pathSave = pathSaveDir + '/' + file.split('.')[0] + '.csv'
            pathSaveTerminal = pathSaveDirTerminal + '/' + file.split('.')[0] + '.csv'
            if (os.path.exists(pathSave)):
                print('File '+ pathInput + ' is computed already.')
                continue
            print('File '+ pathInput + ' ...')
            proc = subprocess.Popen('./nerve'+' "'+ pathInput+'" ' +str(" > ")+ pathSaveTerminal, shell=True)
            proc.wait()