from datetime import timedelta
from datetime import date
from datetime import datetime
import os
import pandas as pd
from persiantools.jdatetime import JalaliDate

class HistoricalLoad ():
    def __init__ (self, repository, path = None):
        self.R = repository
        if path:
            self.data = pd.read_excel (path, engine='openpyxl')
            temp = self.data.isnull().values.any()
            if temp:
                self.correctData = False
            else:
                self.correctData = True
                self.__convert_toGregorianDate ()

    def __convert_toGregorianDate (self):
        for i in range (len (self.data.index)):
            dateList = str (self.data.iloc [i, self.data.columns.get_loc('تاریخ')]).split ('/')
            gregorianDate = JalaliDate (int (dateList [0]), int (dateList [1]), int (dateList [2])).to_gregorian()
            self.data.iloc [i, self.data.columns.get_loc('تاریخ')] = gregorianDate

    def get_HistoricalLoadData (self, date, predictDay = False):
        self.yesterdayLoad = []

        if predictDay:
            dataSet = self.R.dataSet.data
            numberOfRecords = self.R.dataSet.numberOfRecords
        else:
            dataSet = self.R.completedDataSet.data
            numberOfRecords = self.R.completedDataSet.numberOfRecords

        for i in range (int (numberOfRecords / 24)):
            try:
                temp1 = dataSet.iloc [numberOfRecords - 1 - 24 * i - 23]['Date'].to_pydatetime ().date ()
            except:
                try:
                    temp1 = dataSet.iloc [numberOfRecords - 1 - 24 * i - 23]['Date']
                except:
                    break
            temp2 = date - timedelta (days = 2)
            if (temp1 == temp2):
                for h in range (24):
                    self.yesterdayLoad.append (dataSet.iloc [numberOfRecords - 1 - 24 * i - 23 + h]['Load'])
                break
        if (not (self.yesterdayLoad)) and (self.data):
            for row in range (len (self.data.index)):
                if (self.data.iloc [row]['تاریخ'] == date - timedelta (days = 2)):
                    self.yesterdayLoad = self.data.iloc [row]['H1':'H24'].values.tolist ()
                    break

        if not (self.yesterdayLoad):
            print (f'You do not have {JalaliDate(date - timedelta (days = 2))} load data! Please complete your Load Data File!')

        self.lastWeekLoad = []
        for i in range (int (numberOfRecords / 24)):
            try:
                temp3 = dataSet.iloc [numberOfRecords - 1 - 24 * i - 23]['Date'].to_pydatetime ().date ()
            except:
                try:
                    temp3 = dataSet.iloc [numberOfRecords - 1 - 24 * i - 23]['Date']
                except:
                    break

            temp4 = date - timedelta (days = 7)
            if (temp3 == temp4):
                for h in range (24):
                    self.lastWeekLoad.append (dataSet.iloc [numberOfRecords - 1 - 24 * i - 23 + h]['Load'])
                break

        if (not (self.lastWeekLoad)) and (self.data):
            for row in range (len (self.data.index)):
                if (self.data.iloc [row]['تاریخ'] == date - timedelta (days = 7)):
                    self.lastWeekLoad = self.data.iloc [row]['H1':'H24'].values.tolist ()
                    break
        
        if not (self.lastWeekLoad):
            print (f'You do not have {JalaliDate(date - timedelta (days = 7))} load data! Please complete your Load Data File!')
                
        if not (predictDay):
            self.load = []
            for row in range (len (self.data.index)):
                if (self.data.iloc [row]['تاریخ'] == date):
                    self.load = self.data.iloc [row]['H1':'H24'].values.tolist ()
                    break

            if not (self.load):
                print (f'You do not have {JalaliDate (date)} load data! Please complete your Load Data File!')