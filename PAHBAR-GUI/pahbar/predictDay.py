from datetime import date
from datetime import timedelta
import re
import os
from pahbar.historicalLoad import HistoricalLoad

class PredictDay:
    def __init__ (self, fromDate, date):
        self.fromDate = fromDate - timedelta (days=1)
        self.date = date

    # @staticmethod
    # def get_PredictDate ():
    #     predictDateStr = input ("Predict Date (YYYY-MM-DD)?")
    #     pattern = '^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'
    #     result = re.match (pattern, predictDateStr)
    #     while not (result):            
    #         print ('Invalid format! Try again!')
    #         predictDateStr = input ("Predict Date (YYYY-MM-DD)?") 
    #         result = re.match (pattern, predictDateStr)  
    #     predictDateLIST = (predictDateStr.split (sep= '-'))
    #     predictDate = date (int (predictDateLIST [0]), int (predictDateLIST [1]), int (predictDateLIST [2]))
    #     predictDay = PredictDay (predictDate)
    #     return predictDay

    def determine_PredictDates (self):
        self.predictDates = []   
        numberOfPredictions = self.date - self.fromDate
        newDate = self.fromDate +timedelta (days=1)  
        for i in range (numberOfPredictions.days):
            self.predictDates.append (newDate)
            newDate += timedelta (days=1)

    def add_HistoricalLoadData (self, R):
        self.historicalLoad = HistoricalLoad (R)
        self.historicalLoad.get_HistoricalLoadData (self.date, predictDay=True)