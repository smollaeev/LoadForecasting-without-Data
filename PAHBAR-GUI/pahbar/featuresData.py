import calendar
import copy
from datetime import timedelta

import pandas as pd
import pahbar.TimeIrScraping as timeir
from pahbar.calendarData import CalendarData
from pahbar.weatherData import WeatherData

class STFeaturesData:
    def __init__(self, data):
        self.data = self.convert_ToHourly (data)
        self.headers = list (self.data.columns)
        self.__get_Attributes__ ()

    def __get_Attributes__ (self):
        self.numberOfRecords = len (self.data.index)
        self.determine_EndDate ()        

    def __get_Data__ (self, date_, row, headers):
        currentData = self.data.loc [row, headers].to_list () [1:]
        currentData.insert (0, date_)
        return currentData

    def __insert_Data__ (self, features):
        newRow = list (features)
        self.data.loc [len (self.data)] = newRow
        self.numberOfRecords += 1

    def __get_CalendarData__ (dateList):
        calendarDays = timeir.getDays (dateList)
        daysFeatures = []
        for d in calendarDays:
            dayFeatures = []
            d.get_CalendarData ()
            dayFeatures.append (d.eideMazhabi)
            dayFeatures.append (d.aza)
            dayFeatures.append (d.ramezan)
            dayFeatures.append (d.holiday)
            dayFeatures.append (d.dayName)
            dayFeatures.append (d.dayOfYear)
            daysFeatures.append (dayFeatures)
        return daysFeatures

    def __add_CalendarData__ (featuresNewRow, daysFeatures, dateList):
        featuresNewRow.append (daysFeatures [0][0])
        featuresNewRow.append (daysFeatures [0][1])
        featuresNewRow.append (daysFeatures [0][2])
        featuresNewRow.append (daysFeatures [0][3])
        featuresNewRow.append (daysFeatures [1][3])
        featuresNewRow.append (daysFeatures [2][3])
        featuresNewRow.append (daysFeatures [3][3])
        featuresNewRow.append (daysFeatures [4][3])
        featuresNewRow.append (daysFeatures [0][4])
        featuresNewRow.append (daysFeatures [0][5])
        featuresNewRow.append (CalendarData.get_DayLength (dateList [0].timetuple().tm_yday, 36.2605))
        return featuresNewRow

    def __add_WeatherData__ (featuresNewRow, weatherData, newDate):
        featuresNewRow.append (weatherData.allWeatherData [f'{calendar.month_name [newDate.month]}-{newDate.year}'][f'{newDate.day}'][0][0])
        featuresNewRow.append (weatherData.allWeatherData [f'{calendar.month_name [newDate.month]}-{newDate.year}'][f'{newDate.day}'][0][1])
        return featuresNewRow

    def determine_EndDate (self):
        try:
            self.endDate = (self.data.iloc [self.numberOfRecords - 1]['Date'].date ())
        except:
            self.endDate = self.data.iloc [self.numberOfRecords - 1]['Date']

    def get_DataByDate (self, dates, headers):
        data = []
        for date_ in dates:
            for i in range (self.numberOfRecords):
                try:
                    temp = self.data.loc [len (self.data) -1 - i, 'Date'].date ()
                except:
                    temp = self.data.loc [len (self.data) -1 - i, 'Date']
                if temp == date_:
                    data.append (self.__get_Data__ (date_, len (self.data) - 1 - i, headers))
                    break
        return data

    def update (self, dates):
        features = self.get_Features (dates)
        if isinstance (features, bool):
            return False
        for row in range (len (dates)):
            self.__insert_Data__ (features.loc [row].values)            
        self.determine_EndDate ()
        return True

    def get_Features (self, dates):
        features = pd.DataFrame (columns= self.headers)
        self.weatherDataUnavailable = None
        self.calendarDataUnavailable = None
        weatherData = WeatherData (dates [0], dates [-1])
        try:
            weatherData.get_WeatherData ()
        except Exception as inst:
            print (inst)
            self.weatherDataUnavailable = 1
            return False
        for i in range (len (dates)): 
            featuresNewRow = [] 
            try:
                newDate = dates [i].date ()
            except:
                newDate = dates [i]                
            featuresNewRow.append (dates [i])
            dateList = [newDate, newDate - timedelta (days = 1), newDate - timedelta (days=2), newDate - timedelta (days=7), newDate + timedelta (days= 1)]
            try:
                daysFeatures = STFeaturesData.__get_CalendarData__ (dateList)                   
            except Exception as inst:
                print (inst)
                self.calendarDataUnavailable = 1
                return False
            featuresNewRow = STFeaturesData.__add_CalendarData__ (featuresNewRow, daysFeatures, dateList)           
            featuresNewRow = STFeaturesData.__add_WeatherData__ (featuresNewRow, weatherData, newDate)
            featuresNewRows = []
            for j in range (24):
                featuresNewRows.append (copy.deepcopy (featuresNewRow))
                featuresNewRows [j].insert (9, j + 1)
                features.loc [i*24 + j] = featuresNewRows [j]
        return features

    def convert_ToHourly (self, data):
        headers = list (data.columns)
        hourlyHeaders = copy.deepcopy (headers)
        hourlyData = data.loc [data.index.repeat (24)].reset_index (drop = True) [hourlyHeaders]
        hours = []
        for _ in range (len (data.index)):
            hours += range (1, 25)
        hourlyData.insert(loc=9, column='Hour', value=hours)
        return hourlyData


class MTFeaturesData:
    def __init__(self, data):
        self.data = data
        self.headers = list (self.data.columns)
        self.__get_Attributes__ ()

    def __get_Attributes__ (self):
        self.numberOfRecords = len (self.data.index)
        self.determine_EndDate ()        

    def __get_Data__ (self, date_, row, headers):
        currentData = self.data.loc [row, headers].to_list () [1:]
        currentData.insert (0, date_)
        return currentData

    def __insert_Data__ (self, features):
        newRow = list (features)
        self.data.loc [len (self.data)] = newRow
        self.numberOfRecords += 1

    def __get_CalendarData__ (dateList):
        calendarDays = timeir.getDays (dateList)
        daysFeatures = []
        for d in calendarDays:
            dayFeatures = []
            d.get_CalendarData ()
            dayFeatures.append (d.eideMazhabi)
            dayFeatures.append (d.aza)
            dayFeatures.append (d.ramezan)
            dayFeatures.append (d.holiday)
            dayFeatures.append (d.dayName)
            dayFeatures.append (d.dayOfYear)
            daysFeatures.append (dayFeatures)
        return daysFeatures

    def __add_CalendarData__ (featuresNewRow, daysFeatures, dateList):
        featuresNewRow.append (daysFeatures [0][0])
        featuresNewRow.append (daysFeatures [0][1])
        featuresNewRow.append (daysFeatures [0][2])
        featuresNewRow.append (daysFeatures [0][3])
        featuresNewRow.append (daysFeatures [1][3])
        featuresNewRow.append (daysFeatures [2][3])
        featuresNewRow.append (daysFeatures [3][3])
        featuresNewRow.append (daysFeatures [4][3])
        featuresNewRow.append (daysFeatures [0][4])
        featuresNewRow.append (daysFeatures [0][5])
        featuresNewRow.append (CalendarData.get_DayLength (dateList [0].timetuple().tm_yday, 36.2605))
        return featuresNewRow

    def __add_WeatherData__ (featuresNewRow, weatherData, newDate):
        featuresNewRow.append (weatherData.allWeatherData [f'{calendar.month_name [newDate.month]}-{newDate.year}'][f'{newDate.day}'][0][0])
        featuresNewRow.append (weatherData.allWeatherData [f'{calendar.month_name [newDate.month]}-{newDate.year}'][f'{newDate.day}'][0][1])
        return featuresNewRow

    def determine_EndDate (self):
        try:
            self.endDate = (self.data.iloc [self.numberOfRecords - 1]['Date'].date ())
        except:
            self.endDate = self.data.iloc [self.numberOfRecords - 1]['Date']

    def get_DataByDate (self, dates, headers):
        data = []
        for date_ in dates:
            for i in range (self.numberOfRecords):
                try:
                    temp = self.data.loc [len (self.data) -1 - i, 'Date'].date ()
                except:
                    temp = self.data.loc [len (self.data) -1 - i, 'Date']
                if temp == date_:
                    data.append (self.__get_Data__ (date_, len (self.data) - 1 - i, headers))
                    break
        return data

    def update (self, dates):
        features = self.get_Features (dates)
        if isinstance (features, bool):
            return False
        for row in range (len (dates)):
            self.__insert_Data__ (features.loc [row].values)            
        self.determine_EndDate ()
        return True

    def get_Features (self, dates):
        features = pd.DataFrame (columns= self.headers)
        self.weatherDataUnavailable = None
        self.calendarDataUnavailable = None
        weatherData = WeatherData (dates [0], dates [-1])
        try:
            weatherData.get_WeatherData ()
        except Exception as inst:
            print (inst)
            self.weatherDataUnavailable = 1
            return False
        for i in range (len (dates)): 
            featuresNewRow = [] 
            try:
                newDate = dates [i].date ()
            except:
                newDate = dates [i]                
            featuresNewRow.append (dates [i])
            dateList = [newDate, newDate - timedelta (days = 1), newDate - timedelta (days=2), newDate - timedelta (days=7), newDate + timedelta (days= 1)]
            try:
                daysFeatures = MTFeaturesData.__get_CalendarData__ (dateList)                   
            except Exception as inst:
                print (inst)
                self.calendarDataUnavailable = 1
                return False
            featuresNewRow = MTFeaturesData.__add_CalendarData__ (featuresNewRow, daysFeatures, dateList)           
            featuresNewRow = MTFeaturesData.__add_WeatherData__ (featuresNewRow, weatherData, newDate)           
            features.loc [i] = featuresNewRow
        return features