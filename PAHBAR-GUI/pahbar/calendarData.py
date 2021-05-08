import requests
from hijri_converter import convert
import json
from datetime import date, timedelta, datetime
from pahbar.TimeIrScraping import getDay
import pandas as pd

class CalendarData:
    daysTillTheFirstDayOfMonth = {'1':0, '2': 31, '3': 62, '4': 93, '5': 124, '6': 155, '7': 186, '8': 216, '9': 246, '10': 276, '11': 306, '12': 336}
    eideMazhabiOccasions = ['ولادت حضرت علی (ع)', 'مبعث حضرت محمد (ص)', 'ولادت حضرت مهدی (عج)', 'عید فطر', 'عید قربان', 'عید غدیر خم', 'ولادت حضرت محمد (ص)', 'ولادت امام جعفر صادق (ع)']
    azaOccasions = ['شهادت حضرت علی (ع)' , 'شهادت امام جعفر صادق (ع)' , 'اربعین حسینی' , 'شهادت امام حسن مجتبی (ع)' , 'رحلت حضرت محمد (ص)' , 'شهادت امام حسن عسگری (ع)' , 'شهادت حضرت فاطمه زهرا (س)']
    def __init__ (self, miladiDate, datesDataFile = None):
        self.date = miladiDate
        if datesDataFile:
            shamsiAndGhamariDate = self.__get_ShamsiAndGhamariDate_FromFile (datesDataFile)
        else:
            shamsiAndGhamariDate = getDay (miladiDate)

        self.jalaliMonth = shamsiAndGhamariDate ['Shamsi'][1]
        self.jalaliDay = shamsiAndGhamariDate ['Shamsi'][2]

        self.hijriMonth = shamsiAndGhamariDate ['Ghamari'][1]
        self.hijriDay = shamsiAndGhamariDate ['Ghamari'][2]

    def __get_ShamsiAndGhamariDate_FromFile (self, datesDataFile):
        shamsiAndGhamariDate = {}
        datesData = pd.read_excel (datesDataFile, engine='openpyxl', index_col=0)
        for j in range (len (datesData)):
            newDateList = list (map (int, datesData.loc [j, 'Miladi'].split (sep='/')))
            newDate = date (newDateList [0], newDateList [1], newDateList [2])
            if  self.date == newDate:
                shamsiAndGhamariDate ['Shamsi'] = list (map (int, datesData.loc [j, 'Shamsi'].split (sep = '/')))
                shamsiAndGhamariDate ['Ghamari'] = list (map (int, datesData.loc [j, 'Ghamari'].split (sep = '/')))
                return shamsiAndGhamariDate

    def get_CalendarData (self):
        self.holiday = 0
        self.eideMazhabi = 0
        self.aza = 0

        self.dayName = self.date.strftime ('%A')
        if self.dayName == 'Friday':
            self.holiday = 1

        for i in range (3):
            try:
                response = requests.get (f'https://farsicalendar.com/api/sh/{self.jalaliDay}/{self.jalaliMonth}',verify=False)
                self.jsonResponseShamsi = json.loads (response.text)
                break
            except:
                continue
        
        for i in range (3):
            try:
                response = requests.get (f'https://farsicalendar.com/api/ic/{self.hijriDay}/{self.hijriMonth}',verify=False)
                self.jsonResponseGhamari = json.loads (response.text)
                break
            except:
                continue

        if self.is_Holiday ():
            self.holiday = 1 

        if self.is_EideMazhabi ():
            self.eideMazhabi = 1  

        if self.is_Aza ():
            self.aza = 1

        self.determine_DayOfYear ()

    def is_Holiday (self):
        if self.jsonResponseShamsi ['values']:
            for i in range (len (self.jsonResponseShamsi['values'])):
                temp1 = self.jsonResponseShamsi['values'][i]['dayoff']
                if temp1 == True:
                    return True

        if self.jsonResponseGhamari['values']:
            for i in range (len (self.jsonResponseGhamari ['values'])):
                temp2 = self.jsonResponseGhamari ['values'][i]['dayoff']
                if  temp2 == True:
                    return True

        return False

    def is_EideMazhabi (self):
        if self.jsonResponseGhamari['values']:
            for i in range (len (self.jsonResponseGhamari ['values'])):
                if (self.jsonResponseGhamari ['values'][i]['occasion'] in self.eideMazhabiOccasions) or ((self.hijriMonth == 10) and (self.hijriDay == 2)):
                    return True
        
        return False
    
    def is_Aza (self):
        if self.jsonResponseGhamari['values']:
            for i in range (len (self.jsonResponseGhamari ['values'])):
                if (self.jsonResponseGhamari ['values'][i]['occasion'] in self.azaOccasions) or ((self.hijriMonth == 1) and (1 <= self.hijriDay <= 10)) or (self.is_LastDayOfSafar ()):
                    return True
        
        return False

    # def convert_ToShamsi (self):
    #     gy = self.date.year
    #     gm = self.date.month
    #     gd = self.date.day

    #     g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    #     if (gm > 2):
    #         gy2 = gy + 1
    #     else:
    #         gy2 = gy
    #     days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    #     jy = -1595 + (33 * (days // 12053))
    #     days %= 12053
    #     jy += 4 * (days // 1461)
    #     days %= 1461
    #     if (days > 365):
    #         jy += (days - 1) // 365
    #         days = (days - 1) % 365
    #     if (days < 186):
    #         jm = 1 + (days // 31)
    #         jd = 1 + (days % 31)
    #     else:
    #         jm = 7 + ((days - 186) // 30)
    #         jd = 1 + ((days - 186) % 30)
    #     return jy, jm, jd

    def is_LastDayOfSafar (self):
        if (self.hijriMonth == 2) and (getDay (self.date + timedelta (days=1)) ['Ghamari'][1] == 3):
            return True

    def determine_DayOfYear (self):
        self.dayOfYear = self.daysTillTheFirstDayOfMonth [str (self.jalaliMonth)] + self.jalaliDay