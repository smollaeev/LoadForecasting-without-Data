from datetime import date
import pandas as pd
from pahbar.predictDay import PredictDay
import copy
from persiantools.jdatetime import JalaliDate

class STOutput:
    def __init__ (self, predictDates, dataSetHeaders):
        self.predictDates = predictDates
        self.allHeaders = copy.deepcopy (dataSetHeaders)
        self.allHeaders.insert (9, 'Hour')
        self.allHeaders = self.allHeaders [:15]
        self.allHeaders += ['LastWeekLoad', 'YesterdayLoad', 'Load']

        self.featuresHeaders = self.allHeaders [:15]
        self.loadFeaturesHeaders = self.allHeaders [-3:]
        self.outputHeaders = ['تاریخ', 'H1','H2','H3','H4','H5','H6','H7','H8','H9','H10','H11','H12','H13','H14','H15','H16','H17','H18','H19','H20','H21','H22','H23','H24']
        self.output = pd.DataFrame (columns= self.outputHeaders)
        self.predictDays = []
        self.predictedDayList = []
        for i in range (len (self.predictDates)):
            self.predictDays.append (PredictDay (self.predictDates [i], self.predictDates [i]))

    def convert_DatatoDict(self, from_date, to_date):
        data = [
            self.output.iloc[i, :].values.tolist()
            for i in range(len(self.output))
            if (self.output.loc[i]['تاریخ'] >= from_date)
            and (self.output.loc[i]['تاریخ'] <= to_date)
        ]

        for datum in data:
            datum[0] = JalaliDate(datum[0])
        self.dataDictionary = dict ({'header':self.outputHeaders, 'data': data})    

    def make_CompleteListOfOneRow (self, row, features, predictedLoad):
        # predictedLoad = list (predictedLoad)
        self.predictedDayList.append (features)
        self.predictedDayList [row] += predictedLoad
        self.predictedDayList [row].append (max (predictedLoad))
        self.predictedDayList [row].append (predictedLoad.index(max(predictedLoad)) + 1)

    def make_ListOfPredictedLoad (self, predictedLoad): 
        self.predictedLoad = copy.deepcopy (predictedLoad)
        self.predictedLoad [0] = JalaliDate (self.predictedLoad [0])
        self.predictedLoad.append (JalaliDate (date.today ()))


class MTOutput:
    def __init__ (self, predictDates, dataSetHeaders):
        self.predictDates = predictDates
        self.allHeaders = dataSetHeaders
        self.featuresHeaders = dataSetHeaders [:-76]
        self.loadFeaturesHeaders = dataSetHeaders [-76:-26]
        self.outputHeaders = ['تاریخ', 'H1','H2','H3','H4','H5','H6','H7','H8','H9','H10','H11','H12','H13','H14','H15','H16','H17','H18','H19','H20','H21','H22','H23','H24']
        self.output = pd.DataFrame (columns= self.outputHeaders)
        self.predictDays = []
        self.predictedDayList = []
        for i in range (len (self.predictDates)):
            self.predictDays.append (PredictDay (self.predictDates [i], self.predictDates [i]))

    def convert_DatatoDict(self, from_date, to_date):
        data = [
            self.output.iloc[i, :].values.tolist()
            for i in range(len(self.output))
            if (self.output.loc[i]['تاریخ'] >= from_date)
            and (self.output.loc[i]['تاریخ'] <= to_date)
        ]

        for datum in data:
            datum[0] = JalaliDate(datum[0])
        self.dataDictionary = dict ({'header':self.outputHeaders, 'data': data})    

    def make_CompleteListOfOneRow (self, row, features, predictedLoad):
        predictedLoad = list (predictedLoad)
        self.predictedDayList.append (features)
        for i in range (24):
            self.predictedDayList [row].append (predictedLoad [i])
        self.predictedDayList [row].append (max (predictedLoad))
        self.predictedDayList [row].append (predictedLoad.index(max(predictedLoad)) + 1)

    def make_ListOfPredictedLoad (self, predictedLoad): 
        self.predictedLoad = copy.deepcopy (predictedLoad)
        self.predictedLoad [0] = JalaliDate (self.predictedLoad [0])
        self.predictedLoad.append (JalaliDate (date.today ()))