from logging import exception
import os
from pahbar.calendarData import CalendarData
from datetime import date
from datetime import timedelta
from pahbar.dayLength import daylength
from pahbar.weatherData import WeatherData
from pahbar.historicalLoad import HistoricalLoad
import pandas as pd
import pickle
from pahbar.predictDay import PredictDay
import copy
from persiantools.jdatetime import JalaliDate
import matplotlib.pyplot as plt

class Output:
    def __init__ (self, predictDates, dataSetHeaders):
        self.predictDates = predictDates
        self.allHeaders = dataSetHeaders
        self.featuresHeaders = dataSetHeaders [:-1]
        self.outputHeaders = ['تاریخ', 'H1','H2','H3','H4','H5','H6','H7','H8','H9','H10','H11','H12','H13','H14','H15','H16','H17','H18','H19','H20','H21','H22','H23','H24']
        self.predictDays = []
        self.predictedDayList = []
        for i in range (len (self.predictDates)):
            self.predictDays.append (PredictDay (self.predictDates [i], self.predictDates [i]))

    def convert_DatatoDict (self, from_date, to_date):
        data = []
        for i in range (len (self.output)):
            if (self.output.loc [i]['تاریخ'] >= from_date) and (self.output.loc [i]['تاریخ'] <= to_date):
                data.append (self.output.iloc [i,:].values.tolist ())
        for i in range (len (data)):
            data [i][0] = JalaliDate (data [i][0]) 
        self.dataDictionary = dict ({'header':self.outputHeaders, 'data': data})    

    def complete_Features (self):
        self.predictDaysFeatures = pd.DataFrame (columns= self.featuresHeaders)
        self.output = pd.DataFrame (columns= self.outputHeaders)
        endDate = None
        self.weatherDataUnavailable = None
        self.calendarDataUnavailable = None

        for d in self.predictDates:
            if d < date.today ():
                continue
            endDate = d - timedelta (days= 1)
            break
        
        if not (endDate):
            endDate = self.predictDates [-1]

        weatherDataHistorical = WeatherData (endDate, self.predictDates [0])
        try:
            weatherDataHistorical.get_WeatherData ()
        except Exception as inst:
            print (inst)
            self.weatherDataUnavailable = 1
            return False
        
        if d >= date.today ():
            weatherDataForecast = WeatherData (self.predictDates [-1], endDate + timedelta (days= 1))
            try:
                weatherDataForecast.get_WeatherData ()
            except Exception as inst:
                print (inst)
                self.weatherDataUnavailable = 1
                return False

        for i in range (len (self.predictDates)): 
            featuresNewRow = []    
            outputNewRow = [] 
            newDate = self.predictDates [i]   
            featuresNewRow.append (newDate)
            outputNewRow.append (newDate)

            self.calendarData = CalendarData (newDate)
            yesterdayCalendarData = CalendarData (newDate - timedelta (days=2))
            lastWeekCalendarData = CalendarData (newDate - timedelta (days=7))
            try:
                self.calendarData.get_CalendarData ()
                yesterdayCalendarData.get_CalendarData ()
                lastWeekCalendarData.get_CalendarData ()
                featuresNewRow.append (self.calendarData.eideMazhabi)
                featuresNewRow.append (self.calendarData.aza)
                featuresNewRow.append (self.calendarData.holiday)
                featuresNewRow.append (yesterdayCalendarData.holiday)
                featuresNewRow.append (lastWeekCalendarData.holiday)
            except Exception as inst:
                print (inst)
                self.calendarDataUnavailable = 1
                return False

            featuresNewRow.append (self.calendarData.dayName)
            featuresNewRow.append (daylength (self.calendarData.date.timetuple().tm_yday, 36.2605))
            featuresNewRow.append (daylength (yesterdayCalendarData.date.timetuple().tm_yday, 36.2605))
            featuresNewRow.append (daylength (lastWeekCalendarData.date.timetuple().tm_yday, 36.2605))

            
            if (self.calendarData.date <= endDate):
                featuresNewRow.append (weatherDataHistorical.allWeatherData [f'{self.calendarData.date.year}-{self.calendarData.date.month}'].values [self.calendarData.date.day - 1][0])
                featuresNewRow.append (weatherDataHistorical.allWeatherData [f'{self.calendarData.date.year}-{self.calendarData.date.month}'].values [self.calendarData.date.day - 1][1])
            else:
                featuresNewRow.append (weatherDataForecast.allWeatherData [(self.calendarData.date - endDate).days - 1][0])
                featuresNewRow.append (weatherDataForecast.allWeatherData [(self.calendarData.date - endDate).days - 1][1])
                        
            for j in range (16 - len (featuresNewRow)):
                featuresNewRow.append ('Not Available')

            featuresNewRow.insert (6, 1)
            for k in range (24):
                featuresNewRow [6] = k + 1
                self.predictDaysFeatures.loc [24 * i + k] = featuresNewRow

        return True

    def add_HistoricalLoadData (self, row):
        for hour in range (24):
            newRow = []
            newRow.append (max (self.predictDays [row].historicalLoad.yesterdayLoad))
            newRow.append (self.predictDays [row].historicalLoad.yesterdayLoad.index (max (self.predictDays [row].historicalLoad.yesterdayLoad)) + 1)
            newRow.append (self.predictDays [row].historicalLoad.lastWeekLoad [hour])
            newRow.append (self.predictDays [row].historicalLoad.yesterdayLoad [hour])        
            for i in range (len (newRow)):
                self.predictDaysFeatures.iloc [24 * row + hour, i + 13] = newRow [i]

    def make_ListOfOneRow (self, row):
        list2 = self.output.iloc [row].values.tolist ()
        for i in range (24):
            list1 = self.predictDaysFeatures.iloc [row * 24 + i].values.tolist ()
            self.predictedDayList.append (list1)
            self.predictedDayList [row * 24 + i].append (list2 [i + 1])
        
        self.predictedLoad = copy.deepcopy (list2)
        self.predictedLoad [0] = JalaliDate (self.predictedLoad [0])
        self.predictedLoad.append (JalaliDate (date.today ()))