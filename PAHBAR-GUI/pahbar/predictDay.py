from datetime import timedelta

class PredictDay:
    def __init__ (self, fromDate, date):
        self.fromDate = fromDate - timedelta (days=1)
        self.date = date

    def determine_PredictDates(self):
        self.predictDates = []
        numberOfPredictions = self.date - self.fromDate
        newDate = self.fromDate + timedelta (days = 1)
        for _ in range (numberOfPredictions.days):
            self.predictDates.append (newDate)
            newDate += timedelta (days=1)