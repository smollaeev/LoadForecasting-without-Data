from datetime import timedelta
import pandas as pd
from persiantools.jdatetime import JalaliDate

class HistoricalLoad ():
    def __init__ (self, dataSet, loadData = None):
        self.dataSet = dataSet
        self.loadData = loadData
        if isinstance (self.loadData, pd.DataFrame):
            self.__convert_toGregorianDate__ ()

    def __convert_toGregorianDate__ (self):
        for i in range (len (self.loadData.index)):
            if '/' in str (self.loadData.iloc [i, self.loadData.columns.get_loc('تاریخ')]):
                dateList = str (self.loadData.iloc [i, self.loadData.columns.get_loc('تاریخ')]).split ('/')
            else:
                dateList = str (self.loadData.iloc [i, self.loadData.columns.get_loc('تاریخ')]).split ('-')
            gregorianDate = JalaliDate (int (dateList [0]), int (dateList [1]), int (dateList [2])).to_gregorian()
            self.loadData.iloc [i, self.loadData.columns.get_loc('تاریخ')] = gregorianDate
        self.endDate = gregorianDate

    def get_HistoricalLoadData (self, date, yesterdayLoad, predictDay = False):
        self.yesterdayLoad = []

        dataSet = self.dataSet.data
        numberOfRecords = self.dataSet.numberOfRecords

        for i in range (numberOfRecords):
            try:
                temp1 = dataSet.iloc [numberOfRecords - 1 - i]['Date'].to_pydatetime ().date ()
            except:
                try:
                    temp1 = dataSet.iloc [numberOfRecords - i - 1]['Date']
                except:
                    break
            temp2 = date - timedelta (days = 2)
            if (temp1 == temp2):
                self.yesterdayLoad = dataSet.iloc [numberOfRecords - 1 - i, -26:-2].to_list ()
                break
        if not (self.yesterdayLoad):
            try:
                temp = yesterdayLoad [0]
                if (temp == date - timedelta (days = 2)):
                    self.yesterdayLoad = list (yesterdayLoad [1:])
            except:
                pass

        if not (self.yesterdayLoad):
            print (f'You do not have {JalaliDate(date - timedelta (days = 2))} load data! Please complete your Load Data File!')

        self.lastWeekLoad = []
        for i in range (numberOfRecords):
            try:
                temp3 = dataSet.iloc [numberOfRecords - 1 - i]['Date'].to_pydatetime ().date ()
            except:
                try:
                    temp3 = dataSet.iloc [numberOfRecords - 1 - i]['Date']
                except:
                    break

            temp4 = date - timedelta (days = 7)
            if (temp3 == temp4):
                self.lastWeekLoad = dataSet.iloc [numberOfRecords - 1 - i, -26:-2].to_list ()
                break

        if not (self.lastWeekLoad):
            try:
                temp = yesterdayLoad [0]
                if (temp == date - timedelta (days = 7)):
                    self.lastWeekLoad = list (yesterdayLoad [1:])
            except:
                pass
        
        if not (self.lastWeekLoad):
            print (f'You do not have {JalaliDate(date - timedelta (days = 7))} load data! Please complete your Load Data File!')
                
        if not (predictDay):
            self.load = []
            for row in range (len (self.loadData.index)):
                if (self.loadData.iloc [row]['تاریخ'] == date):
                    self.load = self.loadData.iloc [row]['H1':'H24'].values.tolist ()
                    break

            if not (self.load):
                print (f'You do not have {JalaliDate (date)} load data! Please complete your Load Data File!')