from pahbar.calendarData import CalendarData
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as BS
from unidecode import unidecode

def __getMiladiMonths__ (input):
    monthNames=['January','February','March','April','May','June','July','August','September','October','November','December']
    months=input.split('-')
    secondMonthTemp=months[1].strip().split(' ')
    year=secondMonthTemp[1]
    secondMonth=f'{year}/{monthNames.index(secondMonthTemp[0])+1}'
    if any(char.isdigit() for char in months[0]):
        firstmonthTemp=months[0].strip().split(' ')
        firstmonth=f'{firstmonthTemp[1]}/{monthNames.index(firstmonthTemp[0])+1}'
    else:
        firstmonth=f'{year}/{monthNames.index(months[0].strip())+1}'

    return (firstmonth,secondMonth)

def __getQamariMonths__ (input):
    monthNames=['محرم', 'صفر', 'ربيع الاول', 'ربيع الثاني', 'جمادي الاولي', 'جمادي الثانيه', 'رجب', 'شعبان', 'رمضان', 'شوال', 'ذوالقعده', 'ذوالحجه']
    months=input.split('-')
    for i in range (len (months)):
        months [i] = months [i].strip ()
    year=unidecode (months[-1])
    months = months [:-1]

    firstmonth=f'{year}/{monthNames.index(months[0])+1}'
    if months [1] == 'محرم':
        secondMonth = f'{int (year) + 1}/1'
    else:
        secondMonth=f'{year}/{monthNames.index(months[1])+1}'   

    return (firstmonth,secondMonth)

def __get_Day__ (driver, date_):
    select_day = Select(driver.find_element_by_id(
        'ctl00_cphMiddle_Sampa_Web_View_TimeUI_DateConvert00cphMiddle_3733_ddlDay'))
    select_day.select_by_value(str(date_.day))
    select_month = Select(driver.find_element_by_id(
        'ctl00_cphMiddle_Sampa_Web_View_TimeUI_DateConvert00cphMiddle_3733_ddlMonth'))
    select_month.select_by_value(str(date_.month))
    select_year = driver.find_element_by_id(
        'ctl00_cphMiddle_Sampa_Web_View_TimeUI_DateConvert00cphMiddle_3733_txtYear')
    select_year.clear()
    select_year.send_keys(str(date_.year))
    driver.find_element_by_id(
        'ctl00_cphMiddle_Sampa_Web_View_TimeUI_DateConvert00cphMiddle_3733_btnConvert').click()
    WebDriverWait(driver, 30).until(EC.text_to_be_present_in_element(
        (By.ID, 'ctl00_cphMiddle_Sampa_Web_View_TimeUI_DateConvert00cphMiddle_3733_lblFirstDateNumeral'),date_.isoformat() ))
    shamsi = driver.find_element_by_id(
        'ctl00_cphMiddle_Sampa_Web_View_TimeUI_DateConvert00cphMiddle_3733_lblSecondDateNumeral').text
    qamary = driver.find_element_by_id(
        'ctl00_cphMiddle_Sampa_Web_View_TimeUI_DateConvert00cphMiddle_3733_lblThirdDateNumeral').text
    shamsiList = shamsi.split (sep = '/')
    ghamariList = qamary.split (sep = '/')
    for i in range (len (shamsiList)):
        shamsiList [i] = int (unidecode (shamsiList [i]))
    for i in range (len (ghamariList)):
        ghamariList [i] = int (unidecode (ghamariList [i]))
    return shamsiList, ghamariList

def getYear(year):
    driver = webdriver.Firefox()
    driver.get("http://www.time.ir/fa/eventyear")
    year_selector = driver.find_element_by_id(
        'ctl00_cphTop_Sampa_Web_View_EventUI_EventYearCalendar10cphTop_3417_txtYear')
    year_selector.clear()
    year_selector.send_keys(str(year))
    driver.find_element_by_id(
        'ctl00_cphTop_Sampa_Web_View_EventUI_EventYearCalendar10cphTop_3417_btnGo').click()
    page = driver.page_source
    soup = BS(page, 'lxml')
    monthsHTML = soup.select(
        '#ctl00_cphTop_Sampa_Web_View_EventUI_EventYearCalendar10cphTop_3417_pnlYearCalendar .panel.panel-body')
    shamsiMonth = 0
    result = []
    for m in monthsHTML:
        daysList = []
        shamsiMonth += 1
        curr_months = m.select('.eventCalendar .header .dates > span')[0]
        miladi_months = __getMiladiMonths__(curr_months.select('.miladi')[0].string)
        qamari_months = __getQamariMonths__(curr_months.select('.qamari')[0].string)
    
        daysHTML = m.select('.eventCalendar .mainCalendar .dayList > div')
        
        miladiMonthChanged = False
        qamariMonthChanged = False
        qamariMonthChangedAgain=False
        for d in daysHTML:
            isDisabled = 'disabled' in d.attrs['class']
            if 'disabled' not in d.attrs['class']:
                # if d.select('.holiday'):
                #     print('*Holiday*')
                jalali = unidecode (d.select('.jalali')[0].string)
                jalaliDay = f'{year}/{shamsiMonth}/{jalali}'
                miladi = d.select('.miladi')[0].string
                if miladi == '01':
                    miladiMonthChanged = True
                if miladiMonthChanged:
                    miladiMonth = miladi_months[1]
                else:
                    miladiMonth = miladi_months[0]

                miladiDay = f'{miladiMonth}/{miladi}'
                qamari = unidecode (d.select('.qamari')[0].string)
                if qamari == '01' and not qamariMonthChanged and jalali != '1':
                    qamariMonthChanged = True
                elif qamari == '01' and  qamariMonthChanged:
                    qamariMonthChangedAgain=True

                if qamariMonthChanged and not qamariMonthChangedAgain:
                    qamariMonth = qamari_months[1]
                elif qamariMonthChangedAgain and qamariMonthChanged:
                    qamariMonth = qamari_months[2]
                else:
                    qamariMonth = qamari_months[0]
                qamariDay = f'{qamariMonth}/{qamari}'
                result.append ([miladiDay, jalaliDay, qamariDay])
    return result

def getDays(inputDates):
    options = webdriver.ChromeOptions ()
    options.headless = True
    driver = webdriver.Chrome (options = options)
    driver.get("http://www.time.ir")
    convert = Select(WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.ID, "ctl00_cphMiddle_Sampa_Web_View_TimeUI_DateConvert00cphMiddle_3733_ddlSelectConvertType"))
    ))
    convert.select_by_value("0")
    WebDriverWait(driver, 30).until(EC.text_to_be_present_in_element(
        (By.CSS_SELECTOR, '.dateConvertFirstDate > h5'), "میلادی:"))

    outputList = []
    for date_ in inputDates:
        shamsiAndGhamari = __get_Day__ (driver, date_)
        currentDay = CalendarData (date_, shamsiDateList = shamsiAndGhamari [0], ghamariDateList = shamsiAndGhamari [1])
        outputList.append(currentDay)
    driver.quit ()
    return outputList