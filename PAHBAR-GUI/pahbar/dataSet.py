from datetime import timedelta, date
from copy import deepcopy
from numpy.lib.function_base import copy
from pahbar.loadData import LoadData
from pahbar.featuresData import STFeaturesData, MTFeaturesData
from pahbar.dates import Dates

class DataSet:
    def __init__ (self, featuresData, loadData):
        self.featuresData = MTFeaturesData (featuresData)
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

    def __get_HeadersForDisplay__(self):
        result = ['Date', 'Eide Mazhabi', 'Aza', 'Holiday', 'DayName', 'MaximumTemperature', 'AverageTemperature']
        for hour in range (1, 25):
            result.append (f'Load{hour}')
        result.append ('MaxLoad')
        result.append ('PeakHour')
        return (result)

    def __remove_InvalidDates__ (self, dates):
        if dates [-1].to_gregorian () > self.endDate:
            while (dates [-1] != self.endDate):
                dates.pop ()
        return dates
    
    def __prepare_DataToDisplay__(data):
        return [
            data[i][:5] + data[i][8:11] + data[i][13:15] + data[i][-26:-2]
            for i in range(len(data))
        ]

    def __get_DataForDisplay__(self, fromDate, toDate, headers):
        dates = Dates.make_ListOfDates (fromDate, toDate, jalali = True)
        dates = self.__remove_InvalidDates__ (dates)
        return self.get_DataByDate (dates, headers)

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

    def __get_ValidHeadersForDisplay__(self, requestedHeaders, allHeaders):
        validHeaders = deepcopy (requestedHeaders)
        invalidNames = [header for header in validHeaders if header not in allHeaders]
        for invalidName in invalidNames:
            validHeaders.remove (invalidName)
        return validHeaders

    def determine_EndDate (self):
        self.endDate = self.featuresData.endDate

    def get_DataDictionaryToDisplay(self, fromDate, toDate):
        data = []
        headers = self.__get_HeadersForDisplay__ ()
        data = self.__get_DataForDisplay__ (fromDate, toDate, headers)
        return dict ({'header':headers, 'data': data})

    def edit_LoadData(self, newLoadData):
        if self.__is_InvalidEditDate__ (newLoadData):
            return dict(
                {
                    'English': 'Invalid dates in your data!',
                    'Farsi': 'در اطلاعات وارد شده، تاریخ‌های غیرقابل قبول وجود دارد!',
                }
            )

        self.loadData.replace_Data (newLoadData)
        return True
    
    def get_DataByDate (self, dates, headers):
        data = []
        featuresHeaders = self.__get_ValidHeadersForDisplay__ (headers, self.featuresData.headers)
        loadHeaders = self.__get_ValidHeadersForDisplay__ (headers, self.loadData.headers)
        featuresData = self.featuresData.get_DataByDate (dates, featuresHeaders)
        loadData = self.loadData.get_DataByDate (dates, loadHeaders)
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