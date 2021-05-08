import threading
import time
import pickle
from tkinter.messagebox import NO
from pahbar.repository import Repository
from pahbar.trainer import Trainer
from pahbar.predictDay import PredictDay
from pahbar.output import Output
from pahbar.predictor import Predictor
import subprocess
import os.path
from persiantools.jdatetime import JalaliDate
from datetime import timedelta
from pahbar.historicalLoad import HistoricalLoad
import pandas as pd
from pahbar.analysis import Analysis
import logging


def get_uuid():
    return subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()

class Prediction():
    def __init__(self, data_folder_path):
        self.data_folder_path = data_folder_path
        self.R = Repository (self.data_folder_path)
        self.R.dataSet.determine_TrainEndDate ()
        self.pathToLoadData = None
        self.predictionAnalysis = None
        logging.basicConfig (filename='PAHBAR.log', level=logging.DEBUG)
        dateTime = JalaliDate.today ()
        logging.info (f'Date: {dateTime}')

    def import_data(self, file_path)->bool:
        '''
        imports data from excel file in the given path 

        Args:
            file_path (pathlib.Path): The file location of the spreadsheet

        Returns:
            bool: if import is successul returns True otherwise returns False
        '''
        try:
            self.pathToLoadData = file_path
            if os.path.isfile (self.pathToLoadData):
                logging.info (f'One file has been imported -- ({self.pathToLoadData})')
                return True
        except Exception as inst:
            logging.warning (inst)
            return False
    def export_data(self, file_path)->bool:
        '''
        exports data to excel file in the given path 

        Args:
            file_path (pathlib.Path): The file location of the spreadsheet

        Returns:
            bool: if export is successul returns True otherwise returns False
        '''
        try:
            self.R.export_AsXLSX(file_path)
            logging.info (f'DataSet {self.R.selectedDataSet} has been exported -- {file_path}')
            return True
        except Exception as inst:
            logging.error (inst)
            return False
    
    def get_data(self, from_date, to_date)->dict:
        '''
        gives the raw data in time period between from_data to to_date including both of them

        Args:
            from_date (datetime.date): the begining of the time period
            to_date (datetime.date): the end of the time period

        Returns:
            dict: returns a dictionary having two keys 'header' and 'data'
                'header' : a list of the headers of the data in str type
                'data': list of list of data all in str type
        '''
        logging.info (f'Attempted to see the data from dataset {self.R.selectedDataSet} ({from_date} - {to_date}) ...')
        self.R.dataSet.convert_DatatoDict (from_date, to_date)
        if not (self.R.dataSet.dataDictionary ['data']):
            logging.warning (f'The range is not available in the dataset {self.R.selectedDataSet}')
        else:
            logging.info ('Data displayed successfully!')
        return self.R.dataSet.dataDictionary

    def fetch_online_data(self)->bool:
        '''
        fteches online weather and calendar data

        when the training process is done (successfuly or unsuccessfuly)an arbitrary string should be added to the queue in order to notify
        the calling thread that the task is done.
        Args:
            queue (queue.Queue): a synchronous queue used to notify the caller that the task is finished

        Returns:
            bool: if task is done successuly returns True otherwise returns False
        '''
        try:
            logging.info (f'Attempted to update dataSet {self.R.selectedDataSet}... Last day of dataSet is {self.R.dataSet.trainEndDate}')
            if not (self.pathToLoadData) or not (os.path.isfile (self.pathToLoadData)):
                logging.info ("No load data!")
                result = dict ({'English' : "No load data! \"Import Load Data\" first!", 'Farsi' : 'اطلاعات بار موجود نیست! ابتدا اطلاعات بار را بارگذاری نمایید.'})
                return result

            if not (self.R.complete_DataSet (self.pathToLoadData)): 
                if self.R.weatherDataUnavailable:
                    logging.warning ('Weather data unavailable!')
                    result = dict ({'English':'No internet connection!', 'Farsi': 'لطفاً اتصال به اینترنت را بررسی کنید!'})
                    return result

                if self.R.calendarDataUnavailable:
                    logging.warning ('Calendar data unavailable!')
                    result = dict ({'English':'No internet connection!', 'Farsi': 'لطفاً اتصال به اینترنت را بررسی کنید!'})
                    return result

                if self.R.historicalLoadUnavailable:
                    logging.warning ('Please make sure your load data is complete and try again!')
                    result = dict ({'English':'Please make sure your load data is complete and try again! There may be blank cells in your load data! Please fill in the blank cells or delete the row with Nan values!', 'Farsi': 'لطفاً از کامل بودن اطلاعات بار اطمینان حاصل کنید و مجدداً تلاش نمایید! اگر در داده‌ها خانه‌های خالی وجود دارد، سطر مربوطه را حذف نمایید'})
                    return result
                         
        except Exception as inst: 
            print (inst)           
            logging.error (inst)
            return False 
        self.train ()

        logging.info (f'DataSet {self.R.selectedDataSet} has been updated successfully!')
        return True                  

    def determine_PredictDates (self, from_date, to_date):
        logging.info (f'Attempted to predict load ({from_date} - {to_date})')
        logging.info ('Trying to get predict dates ...')

        self.invalidDate = None
        if from_date > self.R.dataSet.trainEndDate:
            self.predictDay = PredictDay (self.R.dataSet.trainEndDate + timedelta (days = 1), to_date)      
        else:
            self.predictDay = PredictDay (from_date, to_date)

        self.predictDay.determine_PredictDates ()

        if not (self.predictDay.predictDates):
            logging.warning ('Invalid Date!')
            self.invalidDate = 1
            return self.invalidDate

    def get_prediction(self, from_date, to_date)->dict:
        '''
        predicts for the requested period(including begining and end) and returns the results 

        Args:
            from_date (datetime.date): the begining of the time period
            to_date (datetime.date): the end of the time period

        Returns:
            dict: returns a dictionary having two keys 'header' and 'data'
                'header' : a list of the headers of the data in str type
                'data': list of list of data all in str type
        '''   
        try:
            self.R.get_ProcessedData ()  
            self.R.get_TrainedAlgorithms ()
            logging.info ('Trained Algorithms data has fetched successfully ... ')
            predictor = Predictor (self.R.processed_X_train, self.R.regressors)
        except Exception as inst:
            print (inst)
            msg = 'No train history available! Please train the model!'
            logging.warning (msg)
            result = dict ({'English':msg, 'Farsi':'تاریخچه‌ای از آموزش مدل در دسترس نیست ... لطفا مدل را آموزش دهید'})
            return result   

        self.output = Output (self.predictDay.predictDates, self.R.dataSet.headers)
        logging.info ('Trying to complete features of the predict days ...')
        success = self.output.complete_Features ()
        if not (success):
            if self.output.weatherDataUnavailable:
                logging.warning ('Weather Data Unavailable!')
                result = dict ({'English':'No internet connection!', 'Farsi':'اتصال اینترنت برقرار نیست'})
                return result
            if self.output.calendarDataUnavailable:
                logging.warning ('Calendar Data Unavailable!')
                result = dict ({'English':'No internet connection!', 'Farsi':'اتصال اینترنت برقرار نیست'})
                return result
                    
        try:
            logging.info ('Trying to predict load ...')
            predictor.predict (self.output, self.R)
        except Exception as inst:
            print (inst)
            logging.warning (inst)
            return None

        self.output.convert_DatatoDict (from_date, to_date)
        logging.info ('Load predicted successfully!')
        return self.output.dataDictionary

    def export_prediction(self, from_date, to_date, file_path)->bool:
        '''
        predicts for the requested period(including begining and end) and saves the result in an xlsx file in the given file_path

        Args:
            from_date (datetime.date): the begining of the time period
            to_date (datetime.date): the end of the time period
            file_path (pathlib.Path): The file location of the spreadsheet

        Returns:
            bool: if task is done successuly returns True otherwise returns False
        '''
        logging.info ('Attempted to export predicted load ...')
        try:
            self.R.export_PredictionAsXLSX (from_date, to_date, file_path)
            if not (self.R.predictedDataHistory):
                logging.warning ('Predicted load information is not available!')
                return False
            else:
                logging.info ('Information exported successfully!')
                return True
        except Exception as inst:
            print (inst)
            logging.error (inst)
            return False

    def train(self, queue = None)->bool:
        '''
        trians the model synchronously in another thread

        when the training process is done (successfuly or unsuccessfuly)an arbitrary string should be added to the queue in order to notify
        the calling thread that the task is done.
        Args:
            queue (queue.Queue): a synchronous queue used to notify the caller that the task is finished

        Returns:
            bool: if task is done successuly returns True otherwise returns False

        '''
        logging.info ('Attempted to train the model ...')
        try:
            logging.info ('Preparing data ...')
            self.R.prepare_Data ()
            trainer = Trainer (self.R)
            # trainer.train ()
            if queue:
                t = ThreadedTask(trainer.train, queue)
                t.start()
            else:
                trainer.train ()
            logging.info ('Model trained successfully!')
        except Exception as inst:
            print (inst)
            logging.error (inst)    

    def select_DataSet (self, mode):
        self.R.select_DataSet (mode)

    def edit_DataSet (self):
        logging.info (f'Attempted to edit dataSet{self.R.selectedDataSet} ... ')
        if not (self.pathToLoadData) or not (os.path.isfile (self.pathToLoadData)):
            logging.warning ('There is no load data imported!')
            return "No load Data! \"Import CORRECT Load Data\" first!"
        newLoadData = HistoricalLoad (self.R, path=self.pathToLoadData)
        try:
            result = self.R.edit_DataSet (newLoadData.data)
            if isinstance (result, dict):
                logging.warning (result ['English'])
                return result
            else:
                logging.info (f'DataSet{self.R.selectedDataSet} edited successfully!')
                return True             
        except Exception as inst:
            logging.error (inst)
            print (inst)
            return False

    def show_Documentation (self):
        logging.info ('Attempted to see the documentation ...')
        path = os.path.join (self.data_folder_path,'Documentation.pdf')
        os.startfile (path)

    def delete_Row (self, from_date, to_date):
        logging.info (f'Attempted to delete {from_date} - {to_date} data from dataSet{self.R.selectedDataSet} ...')
        if (to_date < self.R.dataSet.data.iloc [0]['Date']) or (from_date > self.R.dataSet.data.loc [self.R.dataSet.numberOfRecords - 1]['Date']):
            logging.warning ('Invalid Date!')
            result = dict ({'English':'The range you selected is not available in the dataset!', 'Farsi':'بازه انتخاب شده در دیتاست موجود نیست'})
            return result
        try:
            logging.info ('Trying to predict ... ')
            logging.info ('Trying to get predict dates ...')
            self.determine_PredictDates (from_date, to_date)
            predictedLoad = self.get_prediction (from_date, to_date)
            if isinstance (predictedLoad, dict):
                if 'English' in predictedLoad:
                    logging.warning (predictedLoad ['English'])
                    return predictedLoad
                else:
                    logging.info ('Load predicted successfully!')
                    newLoadData = pd.DataFrame (data = predictedLoad ['data'], columns = predictedLoad ['header'])
            
            logging.info (f'Trying to replace load into dataset{self.R.selectedDataSet} ...')
            self.R.edit_DataSet (newLoadData)
            logging.info ('Load replaced successfully!')
            return True
        except Exception as inst:
            logging.error (inst)
            print (inst)
            return False

    def determine_TrainEndDate (self):
        logging.info ('Trying to determine train end date ...')
        self.R.dataSet.determine_TrainEndDate ()
        trainEndDate = JalaliDate (self.R.dataSet.trainEndDate)
        logging.info ('Train end date determined successfully!')
        return trainEndDate

    def analyze_Prediction (self, from_date, to_date):
        logging.info (f'Attempted to analyze prediction ({from_date} - {to_date})')
        logging.info ('Trying to get output history ...')
        self.R.get_PredictedValues (from_date, to_date)

        if not (self.R.predictedDataHistory):
            msg = 'Invalid Date! The load you selected has not been predicted yet!'
            logging.warning (msg)
            result = dict ({'English':msg, 'Farsi':'بازه نامعتبر! بار بازه انتخاب شده، هنوز پیش‌بینی نشده است'})
            return result

        dates = []
        for i in range (len (self.R.predictedDataHistory)):
            dates.append (self.R.predictedDataHistory [i][1])

        logging.info (f'Trying to get the actual values from dataSet{self.R.selectedDataSet}')
        self.R.dataSet.find_ActualValues (dates)

        if not (self.R.dataSet.actualValues):
            msg = 'No actual data! Please update the dataset!'
            logging.warning (msg)
            result = dict ({'English':msg, 'Farsi':'مقادیر واقعی بازه مورد نظر در دسترس نیست! لطفاً دیتاست را کامل نمایید'})
            return result

        self.predictionAnalysis = Analysis (self.R.dataSet.actualValues, self.R.predictedDataHistory)
        logging.info ('Analyzing predictions started ...')
        self.predictionAnalysis.analyze ()
        if self.predictionAnalysis.resultsDictionary:
            logging.info ('Analysis completed successfully!')
        else:
            logging.error ('Analysis unsuccessful! There is a problem in Analyze Function!')
        return self.predictionAnalysis.resultsDictionary

    def export_AnalysisResults (self, file_path):
        logging.info ('Attempted to export analysis results ... ')
        try:
            self.predictionAnalysis.export_AsXLSX (file_path)
            logging.info (f'Analysis results exported successfully! ({file_path})')
            return True
        except Exception as inst:
            logging.warning (inst)
            logging.warning ('Analysis results are not available!')
            print (inst)
            return False

    def plot_AnalysisResults (self, from_date, to_date):
        logging.info (f'Attempted to plot analysis results ... ({from_date} - {to_date})')
        if from_date != to_date:
            msg = "Sorry! Only one prediction result can be shown!"
            logging.warning (msg)
            result = dict ({'English':msg, 'Farsi':'متاسفانه امکان نمایش نمودارهای بیش از یک روز وجود ندارد ... لطفاً فقط یک تاریخ را انتخاب نمایید'})
            return result
        logging.info ('Plotting ... ')
        if not (self.predictionAnalysis):
            msg = 'You should try "Analyze Prediction" first!'
            logging.warning (msg)
            result = dict ({'English':msg, 'Farsi':'لازم است ابتدا آنالیز پیش‌بینی انجام شود'})
            return result
        fig = self.predictionAnalysis.plot_AnalysisResults (from_date, to_date)
        if isinstance (fig, dict):
            logging.warning (fig ['English'])
            return fig
        else:
            logging.info ('Prediction analysis ploted successfully!')
            return fig

    def save_AnalysisPlot (self, file_path):
        logging.info ('Attempted to save analysis plot ...')
        try:
            result = self.predictionAnalysis.save_Plot (file_path)
            if result:
                logging.info (f'Plot saved in {file_path}')
                return True
            else:
                logging.warning ('Try "Plot Results" first!')
                return False
        except:
            logging.warning ('There is no plot to save!')
            return False

    def calculate_ErrorAttributes (self):
        logging.info ('Trying to calculate error attributes ...')
        attributesList = self.predictionAnalysis.calculate_ErrorAttributes ()
        logging.info ('Calculation complete!')
        return attributesList
    
    def export_PredictionHistory (self, file_path):
        logging.info ('Attempted to export prediction history ...')
        try:
            self.R.export_AllPredictionHistory (file_path)
            logging.info ('Prediction history exported successfully!')
            return True
        except Exception as inst:
            print (inst)
            logging.error (inst)
            return False

    def get_LastTrainDate (self):
        logging.info ('Trying to get the last train date ...')
        try:
            self.R.get_LastTrainDate ()
            logging.info (f'last train date fetched successfully! ({self.R.lastTrainDate})')
            return self.R.lastTrainDate
        except Exception as inst:
            print (inst)
            logging.error (inst)

    def remove_FilePath (self):
        logging.info ('Trying to remove the previous file path ...')
        try:
            self.pathToLoadData = None
        except Exception as inst:
            logging.error (inst)

    def get_Mode (self):
        return self.R.selectedDataSet

    def remove_AnalysisHistory (self):
        self.predictionAnalysis = None

class ThreadedTask(threading.Thread):
    def __init__(self, thread_function, queue):
        threading.Thread.__init__(self)
        self.thread_function = thread_function
        self.daemon = True
        self.queue = queue
    def run(self):
        try:
            self.thread_function()
            self.queue.put("Task finished")
        except:
            self.queue.put("Task finished")
