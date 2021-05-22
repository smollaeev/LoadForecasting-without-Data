from copy import copy
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from persiantools.jdatetime import JalaliDate
import copy

class Analysis:

    def __init__ (self, actualData, predictedData):
        self.actualData = actualData
        self.predictedData = predictedData
        self.error = []
        self.absoluteError = []
        self.headers = ['Type', 'Date']
        for i in range (24):
            self.headers.append (f'H{i + 1}')

    def __calculate_Error__ (self):
        for i in range (len (self.actualData)):
            error = []
            absoluteError = []
            error.append ('Error (%)')
            error.append (self.actualData [i][1])
            absoluteError = copy.deepcopy (error)
            for j in range (24):
                error.append ((self.actualData [i][j + 2] - self.predictedData [i][j + 2]) * 100 / self.actualData [i][j + 2])
                absoluteError.append (abs(self.actualData [i][j + 2] - self.predictedData [i][j + 2]) * 100 / self.actualData [i][j + 2])
            self.error.append (error)
            self.absoluteError.append (absoluteError)

    def __make_AnalysisResults__ (self):
        data = []
        for i in range (len (self.actualData)):
            data.append (self.actualData [i])
            data.append (self.predictedData [i])
            data.append (self.error [i])

        for i in range (len (data)):
            for j in range (len (data [i])):
                if isinstance (data [i][j], float):
                    data [i][j] = round (data [i][j], 3)

        self.resultsDictionary = dict ({'header':self.headers, 'data': data})
        self.exportableOutput = pd.DataFrame (data = self.resultsDictionary['data'], columns= self.resultsDictionary ['header'])

    def __extract_DataForPlot__ (self, from_date):
        self.dataForPlot = []
        shamsiFromDate = JalaliDate (from_date)

        for i in range (len (self.actualData)):
            if (self.actualData [i][1] == shamsiFromDate):
                self.dataForPlot.append (self.actualData [i][2:])
                self.dataForPlot.append (self.predictedData [i][2:])
                self.dataForPlot.append (self.error [i][2:])
                self.dataForPlot.append (self.absoluteError [i][2:])

    def analyze (self):
        self.__calculate_Error__ ()
        self.__make_AnalysisResults__ ()

    def plot_AnalysisResults (self, from_date):
        self.__extract_DataForPlot__ (from_date)
        if not (self.dataForPlot):
            result = dict ({'English':'There is no result available!', 'Farsi':'نتایج آنالیز در دسترس نیست'})
            return result
        self.fig = Figure (figsize=(4,3.2))
        plotsList = []

        for i in range (2):
            plotsList.append (self.fig.add_subplot (2, 1, i + 1))

        plotColors = ['blue','orange','red']
        hours = range (1, 25)
        plotsList [0].plot (hours, self.dataForPlot [0],marker='.', color = plotColors [0], label = "Actual")
        plotsList [0].plot (hours, self.dataForPlot [1],marker='.', color = plotColors [1], label = 'Predicted')
        plotsList [1].plot (hours, self.dataForPlot [2],marker='.', color = plotColors [2], label = 'Error (%)')

        plotsList [0].set_title (f'Prediction Analysis - {JalaliDate (from_date)}', fontsize = 8)
        plotsList [0].set_ylabel ("Load", fontsize = 8)
        
        plotsList [0].set_xticks (hours, minor = True)

        plotsList [1].set_ylabel ("Error (%)", fontsize = 8)
        plotsList [1].set_xlabel ("Hour", fontsize = 8)            
        plotsList [1].set_xticks (hours, minor = True)

        plotsList [0].grid (which = 'minor', alpha = 0.25)
        plotsList [0].grid (which = 'major', alpha = 0.7)
        plotsList [1].grid (which = 'minor', alpha = 0.25)
        plotsList [1].grid (which = 'major', alpha = 0.7)

        plotsList [0].legend ()
        plotsList [1].legend ()

        return self.fig
        
    def calculate_ErrorAttributes (self):
        mean = sum (self.dataForPlot [3])/24
        maximum = max (self.dataForPlot [3])
        hour = self.dataForPlot [3].index (maximum) + 1
        return [round (mean, 2), round (maximum, 2), hour]