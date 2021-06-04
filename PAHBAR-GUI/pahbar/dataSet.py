from datetime import timedelta, date
from pahbar.loadData import LoadData
from pahbar.featuresData import FeaturesData
from pahbar.dates import Dates

class DataSet:
    def __init__ (self, featuresData, loadData):
        self.featuresData = FeaturesData (featuresData)
        self.loadData = LoadData (loadData)
        self.__update_Headers__ ()   
        self.__update_Attributes__ ()

    def __update_Headers__ (self):
        self.headers = self.featuresData.headers + self.loadData.headers
        self.hoursHeaders = []
        for i in range (1, 25):
            self.hoursHeaders.append (f'H{i}')

    def __update_Attributes__ (self):
        self.numberOfRecords = self.featuresData.numberOfRecords
        self.determine_EndDate ()

    def __get_HeadersForDisplay__ (self):
        headers = self.headers [:5] + self.headers [8:11] + self.headers [13:15] + self.hoursHeaders
        return headers

    def __remove_InvalidDates__ (self, dates):
        if dates [-1].to_gregorian () > self.endDate:
            while (dates [-1] != self.endDate):
                dates.pop ()
        return dates
    
    def __prepare_DataToDisplay__ (data):
        result = []
        for i in range (len (data)):
            result.append (data [i][:5] + data [i][8:11] + data [i][13:15] + data [i][-26:-2])
        return result

    def __get_DataForDisplay__ (self, fromDate, toDate):
        dates = Dates.make_ListOfDates (fromDate, toDate, jalali = True)
        dates = self.__remove_InvalidDates__ (dates)        
        data = self.get_DataByDate (dates)
        data = DataSet.__prepare_DataToDisplay__ (data)
        return data

    def __is_InvalidEditDate__ (self, data):
        for row in range (len (data.index)):
            currentDate = data.iloc [row]['تاریخ']
            if (currentDate > self.endDate) or (currentDate < self.featuresData.data.iloc [0]['Date'].date ()):
                return True
        return False

    def __determine_UpdateDates__ (self, stopDate):
        startDate = self.featuresData.endDate + timedelta (days = 1)
        dates = []
        while startDate != stopDate + timedelta (days=1):
            if startDate != date.today () - timedelta (days = 1):
                dates.append (startDate)
            startDate += timedelta (days=1)
        return dates

    def determine_EndDate (self):
        self.endDate = self.featuresData.endDate

    def get_DataDictionaryToDisplay (self, fromDate, toDate):
        data = []
        headers = self.__get_HeadersForDisplay__ ()  
        data = self.__get_DataForDisplay__ (fromDate, toDate)        
        dataDictionary = dict ({'header':headers, 'data': data})
        return dataDictionary

    def edit_LoadData (self, newLoadData):
        if self.__is_InvalidEditDate__ (newLoadData):
            result = dict ({'English':'Invalid dates in your data!', 'Farsi':'در اطلاعات وارد شده، تاریخ‌های غیرقابل قبول وجود دارد!'})
            return result
        self.loadData.replace_Data (newLoadData)
        return True
    
    def get_DataByDate (self, dates):
        data = []
        featuresData = self.featuresData.get_DataByDate (dates)
        loadData = self.loadData.get_DataByDate (dates)
        for i in range (len (dates)):
            try:
                data.append (featuresData [i] + loadData [i])
            except:
                pass
        return data

    def update (self, yesterdayLoad, historicalLoad, stopDate): 
        dates = self.__determine_UpdateDates__ (stopDate)
        featureUpdateSuccess = self.featuresData.update (dates)
        if not (featureUpdateSuccess):
            return False
        historicalLoadUpdateSuccess = self.loadData.update (dates, yesterdayLoad, historicalLoad) 
        if not (historicalLoadUpdateSuccess):
            return False
        self.__update_Attributes__ ()
        return True