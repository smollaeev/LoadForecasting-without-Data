from datetime import timedelta
class LoadData:
    def __init__ (self, data):
        self.data = data
        self.headers = list (self.data.columns) [:-1]
        self.__get_Attributes__ ()

    def __get_Attributes__ (self):
        self.numberOfRecords = len (self.data.index)
        self.determine_EndDate ()

    def __get_HeadersForDisplay__ (self):
        headers = self.headers
        return headers

    def __get_Data__ (self, date_):
        currentData = []
        for i in range (self.numberOfRecords):
            try:
                temp = self.data.loc [len (self.data) -1 - i, 'Date'].date ()
            except:
                temp = self.data.loc [len (self.data) -1 - i, 'Date']
            if temp == date_:
                currentData = self.data.loc [len (self.data) - 1 - i].to_list ()
                currentData.pop ()
                break
        return currentData

    def get_DataByDate (self, dates):
        data = []
        for date_ in dates:
            newData = self.__get_Data__ (date_)
            if newData:
                data.append (newData)
        return data

    def determine_EndDate (self):
        try:
            self.endDate = (self.data.iloc [self.numberOfRecords - 1]['Date'].date ())
        except:
            self.endDate = self.data.iloc [self.numberOfRecords - 1]['Date']

    def replace_Data (self, newData):
        for row in range (len (newData.index)):
            currentDate = newData.iloc [row]['تاریخ']
            correctData = newData.iloc [row]['H1':'H24'].values.tolist ()
            correctDataMax = max (correctData)
            correctDataPeakHour = correctData.index (correctDataMax) + 1
            for i in range (self.numberOfRecords):
                try:
                    dataSetDate = self.data.iloc [self.numberOfRecords - i - 1]['Date'].date ()
                except:
                    dataSetDate = self.data.iloc [self.numberOfRecords - i - 1]['Date']
                if  dataSetDate== currentDate:
                    self.data.loc [self.numberOfRecords - i - 1, 'Load1':'Load24'] = correctData
                    self.data.loc [self.numberOfRecords - i - 1, 'MaxLoad'] = correctDataMax
                    self.data.loc [self.numberOfRecords - i - 1, 'PeakHour'] = correctDataPeakHour

                if dataSetDate == currentDate + timedelta (days=2):
                    self.data.loc [self.numberOfRecords - i - 1, 'Yesterday Load 1':'Yesterday Load 24'] = correctData
                    self.data.loc [self.numberOfRecords - i - 1, 'PeakLoadYesterday'] = correctDataMax
                    self.data.loc [self.numberOfRecords - i - 1, 'PeakHourYesterday'] = correctDataPeakHour

                if dataSetDate == currentDate + timedelta (days=7):
                    self.data.loc [self.numberOfRecords - i - 1, 'LastWeek1':'LastWeek24'] = correctData
                    break
            self.__get_Attributes__ ()

    def update (self, dates, yesterdayLoad, historicalLoad):
        for row in range (len (dates)):
            historicalLoadList = []
            historicalLoad.get_HistoricalLoadData (dates [row], yesterdayLoad)
            historicalLoadList.append (max (historicalLoad.yesterdayLoad))
            historicalLoadList.append (historicalLoad.yesterdayLoad.index (max (historicalLoad.yesterdayLoad)) + 1)
            historicalLoadList += historicalLoad.lastWeekLoad
            historicalLoadList += historicalLoad.yesterdayLoad
            historicalLoadList += historicalLoad.load 
            historicalLoadList.append (max (historicalLoad.load))
            historicalLoadList.append (historicalLoad.load.index(max(historicalLoad.load)) + 1)
            historicalLoadList.append (dates [row])
            self.data.loc [len (self.data)] = historicalLoadList
            self.numberOfRecords += 1
        self.determine_EndDate ()
        return True