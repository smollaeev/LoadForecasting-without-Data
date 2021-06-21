from datetime import timedelta
from persiantools.jdatetime import JalaliDate

class Dates:
    @staticmethod
    def make_ListOfDates (fromDate, toDate, jalali = False):
        dates = []
        currentDate = fromDate
        while currentDate != toDate + timedelta (days=1):
            if jalali:
                dates.append (JalaliDate (currentDate))
            else:
                dates.append (currentDate)
            currentDate += timedelta (days=1)
        return dates

    @staticmethod
    def get_DateList(dateString):
        if '/' in dateString:
            return str (dateString).split ('/')
        else:
            return str (dateString).split ('-')