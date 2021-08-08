from datetime import timedelta
import pandas as pd

class LoadData:
    def __init__ (self, data):
        self.data = data
        self.__get_Headers__ ()
        self.__get_Attributes__ ()

    def __get_Headers__ (self):
        self.headers = list (self.data.columns) [:-1]

    def __get_Attributes__ (self):
        self.numberOfRecords = len (self.data.index)
        self.determine_EndDate ()

    def __get_DataByDate__ (self, date_, headers):
        currentData = []
        for i in range (self.numberOfRecords):
            try:
                temp = self.data.loc [len (self.data) -1 - i, 'Date'].date ()
            except:
                temp = self.data.loc [len (self.data) -1 - i, 'Date']
            if temp == date_:
                currentData = self.data.loc [len (self.data) - 1 - i, headers].to_list ()
                break
        return currentData

    @staticmethod
    def __get_NewDataAttributes__ (newData, row):
        currentDate = newData.iloc [row]['تاریخ']
        correctData = newData.iloc [row]['H1':'H24'].values.tolist ()
        correctDataMax = max (correctData)
        correctDataPeakHour = correctData.index (correctDataMax) + 1
        return currentDate, correctData, correctDataMax, correctDataPeakHour

    def __replace_SelfData__ (self, row, correctData, correctDataMax, correctDataPeakHour):
        self.data.loc [row, 'Load1':'Load24'] = correctData
        self.data.loc [row, 'MaxLoad'] = correctDataMax
        self.data.loc [row, 'PeakHour'] = correctDataPeakHour

    def __replace_YesterdayData__ (self, row, correctData, correctDataMax, correctDataPeakHour):
        self.data.loc [row, 'Yesterday Load 1':'Yesterday Load 24'] = correctData
        self.data.loc [row, 'PeakLoadYesterday'] = correctDataMax
        self.data.loc [row, 'PeakHourYesterday'] = correctDataPeakHour

    def __replace_LastWeekData__ (self, row, correctData):
        self.data.loc [row, 'LastWeek1':'LastWeek24'] = correctData

    def __get_Date__ (self, row):
        try:
            date_ = self.data.iloc [row]['Date'].date ()
        except:
            date_ = self.data.iloc [row]['Date']
        return date_

    def __replace_WithNewRow__ (self, date_, correctData, correctDataMax, correctDataPeakHour):
        for i in range (self.numberOfRecords):
            row = self.numberOfRecords - i - 1
            dataSetDate = self.__get_Date__ (row)            
            if  dataSetDate == date_:
                self.__replace_SelfData__ (row, correctData, correctDataMax, correctDataPeakHour)
            if dataSetDate == date_ + timedelta (days=2):
                self.__replace_YesterdayData__ (row, correctData, correctDataMax, correctDataPeakHour)
            if dataSetDate == date_ + timedelta (days=7):
                self.__replace_LastWeekData__ (row, correctData)
                break

    def __make_HistoricalLoadList__(historicalLoad, date_):
        historicalLoadList = [
            max(historicalLoad.yesterdayLoad),
            historicalLoad.yesterdayLoad.index(max(historicalLoad.yesterdayLoad))
            + 1,
        ]
        historicalLoadList += historicalLoad.lastWeekLoad
        historicalLoadList += historicalLoad.yesterdayLoad
        historicalLoadList += historicalLoad.load
        historicalLoadList.append (max (historicalLoad.load))
        historicalLoadList.append (historicalLoad.load.index(max(historicalLoad.load)) + 1)
        historicalLoadList.append (date_)
        return historicalLoadList

    def __add_Data__ (self, historicalLoadList):
        self.data.loc [len (self.data)] = historicalLoadList
        self.numberOfRecords += 1

    # def __remove_InvalidHeaderNames__ (self, headers):
    #     invalidNames = []
    #     for header in headers:
    #         if header not in self.headers:
    #             invalidNames.append (header)
    #     for invalidName in invalidNames:
    #         headers.remove (invalidName)
    #     return headers
    def determine_EndDate (self):
        try:
            self.endDate = (self.data.iloc [self.numberOfRecords - 1]['Date'].date ())
        except:
            self.endDate = self.data.iloc [self.numberOfRecords - 1]['Date']

    def get_DataByDate (self, dates, headers):
        data = []
        for date_ in dates:
            newData = self.__get_DataByDate__ (date_, headers)
            if newData:
                data.append (newData)
        return data

    def replace_Data (self, newData):
        for row in range (len (newData.index)):            
            currentDate, correctData, correctDataMax, correctDataPeakHour  = LoadData.__get_NewDataAttributes__ (newData, row)
            self.__replace_WithNewRow__ (currentDate, correctData, correctDataMax, correctDataPeakHour)            
            self.__get_Attributes__ ()

    def update (self, dates, yesterdayLoad, historicalLoad):
        for row in range (len (dates)):            
            historicalLoad.get_HistoricalLoadData (dates [row], yesterdayLoad)
            historicalLoadList = LoadData.__make_HistoricalLoadList__ (historicalLoad, dates [row])
            self.__add_Data__ (historicalLoadList)            
        self.determine_EndDate ()
        return True

    def convert_ToHourly (self):
        hourlyData = pd.DataFrame (columns=['Date', 'Hour', 'LastWeekLoad', 'YesterdayLoad', 'Load'])
        dates = []
        hours = []
        lastWeeks = []
        yesterdays = []
        loads = []
        for i in range (len (self.data)):
            for j in range (1,25):
                dates.append (self.data.loc [i, 'Date'])
                hours.append (j)
                lastWeeks.append (self.data.loc [i, f'LastWeek{j}'])
                yesterdays.append (self.data.loc [i, f'Yesterday Load {j}'])
                loads.append (self.data.loc [i, f'Load{j}'])
        hourlyData ['Date'] = dates
        hourlyData ['Hour'] = hours
        hourlyData ['LastWeekLoad'] = lastWeeks
        hourlyData ['YesterdayLoad'] = yesterdays
        hourlyData ['Load'] = loads
        return hourlyData