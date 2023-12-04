import subprocess
import os

pathData = 'data'
pathNerves = 'nerves'

for path, subdirs, files in os.walk(pathData):
    for file in files:
        if (file.endswith('.tif') or file.endswith('.tiff')):
            pathInput = os.path.join(path, file)
            pathSplit = path.split('/')
            print(pathSplit)
            pathSaveDir = pathNerves + '/' + pathSplit[1] + '/' + pathSplit[3]
            if (not os.path.exists(pathSaveDir)):
                os.makedirs(pathSaveDir)
            pathSave = pathSaveDir + '/' + file.split('.')[0] + '.csv'
            if (os.path.exists(pathSave)):
                print('File '+ pathInput + ' is computed already.')
                continue
            print('File '+ pathInput + ' ...')
            proc = subprocess.Popen('./tiff_nerve'+' "'+ pathInput+'" ' +str(" > ")+ pathSave, shell=True)
            proc.wait()