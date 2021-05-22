import requests
import json
from datetime import date
import pandas as pd
import numpy as np

class CalendarData:
    daysTillTheFirstDayOfMonth = {'1':0, '2': 31, '3': 62, '4': 93, '5': 124, '6': 155, '7': 186, '8': 216, '9': 246, '10': 276, '11': 306, '12': 336}
    eideMazhabiOccasions = ['ولادت حضرت علی (ع)', 'مبعث حضرت محمد (ص)', 'ولادت حضرت مهدی (عج)', 'عید فطر', 'عید قربان', 'عید غدیر خم', 'ولادت حضرت محمد (ص)', 'ولادت امام جعفر صادق (ع)']
    azaOccasions = ['شهادت حضرت علی (ع)' , 'شهادت امام جعفر صادق (ع)' , 'اربعین حسینی' , 'شهادت امام حسن مجتبی (ع)' , 'رحلت حضرت محمد (ص)' , 'شهادت امام حسن عسگری (ع)' , 'شهادت حضرت فاطمه زهرا (س)']

    def __init__ (self, miladiDate, shamsiDateList, ghamariDateList, datesDataFile = None):
        self.date = miladiDate
        self.jalaliMonth = shamsiDateList [1]
        self.jalaliDay = shamsiDateList [2]
        self.hijriMonth = ghamariDateList [1]
        self.hijriDay = ghamariDateList [2]

    def __get_ShamsiAndGhamariDate_FromFile__ (self, datesDataFile):
        shamsiAndGhamariDate = {}
        datesData = pd.read_excel (datesDataFile, engine='openpyxl', index_col=0)
        for j in range (len (datesData)):
            newDateList = list (map (int, datesData.loc [j, 'Miladi'].split (sep='/')))
            newDate = date (newDateList [0], newDateList [1], newDateList [2])
            if  self.date == newDate:
                shamsiAndGhamariDate ['Shamsi'] = list (map (int, datesData.loc [j, 'Shamsi'].split (sep = '/')))
                shamsiAndGhamariDate ['Ghamari'] = list (map (int, datesData.loc [j, 'Ghamari'].split (sep = '/')))
                return shamsiAndGhamariDate

    def __is_Holiday__ (self, jsonResponseShamsi, jsonResponseGhamari):
        if jsonResponseShamsi ['values']:
            for i in range (len (jsonResponseShamsi['values'])):
                temp1 = jsonResponseShamsi['values'][i]['dayoff']
                if temp1 == True:
                    return True

        if jsonResponseGhamari['values']:
            for i in range (len (jsonResponseGhamari ['values'])):
                temp2 = jsonResponseGhamari ['values'][i]['dayoff']
                if  temp2 == True:
                    return True

        return False

    def __is_EideMazhabi__ (self, jsonResponseGhamari):
        if jsonResponseGhamari['values']:
            for i in range (len (jsonResponseGhamari ['values'])):
                if (jsonResponseGhamari ['values'][i]['occasion'] in self.eideMazhabiOccasions) or ((self.hijriMonth == 10) and (self.hijriDay == 2)):
                    return True
        
        return False
    
    def __is_Aza__ (self, jsonResponseGhamari):
        if jsonResponseGhamari['values']:
            for i in range (len (jsonResponseGhamari ['values'])):
                if (jsonResponseGhamari ['values'][i]['occasion'] in self.azaOccasions) or ((self.hijriMonth == 1) and (1 <= self.hijriDay <= 10)) or (self.__is_LastDayOfSafar__ ()):
                    return True
        
        return False

    def __is_Ramezan__ (self):
        if (self.hijriMonth == 9):
            return True

    def __is_LastDayOfSafar__ (self):
        if (self.hijriMonth == 2) and (self.hijriMonthTomorrow == 3):
            return True

    def __determine_DayOfYear__ (self):
        self.dayOfYear = self.daysTillTheFirstDayOfMonth [str (self.jalaliMonth)] + self.jalaliDay

    def calculate_DayLength(dayOfYear, lat):
        """Computes the length of the day (the time between sunrise and
        sunset) given the day of the year and latitude of the location.
        Function uses the Brock model for the computations.
        For more information see, for example,
        Forsythe et al., "A model comparison for daylength as a
        function of latitude and day of year", Ecological Modelling,
        1995.
        Parameters
        ----------
        dayOfYear : int
            The day of the year. 1 corresponds to 1st of January
            and 365 to 31st December (on a non-leap year).
        lat : float
            Latitude of the location in degrees. Positive values
            for north and negative for south.
        Returns
        -------
        d : float
            Daylength in hours.
        """
        latInRad = np.deg2rad(lat)
        declinationOfEarth = 23.45*np.sin(np.deg2rad(360.0*(283.0+dayOfYear)/365.0))
        if -np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth)) <= -1.0:
            return 24.0
        elif -np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth)) >= 1.0:
            return 0.0
        else:
            hourAngle = np.rad2deg(np.arccos(-np.tan(latInRad) * np.tan(np.deg2rad(declinationOfEarth))))
            return 2.0*hourAngle/15.0

    def get_CalendarData (self):
        self.holiday = 0
        self.eideMazhabi = 0
        self.aza = 0
        self.ramezan = 0

        self.dayName = self.date.strftime ('%A')
        if self.dayName == 'Friday':
            self.holiday = 1

        for i in range (3):
            try:
                response = requests.get (f'https://farsicalendar.com/api/sh/{self.jalaliDay}/{self.jalaliMonth}',verify=False)
                jsonResponseShamsi = json.loads (response.text)
                break
            except:
                continue
        
        for i in range (3):
            try:
                response = requests.get (f'https://farsicalendar.com/api/ic/{self.hijriDay}/{self.hijriMonth}',verify=False)
                jsonResponseGhamari = json.loads (response.text)
                break
            except:
                continue

        if self.__is_Holiday__ (jsonResponseShamsi, jsonResponseGhamari):
            self.holiday = 1

        if self.__is_EideMazhabi__ (jsonResponseGhamari):
            self.eideMazhabi = 1  

        if self.__is_Aza__ (jsonResponseGhamari):
            self.aza = 1

        if self.__is_Ramezan__ ():
            self.ramezan = 1

        self.__determine_DayOfYear__ ()