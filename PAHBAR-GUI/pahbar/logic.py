from pahbar.dataFile import DataFile
from pahbar.independentVariables import IndependentVariables
from pahbar.featuresData import STFeaturesData, MTFeaturesData
import threading
from pahbar.repository import Repository
from pahbar.trainer import Trainer
from pahbar.predictDay import PredictDay
from pahbar.output import STOutput, MTOutput
from pahbar.predictor import STPredictor, MTPredictor
import os.path
from persiantools.jdatetime import JalaliDate
from datetime import timedelta
from pahbar.historicalLoad import HistoricalLoad
import pandas as pd
from pahbar.analysis import Analysis
import logging
from datetime import date

class Logic ():
    def __init__(self, data_folder_path):
        self.data_folder_path = data_folder_path
        self.R = Repository (self.data_folder_path)
        self.R.dataSet.determine_EndDate ()
        self.pathToLoadData = None
        self.predictionAnalysis = None
        Logic.__create_LogFile__ ()
        
    def __create_LogFile__ ():
        logging.basicConfig (filename='PAHBAR.log', level=logging.DEBUG)
        dateTime = JalaliDate.today ()
        logging.info (f'Date: {dateTime}')

    def import_Data (self, file_path)->bool:
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

    def export_Data(self, file_path) -> bool:
        '''
        exports data to excel file in the given path 

        Args:
            file_path (pathlib.Path): The file location of the spreadsheet

        Returns:
            bool: if export is successul returns True otherwise returns False
        '''
        try:
            return self.__convet_DataToXlsx__(file_path)
        except Exception as inst:
            print(inst)
            logging.error(inst)
            return False

    def __convet_DataToXlsx__(self, file_path):
        featuresData = self.R.unpickle_Data ('FeaturesData')
        loadData = self.R.unpickle_Data ('LoadData').iloc [:, :-1]
        dataSet = featuresData.join (loadData)
        Repository.export_AsXLSX (dataSet, file_path)
        logging.info (f'DataSet {self.R.selectedDataSet} has been exported -- {file_path}')
        return True
    
    def get_Data (self, from_date, to_date)->dict:
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
        dataDictionary = self.R.dataSet.get_DataDictionaryToDisplay (from_date, to_date)
        if not (dataDictionary ['data']):
            logging.warning (f'The range is not available in the dataset {self.R.selectedDataSet}')
        else:
            logging.info ('Data displayed successfully!')
        return dataDictionary

    def fetch_OnlineData(self) -> bool:
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
            logging.info (f'Attempted to update dataSet {self.R.selectedDataSet}... Last day of dataSet is {self.R.dataSet.endDate}')
            if not (self.pathToLoadData) or not (os.path.isfile (self.pathToLoadData)):
                logging.info ("No load data!")
                return dict(
                    {
                        'English': "No load data! \"Import Load Data\" first!",
                        'Farsi': 'اطلاعات بار موجود نیست! ابتدا اطلاعات بار را بارگذاری نمایید.',
                    }
                )


            if DataFile.check_ForNull (self.pathToLoadData):
                return self.__report__(
                    'Please make sure your load data is complete and try again!',
                    'Please make sure your load data is complete and try again! There may be blank cells in your load data! Please fill in the blank cells or delete the row with Nan values!',
                    'لطفاً از کامل بودن اطلاعات بار اطمینان حاصل کنید و مجدداً تلاش نمایید! اگر در داده‌ها خانه‌های خالی وجود دارد، سطر مربوطه را حذف نمایید',
                )

            if DataFile.check_ForZero (self.pathToLoadData):
                return self.__report__(
                    'Please make sure your load data values are non-zero and try again!',
                    'Please make sure your load data is correct and try again! There may be values of zero in your load data!',
                    'لطفاً از صحیح بودن اطلاعات بار اطمینان حاصل کنید و مجدداً تلاش نمایید! اگر در داده‌ها مقادیر صفر وجود دارد، مقادیر درست را وارد نمایید',
                )

            loadData = pd.read_excel (self.pathToLoadData, engine='openpyxl')

            historicalLoad = HistoricalLoad (self.R.dataSet, loadData = loadData)
            if historicalLoad.endDate == date.today () - timedelta (days=1):
                stopDate = historicalLoad.endDate - timedelta (days=1)
                yesterdayLoadData = loadData.iloc [-1, :].values
                self.R.pickle_Data (yesterdayLoadData, 'YesterdayLoad')
            else:
                stopDate = historicalLoad.endDate
            yesterdayLoadData = self.R.unpickle_Data ('YesterdayLoad')
            if not (self.R.dataSet.update (yesterdayLoadData, historicalLoad, stopDate)):
                if self.R.dataSet.featuresData.weatherDataUnavailable:
                    return self.__report__(
                        'Weather data unavailable!',
                        'No internet connection!',
                        'لطفاً اتصال به اینترنت را بررسی کنید!',
                    )

                if self.R.dataSet.featuresData.calendarDataUnavailable:
                    return self.__report__(
                        'Calendar data unavailable!',
                        'No internet connection!',
                        'لطفاً اتصال به اینترنت را بررسی کنید!',
                    )

        except Exception as inst:
            print(inst)
            logging.error(inst)
            return False
        self.R.pickle_Data (self.R.dataSet.featuresData.data, 'FeaturesData')
        self.R.pickle_Data (self.R.dataSet.loadData.data, 'LoadData')
        self.trainSTLF ()

        logging.info (f'DataSet {self.R.selectedDataSet} has been updated successfully!')
        return True                  

    def __report__(self, arg0, arg1, arg2):
        logging.warning(arg0)
        return dict({'English': arg1, 'Farsi': arg2})                  

    def determine_PredictDates (self, from_date, to_date):
        logging.info (f'Attempted to predict load ({from_date} - {to_date})')
        logging.info ('Trying to get predict dates ...')

        self.invalidDate = None
        if from_date > self.R.dataSet.endDate:
            self.predictDay = PredictDay (self.R.dataSet.endDate + timedelta (days = 1), to_date)      
        else:
            self.predictDay = PredictDay (from_date, to_date)

        self.predictDay.determine_PredictDates ()
        if date.today () - timedelta (days=1) in self.predictDay.predictDates:
            self.predictDay.predictDates.remove (date.today () - timedelta (days=1))
        if not (self.predictDay.predictDates):
            logging.warning ('Invalid Date!')
            self.invalidDate = 1
            return self.invalidDate

    def get_STPrediction(self, from_date, to_date, replace = False) -> dict:
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
            self.R.processed_X_train = self.R.unpickle_Data ('Preprocessed_X_Train_STLF_')
            self.R.regressors = self.R.unpickle_Data ('Regressors_STLF_')
            logging.info ('Trained Algorithms data has fetched successfully ... ')
            predictor = STPredictor (self.R.processed_X_train, self.R.regressors)
        except Exception as inst:
            print (inst)
            msg = 'No train history available! Please train the model!'
            logging.warning (msg)
            result = dict ({'English':msg, 'Farsi':'تاریخچه‌ای از آموزش مدل در دسترس نیست ... لطفا مدل را آموزش دهید'})
            return result   

        self.output = STOutput (self.predictDay.predictDates, self.R.dataSet.headers)
        logging.info ('Trying to complete features of the predict days ...')
        outputFeatures = STFeaturesData (self.R.dataSet.featuresData.data)
        d = self.output.predictDates [0]
        dates = []
        while d != self.output.predictDates [-1] + timedelta (days=1):
            if d != date.today () - timedelta (days = 1):
                dates.append (d)
            d += timedelta (days=1)
        features = outputFeatures.get_Features (dates)
        if isinstance(features, bool) and not (features):
            if outputFeatures.weatherDataUnavailable:
                logging.warning ('Weather Data Unavailable!')
                result = dict ({'English':'No internet connection!', 'Farsi':'اتصال اینترنت برقرار نیست'})
                return result
            if outputFeatures.calendarDataUnavailable:
                logging.warning ('Calendar Data Unavailable!')
                result = dict ({'English':'No internet connection!', 'Farsi':'اتصال اینترنت برقرار نیست'})
                return result

        try:
            logging.info ('Trying to predict load ...')
            predictor.predict (self.output.predictDates, self.R, features, self.output, replace = replace)
        except Exception as inst:
            print (inst)
            logging.warning (inst)
            return None
        if replace:
            self.trainSTLF ()
        self.output.convert_DatatoDict (from_date, to_date)
        logging.info ('Load predicted successfully!')
        return self.output.dataDictionary

    def get_MTPrediction(self, from_date, to_date) -> dict:
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
            self.R.processed_X_train = self.R.unpickle_Data ('Preprocessed_X_Train_MTLF_')
            self.R.regressors1 = self.R.unpickle_Data ('Regressors1_MTLF_')
            self.R.regressors2 = self.R.unpickle_Data ('Regressors2_MTLF_')
            self.R.regressors3 = self.R.unpickle_Data ('Regressors3_MTLF_')
            self.R.regressors4 = self.R.unpickle_Data ('Regressors4_MTLF_')
            logging.info ('Trained Algorithms data has fetched successfully ... ')
            predictor = MTPredictor (self.R.processed_X_train, self.R.regressors1, self.R.regressors2, self.R.regressors3, self.R.regressors4)
        except Exception as inst:
            print (inst)
            msg = 'No train history available! Please train the model!'
            logging.warning (msg)
            result = dict ({'English':msg, 'Farsi':'تاریخچه‌ای از آموزش مدل در دسترس نیست ... لطفا مدل را آموزش دهید'})
            return result   

        self.output = MTOutput (self.predictDay.predictDates, self.R.dataSet.headers)
        logging.info ('Trying to complete features of the predict days ...')
        outputFeatures = MTFeaturesData (self.R.dataSet.featuresData.data)
        d = self.output.predictDates [0]
        dates = []
        while d != self.output.predictDates [-1] + timedelta (days=1):
            if d != date.today () - timedelta (days = 1):
                dates.append (d)
            d += timedelta (days=1)
        features = outputFeatures.get_Features (dates)
        if isinstance(features, bool) and not (features):
            if outputFeatures.weatherDataUnavailable:
                logging.warning ('Weather Data Unavailable!')
                result = dict ({'English':'No internet connection!', 'Farsi':'اتصال اینترنت برقرار نیست'})
                return result
            if outputFeatures.calendarDataUnavailable:
                logging.warning ('Calendar Data Unavailable!')
                result = dict ({'English':'No internet connection!', 'Farsi':'اتصال اینترنت برقرار نیست'})
                return result

        try:
            logging.info ('Trying to predict load ...')
            predictor.predict (self.output.predictDates, self.R, features, self.output)
        except Exception as inst:
            print (inst)
            logging.warning (inst)
            return None
        self.output.convert_DatatoDict (from_date, to_date)
        logging.info ('Load predicted successfully!')
        return self.output.dataDictionary

    def export_Prediction (self, from_date, to_date, file_path, predictionMode)->bool:
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
            self.R.export_PredictionAsXLSX (from_date, to_date, file_path, predictionMode=predictionMode)
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

    def trainSTLF(self, queue = None) -> bool:
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
            self.__train_STLF__(queue)
        except Exception as inst:
            print(inst)
            logging.error(inst)

    def __train_STLF__(self, queue):
        logging.info ('Preparing data ...')
        X_train, y_train = self.R.get_ShortTermTrainSet ()
        X_train = IndependentVariables.prepare_Data_STLF (X_train)
        self.R.pickle_Data (X_train, 'Preprocessed_X_Train_STLF_')
        trainer = Trainer (self.R, X_train, y_train)
        if queue:
            t = ThreadedTask (trainer.trainSTLF, queue)
            t.start()
        else:
            trainer.trainSTLF ()
        logging.info ('Model trained successfully!')

    def trainMTLF(self, queue = None) -> bool:
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
            self.__train_MTLF__(queue)
        except Exception as inst:
            print(inst)
            logging.error(inst)

    def __train_MTLF__(self, queue):
        logging.info ('Preparing data ...')
        X_train, y_train = self.R.get_MidTermTrainSet ()
        X_train = IndependentVariables.prepare_Data_MTLF (X_train)
        self.R.pickle_Data (X_train, 'Preprocessed_X_Train_MTLF_')
        trainer = Trainer (self.R, X_train, y_train)
        if queue:
            t = ThreadedTask (trainer.trainMTLF, queue)
            t.start()
        else:
            trainer.trainMTLF ()
        logging.info ('Model trained successfully!')    

    def select_DataSet (self, mode):
        self.R.select_DataSet (mode)

    def edit_DataSet(self):
        logging.info (f'Attempted to edit dataSet{self.R.selectedDataSet} ... ')
        if not (self.pathToLoadData) or not (os.path.isfile (self.pathToLoadData)):
            logging.warning ('There is no load data imported!')
            return "No load Data! \"Import CORRECT Load Data\" first!"

        if DataFile.check_ForNull (self.pathToLoadData):
            return self.__report__(
                'Please make sure your load data is complete and try again!',
                'Please make sure your load data is complete and try again! There may be blank cells in your load data! Please fill in the blank cells or delete the row with Nan values!',
                'لطفاً از کامل بودن اطلاعات بار اطمینان حاصل کنید و مجدداً تلاش نمایید! اگر در داده‌ها خانه‌های خالی وجود دارد، سطر مربوطه را حذف نمایید',
            )

        if DataFile.check_ForZero (self.pathToLoadData):
            return self.__report__(
                'Please make sure your load data values are non-zero and try again!',
                'Please make sure your load data is correct and try again! There may be values of zero in your load data!',
                'لطفاً از صحیح بودن اطلاعات بار اطمینان حاصل کنید و مجدداً تلاش نمایید! اگر در داده‌ها مقادیر صفر وجود دارد، مقادیر درست را وارد نمایید',
            )

        loadData = pd.read_excel (self.pathToLoadData, engine='openpyxl')

        newLoadData = HistoricalLoad (self.R.dataSet, loadData = loadData)
        try:
            result = self.R.dataSet.edit_LoadData (newLoadData.loadData)

            if isinstance (result, dict):
                logging.warning (result ['English'])
                return result
            else:
                self.R.pickle_Data (self.R.dataSet.featuresData.data, 'FeaturesData')
                self.R.pickle_Data (self.R.dataSet.loadData.data, 'LoadData')
                self.trainSTLF ()
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

    def determine_TrainEndDate (self):
        logging.info ('Trying to determine train end date ...')
        self.R.dataSet.determine_EndDate ()
        trainEndDate = JalaliDate (self.R.dataSet.endDate)
        logging.info ('Train end date determined successfully!')
        return trainEndDate

    def analyze_Prediction (self, from_date, to_date, predictionMode):
        logging.info (f'Attempted to analyze prediction ({from_date} - {to_date})')
        logging.info ('Trying to get output history ...')
        self.R.get_PredictedValues (from_date, to_date, predictionMode)

        if not (self.R.predictedDataHistory):
            msg = 'Invalid Date! The load you selected has not been predicted yet!'
            logging.warning (msg)
            result = dict ({'English':msg, 'Farsi':'بازه نامعتبر! بار بازه انتخاب شده، هنوز پیش‌بینی نشده است'})
            return result

        dates = []
        for i in range (len (self.R.predictedDataHistory)):
            dates.append (self.R.predictedDataHistory [i][1])

        logging.info (f'Trying to get the actual values from dataSet{self.R.selectedDataSet}')
        for i in range (len (dates)):
            dates [i] = dates [i].to_gregorian ()
        headers = self.R.dataSet.loadData.headers [-26:-2]
        headers.insert (0, 'Date')
        actualValues = self.R.dataSet.loadData.get_DataByDate (dates, headers)
        for i in range (len (actualValues)):
            actualValues [i][0] = JalaliDate (actualValues[i][0])
        for i in range (len (actualValues)):
            actualValues [i].insert (0, 'Actual')

        if not (actualValues):
            msg = 'No actual data! Please update the dataset!'
            logging.warning (msg)
            result = dict ({'English':msg, 'Farsi':'مقادیر واقعی بازه مورد نظر در دسترس نیست! لطفاً دیتاست را کامل نمایید'})
            return result

        self.predictionAnalysis = Analysis (actualValues, self.R.predictedDataHistory)
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
            Repository.export_AsXLSX (self.predictionAnalysis.exportableOutput, file_path)
            logging.info (f'Analysis results exported successfully! ({file_path})')
            return True
        except Exception as inst:
            logging.warning (inst)
            logging.warning ('Analysis results are not available!')
            print (inst)
            return False

    def plot_AnalysisResults(self, from_date, to_date):
        logging.info (f'Attempted to plot analysis results ... ({from_date} - {to_date})')
        if from_date != to_date:
            return self.__report__(
                "Sorry! Only one prediction result can be shown!", "Sorry! Only one prediction result can be shown!",
                'متاسفانه امکان نمایش نمودارهای بیش از یک روز وجود ندارد ... لطفاً فقط یک تاریخ را انتخاب نمایید',
            )

        logging.info ('Plotting ... ')
        if not (self.predictionAnalysis):
            return self.__report__(
                'You should try "Analyze Prediction" first!', 'You should try "Analyze Prediction" first!',
                'لازم است ابتدا آنالیز پیش‌بینی انجام شود',
            )

        fig = self.predictionAnalysis.plot_AnalysisResults (from_date)
        if isinstance (fig, dict):
            logging.warning (fig ['English'])
        else:
            logging.info ('Prediction analysis ploted successfully!')

        return fig

    def save_AnalysisPlot (self, file_path):
        logging.info ('Attempted to save analysis plot ...')
        try:
            result = Repository.save_Plot (self.predictionAnalysis.fig, file_path)
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

    def export_STPredictionHistory (self, file_path):
        logging.info ('Attempted to export prediction history ...')
        try:
            self.R.export_AllPredictionHistory (file_path)
            logging.info ('Prediction history exported successfully!')
            return True
        except Exception as inst:
            print (inst)
            logging.error (inst)
            return False
    
    def export_MTPredictionHistory (self, file_path):
        logging.info ('Attempted to export prediction history ...')
        try:
            self.R.export_AllPredictionHistory (file_path, midTerm = True)
            logging.info ('Prediction history exported successfully!')
            return True
        except Exception as inst:
            print (inst)
            logging.error (inst)
            return False

    def get_LastTrainDate (self):
        logging.info ('Trying to get the last train date ...')
        try:
            self.R.lastTrainDateST = self.R.unpickle_Data ('TrainDate_STLF_')
            logging.info (f'last train date fetched successfully! ({self.R.lastTrainDateST})')
            return self.R.lastTrainDateST
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