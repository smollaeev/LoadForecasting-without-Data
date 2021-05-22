from persiantools.jdatetime import JalaliDate
from datetime import timedelta, date
from pahbar.features import Features

class DataSet:
    def __init__ (self, data):
        self.data = data
        self.headers = list (self.data.columns)
        self.featuresHeaders = self.headers [:-76]
        self.loadFeaturesHeaders = self.headers [-76:-26]
        self.hoursHeaders = []
        for i in range (1, 25):
            self.hoursHeaders.append (f'H{i}')
        self.__update_Attributes__ ()

    def __update_Attributes__ (self):
        self.numberOfRecords = len (self.data.index)
        self.determine_EndDate ()

    def determine_EndDate (self):
        self.endDate = (self.data.iloc [self.numberOfRecords - 1]['Date'].date ())

    def convert_DatatoDict (self, from_date, to_date):
        data = []
        headers = self.headers [:5] + self.headers [8:11] + self.headers [13:15] + self.hoursHeaders

        for i in range (len (self.data)):
            dataSetDate = self.data.loc [i, 'Date'].date ()

            if (dataSetDate >= from_date) and (dataSetDate <= to_date):
                data.append (self.data.iloc [i,:5].values.tolist () + self.data.iloc [i, 8:11].values.tolist () + self.data.iloc [i, 13:15].values.tolist () + self.data.iloc [i, -26:-2].values.tolist ())           

        for i in range (len (data)):
            data [i][0] = JalaliDate (data [i][0])
        
        self.dataDictionary = dict ({'header':headers, 'data': data})

    def edit_Data (self, newLoadData):
        for i in range (len (newLoadData)):
            try:
                newLoadData.loc [i, 'تاریخ'] = newLoadData.loc [i, 'تاریخ'].to_gregorian ()
            except Exception as inst:
                print (inst)
        
        self.invalidEditDate = 0     
        for row in range (len (newLoadData.index)):
            currentDate = newLoadData.iloc [row]['تاریخ']
            if (currentDate > self.endDate) or (currentDate < self.data.iloc [0]['Date'].date ()):
                self.invalidEditDate += 1
                break
            correctData = newLoadData.iloc [row]['H1':'H24'].values.tolist ()
            correctDataMax = max (correctData)
            correctDataPeakHour = correctData.index (correctDataMax) + 1
            for i in range (self.numberOfRecords):
                dataSetDate = self.data.iloc [self.numberOfRecords - i - 1]['Date'].date ()
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
            self.__update_Attributes__ ()
        
        if not (self.invalidEditDate):
            return True
        else:
            result = dict ({'English':'Invalid dates in your data!', 'Farsi':'در اطلاعات وارد شده، تاریخ‌های غیرقابل قبول وجود دارد!'})
            return result
    
    def get_DataByDate (self, dates):
        self.actualValues = []
        for date in dates:
            for i in range (len (self.data)):
                temp = self.data.loc [len (self.data) -1 - i, 'Date'].date ()
                if JalaliDate (temp) == date:
                    load = self.data.loc [len (self.data) - 1 - i, 'Load1':'Load24'].to_list ()                    
                    self.actualValues.append (['Actual'] + [date] + load)
                    break

    def update (self, yesterdayLoad, historicalLoad, stopDate):    
        self.newDaysFeatures = Features ()
        d = (self.data.iloc [self.numberOfRecords - 1]['Date']) + timedelta (days = 1)
        dates = []
        while d.date () != stopDate + timedelta (days=1):
            if d.date () != date.today () - timedelta (days = 1):
                dates.append (d)
            d += timedelta (days=1)
            
        features = self.newDaysFeatures.get_Features (dates, self.featuresHeaders)
        if isinstance (features, bool):
            return False
 
        for row in range (len (dates)):
            historicalLoadList = []
            historicalLoad.get_HistoricalLoadData (dates [row], yesterdayLoad)
            historicalLoadList.append (max (historicalLoad.yesterdayLoad))
            historicalLoadList.append (historicalLoad.yesterdayLoad.index (max (historicalLoad.yesterdayLoad)) + 1)
            historicalLoadList += historicalLoad.lastWeekLoad
            historicalLoadList += historicalLoad.yesterdayLoad
            historicalLoadList += historicalLoad.load         

            newRow = list (features.loc [row].values)
            newRow.extend (historicalLoadList)
            newRow.append (max (historicalLoad.load))
            newRow.append (historicalLoad.load.index(max(historicalLoad.load)) + 1)

            self.data.loc [len (self.data)] = newRow
            
            self.numberOfRecords += 1

        self.determine_EndDate ()

        return True