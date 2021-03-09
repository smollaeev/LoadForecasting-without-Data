from datetime import date
from datetime import timedelta
import pandas as pd
import numpy as np
from pahbar.independentVariables import IndependentVariables
from pahbar.calendarData import CalendarData
from pahbar.dayLength import daylength
from pahbar.weatherData import WeatherData
import os
from pahbar.historicalLoad import HistoricalLoad
import pickle
import copy
import os.path
from persiantools.jdatetime import JalaliDate
from pahbar.dataSet import DataSet
import jdatetime
import logging

class Repository:

    def __init__ (self, path):
        self.path = path
        self.selectedDataSet = '.pickle'
        self.outputHeaders = ['نوع داده', 'تاریخ']
        for i in range (1, 25):
            self.outputHeaders.append (f'H{i}')
        self.__unpickle_DataSet (os.path.join (self.path, 'DataSet.pickle'))   
        self.__unpickle_OutputHistory (os.path.join (self.path, 'Output.pickle'))     

    def __pickle_DataSet (self, path):
        with open(path, 'wb') as file:
            pickle.dump (self.dataSet.data, file)

    def __pickle_CompletedDataSet (self, path):
        with open (path, 'wb') as file:
            pickle.dump (self.completedDataSet.data, file)

    def __unpickle_DataSet (self, path):
        with open (path, 'rb') as file:
            data = pickle.load (file)
        self.dataSet = DataSet (data, self.selectedDataSet, self.path)

    def __unpickle_CompletedDataSet (self):
        with open (self.dataSet.completedDataSetPath, 'rb') as file:
            data = pickle.load (file)
        self.completedDataSet = DataSet (data, self.selectedDataSet, self.path)

    def __unpickle_OutputHistory (self, path):
        with open (path, 'rb') as file:
            self.outputHistory = pickle.load (file)

    def __get_TrainSet (self):
        X = self.dataSet.data.iloc [:, 1:-1].values
        self.X_train = IndependentVariables (X)
        self.y_train = self.dataSet.data.iloc [:, -1].values 

    def __dump_ProcessedData (self, path):
        with open (path, 'wb') as file:
            pickle.dump (self.X_train, file)

    def export_PredictionAsXLSX (self, fromDate, toDate, path):
        self.get_PredictedValues (from_date = fromDate, to_date = toDate)
        if self.predictedDataHistory:
            for i in range (len (self.predictedDataHistory)):
                for j in range (len (self.predictedDataHistory [i])):
                    if isinstance (self.predictedDataHistory [i][j], float):
                        self.predictedDataHistory [i][j] = round (self.predictedDataHistory [i][j], 3)
                    
            exportedOutput = pd.DataFrame (data = self.predictedDataHistory, columns= self.outputHeaders)
            exportedOutput.to_excel (path)

    def save_outputHistory (self):
        path = os.path.join (self.path, 'Output'+f'{self.selectedDataSet}')
        with open (path, 'wb') as file:
            pickle.dump (self.outputHistory, file)

    def dump_TrainedAlgorithmsData (self, trainer):
        fileName = 'Regressors_'+f'{self.selectedDataSet_RightNow}'
        path = os.path.join (self.path, fileName) 
        with open(path, 'wb') as file:
            pickle.dump (trainer.regressors, file)

        fileName = 'TrainDate_' + f'{self.selectedDataSet_RightNow}'
        path = os.path.join (self.path, fileName) 
        with open(path, 'wb') as file:
            pickle.dump (JalaliDate (date.today ()), file)

    def get_ProcessedData (self):
        fileName = 'Preprocessed_X_Train_'+f'{self.selectedDataSet}'
        path = os.path.join (self.path, fileName)
        with open (path, 'rb') as file:
            self.processed_X_train = pickle.load (file)

    def get_TrainedAlgorithms (self):
        fileName = 'Regressors_'+f'{self.selectedDataSet}'
        path = os.path.join (self.path, fileName)
        with open(path, 'rb') as file:
            self.regressors = pickle.load (file) 

    def get_LastTrainDate (self):
        fileName = 'TrainDate_' + f'{self.selectedDataSet}'
        path = os.path.join (self.path, fileName) 
        with open(path, 'rb') as file:
            self.lastTrainDate = pickle.load (file)

    def export_AsXLSX (self, path):
        # self.dataSet.define_Path (self.selectedDataSet, self.path)
        self.__unpickle_CompletedDataSet ()
        self.completedDataSet.data.to_excel (path)

    def select_DataSet (self, mode):
        if self.selectedDataSet != mode:
            self.selectedDataSet = mode
            self.__unpickle_DataSet (os.path.join (self.path, 'DataSet'+f'{mode}'))   
            self.__unpickle_OutputHistory (os.path.join (self.path, 'Output'+f'{mode}'))         

    def complete_DataSet (self, pathToLoadData):
        self.completedDataSet = copy.deepcopy (self.dataSet)

        self.weatherDataUnavailable = None
        self.calendarDataUnavailable = None
        self.historicalLoadUnavailable = None
        
        newDate = (self.completedDataSet.data.iloc [self.completedDataSet.numberOfRecords - 1]['Date'])
        
        historicalLoad = HistoricalLoad (self, pathToLoadData)
        if not (historicalLoad.correctData):
            self.historicalLoadUnavailable = 1
            return False

        weatherData = WeatherData (date.today () - timedelta (days=1), newDate.date () + timedelta (days=1))
        try:
            weatherData.get_WeatherData ()
        except Exception as inst:
            print (inst)
            logging.warning (inst)
            self.weatherDataUnavailable = 1
            print (f'There was a problem in fetching {JalaliDate (newDate.date () + timedelta (days=1))} weather data. Trying to get the rest of data ...')
            return False

        stopDate = historicalLoad.data.iloc [len (historicalLoad.data.index) - 1, historicalLoad.data.columns.get_loc('تاریخ')]
        currentDate = copy.deepcopy (self.completedDataSet.data.iloc [self.completedDataSet.numberOfRecords - 1]['Date'].date ())
        while (currentDate != stopDate): 
            newRows = []
            newDate = newDate + timedelta (days=1)
            for i in range (24):
                newRows.append ([newDate])
            
            calendarData = CalendarData (newDate.date ())
            yesterdayCalendarData = CalendarData (newDate.date () - timedelta (days=2))
            lastWeekCalendarData = CalendarData (newDate.date () - timedelta (days=7))

            try:
                calendarData.get_CalendarData ()
                yesterdayCalendarData.get_CalendarData ()
                lastWeekCalendarData.get_CalendarData ()
                for i in range (24):
                    newRows [i].append (calendarData.eideMazhabi)
                    newRows [i].append (calendarData.aza)
                    newRows [i].append (calendarData.holiday)
                    newRows [i].append (yesterdayCalendarData.holiday)
                    newRows [i].append (lastWeekCalendarData.holiday)

            except Exception as inst:
                print (inst)
                print (f'There was a problem in fetching {JalaliDate (newDate.date ())} calendar data. Trying to get the rest of data ...')
                self.calendarDataUnavailable = 1
                return False

            for i in range (24):
                newRows [i].append (i + 1)
                newRows [i].append (calendarData.dayName)
                newRows [i].append (daylength (calendarData.date.timetuple().tm_yday, 36.2605))
                newRows [i].append (daylength (yesterdayCalendarData.date.timetuple().tm_yday, 36.2605))
                newRows [i].append (daylength (lastWeekCalendarData.date.timetuple().tm_yday, 36.2605))

            historicalLoad.get_HistoricalLoadData (newDate.date ())
            
            for i in range (24):
                newRows [i].append (weatherData.allWeatherData [f'{calendarData.date.year}-{calendarData.date.month}'].values [calendarData.date.day - 1][0])
                newRows [i].append (weatherData.allWeatherData [f'{calendarData.date.year}-{calendarData.date.month}'].values [calendarData.date.day - 1][1])
            
            if historicalLoad.yesterdayLoad:
                for i in range (24):
                    newRows [i].append (max (historicalLoad.yesterdayLoad))
                    newRows [i].append (historicalLoad.yesterdayLoad.index (max (historicalLoad.yesterdayLoad)) + 1)
            else:
                self.historicalLoadUnavailable = 1
                return False

            if historicalLoad.lastWeekLoad:
                for hour in range (24):
                    newRows [hour].append (historicalLoad.lastWeekLoad [hour])
            else:
                self.historicalLoadUnavailable = 1
                return False

            for hour in range (24):
                newRows [hour].append (historicalLoad.yesterdayLoad [hour])

            if historicalLoad.load:
                for hour in range (24):
                    newRows [hour].append (historicalLoad.load [hour])
                # newRows.append (max (historicalLoad.load))
                # newRows.append (historicalLoad.load.index (max (historicalLoad.load)) + 1)
            else:
                self.historicalLoadUnavailable = 1
                return False

            for i in range (24):
                self.completedDataSet.data.loc [len (self.completedDataSet.data)] = newRows [i]
            
            self.completedDataSet.numberOfRecords += 24
            currentDate = newDate.date ()
        
        self.dataSet = copy.deepcopy (self.completedDataSet)
        self.__pickle_CompletedDataSet (self.dataSet.completedDataSetPath)
        self.__pickle_DataSet (self.dataSet.dataSetPath)

        self.dataSet.determine_TrainEndDate ()

        return True

    def edit_DataSet (self, newLoadData):
        self.completedDataSet = copy.deepcopy (self.dataSet)
        self.completedDataSet.define_Path (self.selectedDataSet, self.path)
        self.completedDataSet.pickle_Data (self.completedDataSet.completedDataSetPath)
        self.historicalLoadUnavailable = None
        for i in range (len (newLoadData)):
            try:
                newLoadData.loc [i, 'تاریخ'] = newLoadData.iloc [i]['تاریخ'].to_gregorian ()
            except Exception as inst:
                print (inst)
        self.completedDataSet.edit_Data (self, newLoadData)
        # self.dataSet.define_Path (self.selectedDataSet, self.path)
        if not (self.completedDataSet.invalidEditDate):
            self.completedDataSet.pickle_Data (self.completedDataSet.completedDataSetPath)
            self.dataSet = copy.deepcopy (self.completedDataSet)
            self.dataSet.pickle_Data (self.completedDataSet.dataSetPath)
            return True
        else:
            result = dict ({'English':'Invalid dates in your data!', 'Farsi':'در اطلاعات وارد شده، تاریخ‌های غیرقابل قبول وجود دارد!'})
            return result

    def record_SelectedDataSetRightNow (self):
        return self.selectedDataSet
        
    def prepare_Data (self):
        self.selectedDataSet_RightNow = self.record_SelectedDataSetRightNow ()
        self.__get_TrainSet ()
        self.X_train.encode_OneHot_FitTransform ()
        self.X_train.fit_FeatureScaler ()
        self.X_train.scale_Features (self.X_train)
        fileName = 'Preprocessed_X_Train_'+f'{self.selectedDataSet_RightNow}'
        path = os.path.join (self.path, fileName)
        self.__dump_ProcessedData (path)

    def get_PredictedValues (self, from_date, to_date):
        self.__unpickle_OutputHistory (os.path.join (self.path, 'Output'+f'{self.selectedDataSet}'))

        self.predictedDataHistory = []

        currentDate = from_date - timedelta (days=1)
        while (currentDate != to_date):
            currentDate += timedelta (days=1)
            for i in range (len (self.outputHistory)):
                index = len (self.outputHistory) - i - 1
                dateList = str (self.outputHistory.iloc [index, self.outputHistory.columns.get_loc('تاریخ')]).split ('-')
                gregorianDate = JalaliDate (int (dateList [0]), int (dateList [1]), int (dateList [2])).to_gregorian()
                if (gregorianDate == currentDate):
                    self.predictedDataHistory.append (['Predicted'] + self.outputHistory.iloc [index,:-1].values.tolist ())
                    break

    def export_AllPredictionHistory (self, file_path):
        self.__unpickle_OutputHistory (os.path.join (self.path, 'Output'+f'{self.selectedDataSet}'))
        for i in range (len (self.outputHistory)):
            for j in range (1, 25):
                self.outputHistory.iloc [i, self.outputHistory.columns.get_loc(f'H{j}')] = round (self.outputHistory.iloc [i][f'H{j}'], 3)
        self.outputHistory.to_excel (file_path)        