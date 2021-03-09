import pickle
import pandas as pd
import openpyxl
import os

path = 'C:\\Users\\User\\Documents\\Work\\SIRCo\\loadForecasting\\theNewSoftware\\Power-consumption-forecasting-software\\data'
# fileToRead = os.path.join (path, 'Output_ExcludingDG.pickle') 
# with open(fileToRead, 'rb') as file:
#     outputHistory = pickle.load (file)
# outputHistory.to_excel (os.path.join (path, 'Output_ExcludingDG.xlsx'))

fileToRead = os.path.join (path, 'DataSet.pickle') 
with open(fileToRead, 'rb') as file:
    outputHistory = pickle.load (file)
outputHistory.to_excel (os.path.join (path, 'DataSet.xlsx'))

# path = 'C:\\Users\\User\\Documents\\Work\\SIRCo\\Load Forecasting\\The New Software\\Pahbar-GUI\\data'
# fileToRead = os.path.join (path, 'DataSet_ExcludingDG.pickle') 
# with open(fileToRead, 'rb') as file:
#     outputHistory = pickle.load (file)
# outputHistory.to_excel (os.path.join (path, 'DataSet_ExcludingDG.xlsx'))

# path = 'C:\\Users\\User\\Documents\\Work\\SIRCo\\Load Forecasting\\The New Software\\Pahbar-GUI\\data'
# fileToRead = os.path.join (path, 'Output.pickle') 
# with open(fileToRead, 'rb') as file:
#     outputHistory = pickle.load (file)
# outputHistory.to_excel (os.path.join (path, 'Output.xlsx'))