import requests
from hijri_converter import convert
import json
from datetime import timedelta

class CalendarData:
    eideMazhabiOccasions = ['ولادت حضرت علی (ع)', 'مبعث حضرت محمد (ص)', 'ولادت حضرت مهدی (عج)', 'عید فطر', 'عید قربان', 'عید غدیر خم', 'ولادت حضرت محمد (ص)', 'ولادت امام جعفر صادق (ع)']
    azaOccasions = ['شهادت حضرت علی (ع)' , 'شهادت امام جعفر صادق (ع)' , 'اربعین حسینی' , 'شهادت امام حسن مجتبی (ع)' , 'رحلت حضرت محمد (ص)' , 'شهادت امام حسن عسگری (ع)' , 'شهادت حضرت فاطمه زهرا (س)']
    def __init__ (self, date):
        self.date = date

    def get_CalendarData (self):
        self.holiday = 0
        self.eideMazhabi = 0
        self.aza = 0

        self.dayName = self.date.strftime ('%A')
        if self.dayName == 'Friday':
            self.holiday = 1

        self.jalaliYear, self.jalaliMonth, self.jalaliDay = self.convert_ToShamsi ()        
        response = requests.get (f'https://farsicalendar.com/api/sh/{self.jalaliDay}/{self.jalaliMonth}')
        self.jsonResponseShamsi = json.loads (response.text)

        self.hijriDate = convert.Gregorian(self.date.year, self.date.month, self.date.day).to_hijri()
        response = requests.get (f'https://farsicalendar.com/api/ic/{self.hijriDate.day}/{self.hijriDate.month}')
        self.jsonResponseGhamari = json.loads (response.text)

        if self.is_Holiday ():
            self.holiday = 1 

        if self.is_EideMazhabi ():
            self.eideMazhabi = 1  

        if self.is_Aza ():
            self.aza = 1

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

        if (self.hijriDate.month == 10) and (self.hijriDate.day == 2):
            return True

        return False

    def is_EideMazhabi (self):
        if self.jsonResponseGhamari['values']:
            for i in range (len (self.jsonResponseGhamari ['values'])):
                if (self.jsonResponseGhamari ['values'][i]['occasion'] in self.eideMazhabiOccasions) or ((self.hijriDate.month == 10) and (self.hijriDate.day == 2)):
                    return True
        
        return False
    
    def is_Aza (self):
        if self.jsonResponseGhamari['values']:
            for i in range (len (self.jsonResponseGhamari ['values'])):
                if (self.jsonResponseGhamari ['values'][i]['occasion'] in self.azaOccasions) or ((self.hijriDate.month == 1) and (1 <= self.hijriDate.day <= 10)) or (self.is_LastDayOfSafar ()):
                    return True
        
        return False

    def convert_ToShamsi (self):
        gy = self.date.year
        gm = self.date.month
        gd = self.date.day

        g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        if (gm > 2):
            gy2 = gy + 1
        else:
            gy2 = gy
        days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
        jy = -1595 + (33 * (days // 12053))
        days %= 12053
        jy += 4 * (days // 1461)
        days %= 1461
        if (days > 365):
            jy += (days - 1) // 365
            days = (days - 1) % 365
        if (days < 186):
            jm = 1 + (days // 31)
            jd = 1 + (days % 31)
        else:
            jm = 7 + ((days - 186) // 30)
            jd = 1 + ((days - 186) % 30)
        return jy, jm, jd

    def is_LastDayOfSafar (self):
        if (self.hijriDate.month == 2) and (convert.Gregorian ((self.date + timedelta (days= 1)).year, (self.date + timedelta (days= 1)).month, (self.date + timedelta (days= 1)).day).to_hijri().month == 3):
            return True