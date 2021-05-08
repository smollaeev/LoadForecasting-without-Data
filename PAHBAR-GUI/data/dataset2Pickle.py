import pickle
import pandas as pd
import openpyxl
import os

path = 'C:\\Users\\User\\Documents\\Work\\SIRCo\\loadForecasting\\theNewSoftware\\Power-consumption-forecasting-software\\data'

dataSet = pd.read_excel (os.path.join (path, 'DataSet_Hourly.xlsx'), index_col= 0, engine='openpyxl')
fileToWrite = os.path.join (path, 'DataSet.pickle') 
with open(fileToWrite, 'wb') as file:
    pickle.dump (dataSet, file)

dataSet = pd.read_excel (os.path.join (path, 'DataSet_ExcludingDG_Hourly.xlsx'), index_col= 0, engine='openpyxl')
fileToWrite = os.path.join (path, 'DataSet_ExcludingDG.pickle') 
with open(fileToWrite, 'wb') as file:
    pickle.dump (dataSet, file)

# outputHistory = pd.read_excel (os.path.join (path, 'Output.xlsx'), index_col= 0, engine='openpyxl')
# fileToWrite = os.path.join (path, 'Output.pickle') 
# with open(fileToWrite, 'wb') as file:
#     pickle.dump (outputHistory, file)

# outputHistory = pd.read_excel (os.path.join (path, 'Output_ExcludingDG.xlsx'), index_col= 0, engine='openpyxl')
# fileToWrite = os.path.join (path, 'Output_ExcludingDG.pickle') 
# with open(fileToWrite, 'wb') as file:
#     pickle.dump (outputHistory, file)