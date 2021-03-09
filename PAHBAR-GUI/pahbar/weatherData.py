from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from random import randint
from pahbar.temperatureData import Temperature
from datetime import date
import re

class WeatherData:
    def __init__ (self, endDate, startingDate):
        self.startingDate = startingDate
        self.endDate = endDate
        if self.startingDate:
            self.numberOfMonths = (self.endDate.year - self.startingDate.year) * 12 + (self.endDate.month - self.startingDate.month)
            self.yearList = range (self.startingDate.year, self.endDate.year + 1)
        else:
            self.numberOfMonths = 0
            self.yearList = [self.endDate.year]

        self.__make_ListOfMonthNumbers ()
        self.__make_ListOfyearMonths ()

    def __make_ListOfyearMonths (self):
        self.yearMonthList = []
        j = 0
        for i in range (len (self.monthNumbers)):
            if i == 0:
                self.yearMonthList.append (f'{self.yearList [j]}-{self.monthNumbers[i]}')
            else:
                if (self.monthNumbers [i - 1] != 12):
                    self.yearMonthList.append (f'{self.yearList [j]}-{self.monthNumbers[i]}')
                else:
                    j += 1
                    self.yearMonthList.append (f'{self.yearList [j]}-{self.monthNumbers[i]}')                    

    def __make_ListOfMonthNumbers (self):
        self.monthNumbers = []
        if self.startingDate:
            startMonth = self.startingDate.month
        else:
            startMonth = self.endDate.month
        j = 0
        for i in range (self.numberOfMonths + 1):
            if startMonth + i <= 12:
                self.monthNumbers.append (startMonth + i)
            else:
                j += 1
                if j <= 12:
                    self.monthNumbers.append (j)
                else:
                    j = 0

    def get_WeatherData (self):
        
        self.allWeatherData = {}

        if self.endDate < date.today ():
            for yearMonth in self.yearMonthList:                
                url = f'https://www.wunderground.com/history/monthly/ir/mashhad/OIMM/date/{yearMonth}'

                bi = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
                browser = webdriver.Firefox(firefox_binary=bi)
                browser.get(url)
                sleep(randint(10, 12))
                # sleep (randint (40, 50))

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

                self.allWeatherData [yearMonth] = temperature
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
            for i in range ((self.endDate-self.startingDate).days + 1):
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
                self.allWeatherData [i] = temperature.values [i]