import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from persiantools.jdatetime import JalaliDate

class Analysis:

    def __init__ (self, actualData, predictedData):
        self.actualData = actualData
        self.predictedData = predictedData
        self.headers = self.__get_Headers__ ()
        self.error = []
        self.absoluteError = []
        
    def __get_Headers__ (self):
        headers = ['Type', 'Date']
        for i in range (24):
            headers.append (f'H{i + 1}')
        return headers

    def __calculate_Error__ (self, actualData, predictedData):
        error = []
        absoluteError = []
        for j in range (24):
            error.append ((actualData [j + 2] - predictedData [j + 2]) * 100 / actualData [j + 2])
            absoluteError.append (abs(actualData [j + 2] - predictedData [j + 2]) * 100 / actualData [j + 2])
        return error, absoluteError

    @staticmethod
    def __prepare_ErrorList__ (actualData, error, absoluteError):
        error.insert (0, 'Error (%)')
        absoluteError.insert (0, 'Error (%)')
        error.insert (1, actualData [1])
        absoluteError.insert (1, actualData [1])
        return error, absoluteError

    def __get_ErrorForEachRecord__ (self, row):
        error, absoluteError = self.__calculate_Error__ (self.actualData [row], self.predictedData [row])
        error, absoluteError = Analysis.__prepare_ErrorList__ (self.actualData [row], error, absoluteError)
        self.error.append (error)
        self.absoluteError.append (absoluteError)

    def __get_Error__ (self):
        for i in range (len (self.actualData)):
            self.__get_ErrorForEachRecord__ (i)  

    def __get_AllData__ (self):
        data = []
        for i in range (len (self.actualData)):
            data.append (self.actualData [i])
            data.append (self.predictedData [i])
            data.append (self.error [i])
        return data

    def __prepare_Output__ (self, data):
        self.resultsDictionary = dict ({'header':self.headers, 'data': data})
        self.exportableOutput = pd.DataFrame (data = self.resultsDictionary['data'], columns= self.resultsDictionary ['header'])

    def __make_AnalysisResults__ (self):
        data = self.__get_AllData__ ()
        data = Analysis.__round_Numbers__ (data, 3)
        self.__prepare_Output__ (data)

    def __extract_DataForPlot__ (self, shamsiDate):
        self.dataForPlot = []
        for i in range (len (self.actualData)):
            if (self.actualData [i][1] == shamsiDate):
                self.dataForPlot.append (self.actualData [i][2:])
                self.dataForPlot.append (self.predictedData [i][2:])
                self.dataForPlot.append (self.error [i][2:])
                self.dataForPlot.append (self.absoluteError [i][2:])       

    @staticmethod
    def __round_Numbers__ (data, afterDecimal):
        for i in range (len (data)):
            for j in range (len (data [i])):
                if isinstance (data [i][j], float):
                    data [i][j] = round (data [i][j], afterDecimal)
        return data

    def __create_PlotsList (self):
        self.plotsList = []
        for i in range (2):
            self.plotsList.append (self.fig.add_subplot (2, 1, i + 1))
        return self.plotsList

    def __plot__ (self, hours, plotColors):
        self.plotsList [0].plot (hours, self.dataForPlot [0],marker='.', color = plotColors [0], label = "Actual")
        self.plotsList [0].plot (hours, self.dataForPlot [1],marker='.', color = plotColors [1], label = 'Predicted')
        self.plotsList [1].plot (hours, self.dataForPlot [2],marker='.', color = plotColors [2], label = 'Error (%)')

    def __add_PlotsAttributes__ (self, hours, shamsiDate):
        self.plotsList [0].set_title (f'Prediction Analysis - {shamsiDate}', fontsize = 8)
        self.plotsList [0].set_ylabel ("Load", fontsize = 8)        
        self.plotsList [0].set_xticks (hours, minor = True)
        self.plotsList [1].set_ylabel ("Error (%)", fontsize = 8)
        self.plotsList [1].set_xlabel ("Hour", fontsize = 8)            
        self.plotsList [1].set_xticks (hours, minor = True)
        self.plotsList [0].grid (which = 'minor', alpha = 0.25)
        self.plotsList [0].grid (which = 'major', alpha = 0.7)
        self.plotsList [1].grid (which = 'minor', alpha = 0.25)
        self.plotsList [1].grid (which = 'major', alpha = 0.7)
        self.plotsList [0].legend ()
        self.plotsList [1].legend ()

    def __create_Fig__ (self, shamsiDate):
        hours = range (1, 25)
        plotColors = ['blue','orange','red']
        self.fig = Figure (figsize=(4,3.2))
        self.__create_PlotsList ()    
        self.__plot__ (hours, plotColors)
        self.__add_PlotsAttributes__ (hours, shamsiDate)

    def analyze (self):
        self.__get_Error__ ()
        self.__make_AnalysisResults__ ()

    def plot_AnalysisResults(self, from_date):
        shamsiFromDate = JalaliDate (from_date)
        self.__extract_DataForPlot__ (shamsiFromDate)
        if not (self.dataForPlot):
            return dict(
                {
                    'English': 'There is no result available!',
                    'Farsi': 'نتایج آنالیز در دسترس نیست',
                }
            )

        self.__create_Fig__ (shamsiFromDate)
        return self.fig
        
    def calculate_ErrorAttributes (self):
        mean = sum (self.dataForPlot [3])/24
        maximum = max (self.dataForPlot [3])
        hour = self.dataForPlot [3].index (maximum) + 1
        return [round (mean, 2), round (maximum, 2), hour]