from datetime import timedelta
import pandas as pd
from persiantools.jdatetime import JalaliDate
from pahbar.dates import Dates

class HistoricalLoad ():
    def __init__ (self, dataSet, loadData = None):
        self.dataSet = dataSet
        self.loadData = loadData
        if isinstance (self.loadData, pd.DataFrame):
            self.__convert_toGregorianDate__ ()

    def __convert_toGregorianDate__ (self):
        for i in range (len (self.loadData.index)):
            dateList = Dates.get_DateList (str (self.loadData.iloc [i, self.loadData.columns.get_loc('تاریخ')]))
            gregorianDate = JalaliDate (int (dateList [0]), int (dateList [1]), int (dateList [2])).to_gregorian()
            self.loadData.iloc [i, self.loadData.columns.get_loc('تاریخ')] = gregorianDate
        self.endDate = gregorianDate

    def __find_InDataSet__ (self, date1, date2, dataSet, row):
        load = []
        if (date1 == date2):
            load = dataSet.loc [row, 'Load1':'Load24'].to_list ()
        return load   

    def __get_HistoricalLoadFromDataSet__ (self, date_, numberOfPreviousDays):
        dataSet = self.dataSet.loadData.data
        numberOfRecords = self.dataSet.loadData.numberOfRecords
        for i in range (numberOfRecords):
            row = numberOfRecords - 1 - i
            try:
                temp1 = dataSet.iloc [row]['Date'].to_pydatetime ().date ()
            except:
                try:
                    temp1 = dataSet.iloc [row]['Date']
                except:
                    break
            temp2 = date_ - timedelta (days = numberOfPreviousDays)
            historicalLoad = self.__find_InDataSet__ (temp1, temp2, dataSet, row)
            if historicalLoad:
                break
        return historicalLoad
    
    @staticmethod
    def __get_HistoricalLoadFromSavedLoad__(savedLoad, date_, numberOfPreviousDays):
        try:
            if (savedLoad [0] == date_ - timedelta (days = numberOfPreviousDays)):
                return list (savedLoad [1:])
        except:
            pass

    def __get_YesterdayLoad__ (self, date_, yesterdayLoad):
        self.yesterdayLoad = []
        self.yesterdayLoad = self.__get_HistoricalLoadFromDataSet__ (date_, 2)
        if not (self.yesterdayLoad):
            self.yesterdayLoad = HistoricalLoad.__get_HistoricalLoadFromSavedLoad__ (yesterdayLoad, date_, 2)
        if not (self.yesterdayLoad):
            print (f'You do not have {JalaliDate(date_ - timedelta (days = 2))} load data! Please complete your Load Data File!')

    def __get_LastWeekLoad__ (self, date_, yesterdayLoad):
        self.lastWeekLoad = []
        self.lastWeekLoad = self.__get_HistoricalLoadFromDataSet__ (date_, 7)
        if not (self.lastWeekLoad):
            self.lastWeekLoad = HistoricalLoad.__get_HistoricalLoadFromSavedLoad__ (yesterdayLoad, date_, 7)        
        if not (self.lastWeekLoad):
            print (f'You do not have {JalaliDate(date_ - timedelta (days = 7))} load data! Please complete your Load Data File!')

    def __get_Load__ (self, date_):
        self.load = []
        for row in range (len (self.loadData.index)):
            if (self.loadData.iloc [row]['تاریخ'] == date_):
                self.load = self.loadData.iloc [row]['H1':'H24'].values.tolist ()
                break
        if not (self.load):
            print (f'You do not have {JalaliDate (date_)} load data! Please complete your Load Data File!')

    def get_HistoricalLoadData (self, date_, yesterdayLoad, predictDay = False):
        self.__get_YesterdayLoad__ (date_, yesterdayLoad)
        self.__get_LastWeekLoad__ (date_, yesterdayLoad)     
        if not (predictDay):
            self.__get_Load__ (date_)   