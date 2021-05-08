from datetime import timedelta
from dayLength import daylength
import pandas as pd

dataSet = pd.read_excel ('DataSet_ExcludingDG_Hourly.xlsx', index_col=0, engine='openpyxl')
dayLengths = []
daylengthsYesterday = []
dayLengthsLastWeek = []
for d in range (len (dataSet.Date)):
    dayLengths.append (daylength (dataSet.Date[d].date ().timetuple().tm_yday, 36.2605))
    daylengthsYesterday.append (daylength ((dataSet.Date[d].date () - timedelta (days= 2)).timetuple().tm_yday, 36.2605))
    dayLengthsLastWeek.append (daylength ((dataSet.Date[d].date () - timedelta (days= 7)).timetuple().tm_yday, 36.2605))

lengths = pd.DataFrame (columns=['0','2','7'])
lengths ['0'] = dayLengths
lengths ['2'] = daylengthsYesterday
lengths ['7'] = dayLengthsLastWeek
lengths.to_excel ('Lengths.xlsx')
    