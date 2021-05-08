from os import sep
from typing import Collection
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from random import randint
from pahbar.temperatureData import Temperature
from datetime import date
import re
import calendar
from selenium.webdriver.support.ui import WebDriverWait
import collections
from selenium.webdriver.common.by import By

class WeatherData:
    def __init__ (self, endDate, startingDate):
        self.startingDate = startingDate
        self.endDate = endDate
        if self.startingDate:
            self.numberOfMonths = (self.endDate.year - self.startingDate.year) * 12 + (self.endDate.month - self.startingDate.month) + 1
            self.yearList = range (self.startingDate.year, self.endDate.year + 1)
        else:
            self.numberOfMonths = 0
            self.yearList = [self.endDate.year]

        self.__make_ListOfMonthNames ()
        self.__get_MonthYearList ()

    def __get_DailyTemp (self, dayData):
        maxTemp = float (dayData.find ('div', {'class' : 'high'}).string.strip () [:-1])
        minTemp = float (dayData.find ('div', {'class' : 'low'}).string.strip () [:-1])
        avgTemp = (maxTemp+minTemp)/2
        return maxTemp, avgTemp

    def __get_MonthYearList (self):
        self.monthYearList = []
        j = 0
        for i in range (len (self.monthNames)):
            if i == 0:
                self.monthYearList.append ({'month': self.monthNames [i], 'year':self.yearList [j]})
            else:
                if (self.monthNames [i - 1] != 'December'):
                    self.monthYearList.append ({'month': self.monthNames [i], 'year': self.yearList [j]})
                else:
                    j += 1
                    self.monthYearList.append ({'month': self.monthNames [i], 'year': self.yearList [j]})                

    def __make_ListOfMonthNames (self):
        self.monthNames = []
        
        if self.startingDate:
            startMonth = self.startingDate.month
        else:
            startMonth = self.endDate.month
        endMonth = self.endDate.month
        if self.numberOfMonths >= (12 - startMonth):
            self.monthNumbers = list (range (startMonth, 13))
            for i in range (1, self.numberOfMonths + 1 - len (self.monthNumbers)):
                if i%12 == 0:
                    self.monthNumbers.append (12)
                else:
                    self.monthNumbers.append (i%12)
        else:
            self.monthNumbers = list (range (startMonth, endMonth + 1))
        
        for monthNumber in self.monthNumbers:
            self.monthNames.append (calendar.month_name[monthNumber])

    def get_WeatherData (self):
        missingDataDates = collections.defaultdict (list)
        self.allWeatherData = collections.defaultdict (list)
        for m in self.monthYearList:
            url = f'https://www.accuweather.com/en/ir/mashhad/209737/{m["month"]}-weather/209737?year={m["year"]}'

            # options = webdriver.ChromeOptions ()
            # options.add_argument ("--headless")
            # browser = webdriver.Chrome (options = options)
            browser = webdriver.Chrome ()
            browser.get (url)
            try:
                browser.find_element_by_css_selector('body > div.fc-consent-root > div.fc-dialog-container > div.fc-dialog.fc-choice-dialog > div.fc-footer-buttons-container > div.fc-footer-buttons > button.fc-button.fc-cta-consent.fc-primary-button').click ()
            except:
                pass
            try:
                browser.find_element_by_css_selector ('#privacy-policy-banner > div > div').click ()
            except:
                pass

            soup = BeautifulSoup (browser.page_source, 'lxml')
            browser.quit ()
            table = soup.find('div', {'class' : 'monthly-calendar'})
            daysData = table.find_all ('a')
            datesAndTemperature = collections.defaultdict (list)
            for i, d in enumerate (daysData):
                date_ = int (d.find ('div', {'class': 'date'}).string)
                if (date_ != 1 and len(datesAndTemperature) <1):
                    continue
                elif date_ == 1 and len (datesAndTemperature) > 1:
                    break
                else:
                    try:
                        dailyTemp = self.__get_DailyTemp (d)
                        datesAndTemperature [f'{date_}'].append ([dailyTemp [0], dailyTemp [1]]) 
                    except:
                        missingDataDate = date (m ['year'], m ['month'], date_)
                        missingDataDates[f'{missingDataDate.year}-{missingDataDate.month}'].append (date_)
                        
            if len (missingDataDates) > 0:
                missingMonthData = self.get_WeatherData_FromWunderGround (missingDataDates)
                for d in missingDataDates.values ():
                    datesAndTemperature [f'{d}'].append (missingMonthData.values () [d])                        

            self.allWeatherData [f"{m['month']}-{m['year']}"] = datesAndTemperature

    def get_WeatherData_FromWunderGround(self, missingDataDatesDict):
        allWeatherData = {}
        endDate = list (missingDataDatesDict) [-1]
        startingDate = list (missingDataDatesDict) [0]
        if endDate < date.today ():
            for yearMonth in missingDataDatesDict.keys ():                
                url = f'https://www.wunderground.com/history/monthly/ir/mashhad/OIMM/date/{yearMonth}'

                bi = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
                browser = webdriver.Firefox(firefox_binary=bi)
                browser.get(url)
                sleep(randint(10, 12))

                soup = BeautifulSoup (browser.page_source, 'lxml')
                browser.quit ()
                tables = soup.find_all('table', {'class' : 'days ng-star-inserted'})

                table = tables [0]

                allRows = []
                tableHead = ['Max', 'Avg', 'Min']            

                rows = table.findAll('tr')
                for j in range (1, len (rows)):
                    tableRow = rows [j]
                    columns = tableRow.findAll ('td')
                    tableRows = []
                    for column in columns:
                        tableRows.append (column.text.strip ())
                    allRows.append (tableRows)

                temperatureData = []
                j = 0
                while allRows [j] != tableHead:
                    j += 1
                while allRows [j + 1] != tableHead:
                    temperatureData.append (allRows [j + 1][:2])
                    j += 1
                temperature = Temperature (temperatureData)
                temperature.convert_ToCentigrade ()

                allWeatherData [yearMonth] = temperature
        else:
            url = f'https://www.wunderground.com/forecast/OIMM'

            bi = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
            browser = webdriver.Firefox(firefox_binary=bi)
            browser.get(url)
            sleep(randint(10, 12))

            soup = BeautifulSoup (browser.page_source, 'lxml')
            browser.quit ()
            tables = soup.find_all('div', {'class' : 'forecast'})

            table = tables [0]
 
            As = table.findAll ('a')
            
            temperatures = []
            for a in As:
                spans = a.findAll ('span')
                temperatures.append (spans [0])

            allTemperature = []  
            for i in range ((endDate-startingDate).days + 1):
                singleDayTemperatures = []
                string = (temperatures [i].text).split ('|')
                for element in string:
                    for s in [re.findall (r'\b\d+\b', element)]:
                        try:
                            singleDayTemperatures.append (int (s [0]))
                        except:                                    
                            continue
                allTemperature.append (singleDayTemperatures)

            for t in range (len (allTemperature)):
                if len (allTemperature [t]) == 2:
                    averageTemp = sum (allTemperature [t])/2
                    allTemperature [t][1] = averageTemp
                else:
                    allTemperature [t].insert (0, (allTemperature [t][0]*allTemperature [t+1][0])/allTemperature [t+1][1])
                    averageTemp = sum (allTemperature [t])/2
                    allTemperature [t][1] = averageTemp

            temperature = Temperature (allTemperature)
            temperature.convert_ToCentigrade ()

            for i in range (len (allTemperature)):
                allWeatherData [i] = temperature.values [i]
        return allWeatherData