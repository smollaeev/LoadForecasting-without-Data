import pandas as pd
from pahbar.weatherData import WeatherData
from datetime import timedelta
import pahbar.TimeIrScraping as timeir
from pahbar.calendarData import CalendarData
import calendar

class Features:
    def get_Features (self, dates, featuresNames):
        features = pd.DataFrame (columns= featuresNames)
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
            dateList = [newDate, newDate - timedelta (days=2), newDate - timedelta (days=7), newDate + timedelta (days= 1)]
            
            try:
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
                    
            except Exception as inst:
                print (inst)
                self.calendarDataUnavailable = 1
                return False

            featuresNewRow.append (daysFeatures [0][0])
            featuresNewRow.append (daysFeatures [0][1])
            featuresNewRow.append (daysFeatures [0][2])
            featuresNewRow.append (daysFeatures [0][3])
            featuresNewRow.append (daysFeatures [1][3])
            featuresNewRow.append (daysFeatures [2][3])
            featuresNewRow.append (daysFeatures [3][3])

            featuresNewRow.append (daysFeatures [0][4])
            featuresNewRow.append (daysFeatures [0][5])
            featuresNewRow.append (CalendarData.calculate_DayLength (dateList [0].timetuple().tm_yday, 36.2605))
            featuresNewRow.append (CalendarData.calculate_DayLength (dateList [1].timetuple().tm_yday, 36.2605))
            featuresNewRow.append (CalendarData.calculate_DayLength (dateList [2].timetuple().tm_yday, 36.2605))

            featuresNewRow.append (weatherData.allWeatherData [f'{calendar.month_name [newDate.month]}-{newDate.year}'][f'{newDate.day}'][0][0])
            featuresNewRow.append (weatherData.allWeatherData [f'{calendar.month_name [newDate.month]}-{newDate.year}'][f'{newDate.day}'][0][1])

            features.loc [i] = featuresNewRow

        return features