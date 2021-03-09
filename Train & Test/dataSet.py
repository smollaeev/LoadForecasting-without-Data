from persiantools.jdatetime import JalaliDate
import os
import pickle
import pandas as pd
from pahbar.historicalLoad import HistoricalLoad
from datetime import timedelta

class DataSet:
    def __init__ (self, data, selectedDataSet, path):
        self.data = data
        self.headers = list (self.data.columns)
        self.__update_Attributes ()
        self.define_Path (selectedDataSet, path)

    def __update_Attributes (self):
        self.numberOfRecords = len (self.data.index)
        self.determine_TrainEndDate ()

    def __unpickle_DataSet (self):
        with open(self.dataSetPath, 'rb') as file:
            self.data = pickle.load (file)

    def define_Path (self, selectedDataSet, path):
        if selectedDataSet == '.pickle':
            self.completedDataSetPath = os.path.join (path, 'CompletedDataSet.pickle')
            self.dataSetPath = os.path.join (path, 'DataSet.pickle')
        if selectedDataSet == '_ExcludingDG.pickle':
            self.completedDataSetPath = os.path.join (path, 'CompletedDataSet_ExcludingDG.pickle')
            self.dataSetPath = os.path.join (path, 'DataSet_ExcludingDG.pickle')

    def pickle_Data (self, path):
        fileToWrite = os.path.join (path)
        with open(fileToWrite, 'wb') as file:
            pickle.dump (self.data, file)

    def insert_Row (self, rowNumber, rowValue): 
        # Starting value of upper half 
        upperHalfStart = 0
    
        # End value of upper half 
        upperHalfEnd = rowNumber 
    
        # Start value of lower half 
        lowerHalfStart = rowNumber 
    
        # End value of lower half 
        lowerHalfEnd = self.data.shape[0]
    
        # Create a list of upperHalf index 
        upperHalf = [*range(upperHalfStart, upperHalfEnd, 1)] 
    
        # Create a list of lowerHalf index 
        lowerHalf = [*range(lowerHalfStart, lowerHalfEnd, 1)] 
    
        # Increment the value of lower half by 1 
        lowerHalf = [x.__add__(1) for x in lowerHalf] 
    
        # Combine the two lists 
        index_ = upperHalf + lowerHalf 
    
        # Update the index of the dataframe 
        self.data.index = index_ 
    
        # Insert a row at the end 
        self.data.loc[rowNumber] = rowValue 
        
        # Sort the index labels 
        self.data = self.data.sort_index()

    def determine_TrainEndDate (self):
        self.trainEndDate = (self.data.iloc [self.numberOfRecords - 1]['Date']).date ()

    def revive (self):
        self.__unpickle_DataSet ()
        self.headers = list (self.data.columns)
        self.numberOfRecords = len (self.data.index)
        self.trainEndDate = (self.data.iloc [self.numberOfRecords - 1]['Date']).date ()

    def convert_DatatoDict (self, from_date, to_date):
        data = []
        for i in range (len (self.data)):
            if (self.data.loc [i]['Date'].date () >= from_date) and (self.data.loc [i]['Date'].date () <= to_date):
                data.append (self.data.iloc [i,:].values.tolist ())
        for i in range (len (data)):
            data [i][0] = JalaliDate (data [i][0].date ())

        for i in range (len (data)):
            data [i] = data [i] [0:4] + data [i] [6:8] + data [i] [10:12] + data [i] [62:]
        
        self.dataDictionary = dict ({'header':self.headers[0:4] + self.headers [6:8] + self.headers[10:12] + self.headers[62:], 'data': data})

    def edit_Data (self, pathToLoadData, R):
        newLoadData = HistoricalLoad (R, path=pathToLoadData)

        for row in range (len (newLoadData.data.index)):
            currentDate = newLoadData.data.iloc [row]['تاریخ']
            correctData = newLoadData.data.iloc [row]['H1':'H24'].values.tolist ()
            correctDataMax = max (correctData)
            correctDataPeakHour = correctData.index (correctDataMax) + 1
            for i in range (self.numberOfRecords):
                if self.data.iloc [self.numberOfRecords - i - 1]['Date'].date () == currentDate:
                    self.data.loc [self.numberOfRecords - i - 1, 'H1':'H24'] = correctData
                    self.data.loc [self.numberOfRecords - i - 1, 'MaxLoad'] = correctDataMax
                    self.data.loc [self.numberOfRecords - i - 1, 'PeakHour'] = correctDataPeakHour

                if self.data.iloc [self.numberOfRecords - i - 1]['Date'].date () == currentDate + timedelta (days=2):
                    self.data.loc [self.numberOfRecords - i - 1, 'Yesterday Load 1':'Yesterday Load 24'] = correctData
                    self.data.loc [self.numberOfRecords - i - 1, 'PeakLoadYesterday'] = correctDataMax
                    self.data.loc [self.numberOfRecords - i - 1, 'PeakHourYesterday'] = correctDataPeakHour

                if self.data.iloc [self.numberOfRecords - i - 1]['Date'].date () == currentDate + timedelta (days=7):
                    self.data.loc [self.numberOfRecords - i - 1, 'LastWeek1':'LastWeek24'] = correctData
            self.__update_Attributes ()


