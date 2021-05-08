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
        self.hoursHeaders = []
        for i in range (1, 25):
            self.hoursHeaders.append (f'H{i}')
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
        headers = self.headers [:-1] + self.hoursHeaders
        removeIndexList = [4, 4, 4, 4, 7, 7, 10, 10, 10, 10]
        day = 0
        for k in range (len (removeIndexList)):
            headers.pop (removeIndexList [k])

        for i in range (int (len (self.data)/24)):
            dataSetDate = self.data.loc [i * 24]['Date'].date ()

            if (dataSetDate >= from_date) and (dataSetDate <= to_date):
                data.append (self.data.iloc [i * 24,:].values.tolist ())

                for j in range (1, 24):
                    data [day].append (self.data.loc [i * 24 + j]['Load'])
                
                for k in range (len (removeIndexList)):
                    data [day].pop (removeIndexList [k])  
                day += 1              

        for i in range (len (data)):
            data [i][0] = JalaliDate (data [i][0].date ())
        
        
        self.dataDictionary = dict ({'header':headers, 'data': data})

    def edit_Data (self, R, newLoadData):
        self.invalidEditDate = 0     
        for row in range (len (newLoadData.index)):
            currentDate = newLoadData.iloc [row]['تاریخ']
            if (currentDate > self.trainEndDate) or (currentDate < self.data.iloc [0]['Date']):
                self.invalidEditDate += 1
                break
            correctData = newLoadData.iloc [row]['H1':'H24'].values.tolist ()
            # correctDataMax = max (correctData)
            # correctDataPeakHour = correctData.index (correctDataMax) + 1
            for i in range (int (self.numberOfRecords / 24)):
                dataSetDate = self.data.iloc [self.numberOfRecords - i * 24 - 1]['Date'].date ()
                if  dataSetDate== currentDate:
                    for j in range (24):
                        self.data.loc [self.numberOfRecords - i * 24 - 1 - j, 'Load'] = correctData [23 - j]
                    # self.data.loc [self.numberOfRecords - i - 1, 'MaxLoad'] = correctDataMax
                    # self.data.loc [self.numberOfRecords - i - 1, 'PeakHour'] = correctDataPeakHour

                if dataSetDate == currentDate + timedelta (days=2):
                    for j in range (24):
                        self.data.loc [self.numberOfRecords - i * 24 - 1 - j, 'YesterdayLoad'] = correctData [23 - j]
                    # self.data.loc [self.numberOfRecords - i - 1, 'PeakLoadYesterday'] = correctDataMax
                    # self.data.loc [self.numberOfRecords - i - 1, 'PeakHourYesterday'] = correctDataPeakHour

                if dataSetDate == currentDate + timedelta (days=7):
                    for j in range (24):
                        self.data.loc [self.numberOfRecords - i * 24 - 1 - j, 'LastWeekLoad'] = correctData [23 - j]
                    break
            self.__update_Attributes ()
    
    def find_ActualValues (self, dates):
        self.actualValues = []
        for date in dates:
            load = []
            for i in range (int (len (self.data) / 24)):
                temp = self.data.loc [len (self.data) -1 - i * 24 - 23]['Date']
                if JalaliDate (temp.date ()) == date:
                    for j in range (24):
                        load.append (self.data.iloc [len (self.data) - 1 - i * 24 - 23 + j]['Load'])                     
                    self.actualValues.append (['Actual'] + [date] + load)
                    break

