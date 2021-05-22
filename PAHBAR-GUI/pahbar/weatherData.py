from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import date
import calendar
import collections

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

        self.__make_ListOfMonthNames__ ()
        self.__get_MonthYearList__ ()

    def __get_DailyTemp__ (self, dayData):
        try:
            maxTemp = float (dayData.find ('div', {'class' : 'high'}).string.strip () [:-1])
            minTemp = float (dayData.find ('div', {'class' : 'low'}).string.strip () [:-1])
            avgTemp = (maxTemp+minTemp)/2
            return maxTemp, avgTemp
        except:
            return False

    def __get_MonthYearList__ (self):
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

    def __make_ListOfMonthNames__ (self):
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
                    dailyTemp = self.__get_DailyTemp__ (d)
                    if not dailyTemp:
                        missingDataDate = date (m ['year'], list (calendar.month_name).index (m ['month']), date_)
                        missingDataDates[f'{missingDataDate.year}-{missingDataDate.month}'].append (date_)
                        datesAndTemperature [f'{date_}'].append ('N/A')
                    else:
                        datesAndTemperature [f'{date_}'].append ([dailyTemp [0], dailyTemp [1]])                    

            self.allWeatherData [f"{m['month']}-{m['year']}"] = datesAndTemperature