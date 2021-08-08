from enum import Enum
from pahbar.logic import Logic

class Event(Enum):
    IMPORT_DATA_BUTTON = 'GET_DATA_BUTTON'
    EXPORT_DATA_BUTTON = 'EXPORT_DATA_BUTTON'
    FETCH_ONLINE_DATA = 'FETCH_ONLINE_DATA'
    EDIT_DATA = 'EDIT_DATA'
    DISPLAY_DATA_BUTTON = 'DISPLAY_DATA_BUTTON'
    DATA_DISPLAY_RADIO_BUTTON = 'DATA_DISPLAY_RADIO_BUTTON'
    DISPLAY_ST_PREDICTION_BUTTON = 'DISPLAY_ST_PREDICTION_BUTTON'
    DISPLAY_MT_PREDICTION_BUTTON = 'DISPLAY_MT_PREDICTION_BUTTON'
    EXPORT_Prediction_BUTTON = 'EXPORT_Prediction_BUTTON'
    STLF_TRAIN_BUTTON = 'STLF_TRAIN_BUTTON'
    MTLF_TRAIN_BUTTON = 'MTLF_TRAIN_BUTTON'
    DOCUMENTATION = 'DOCUMENTATION'
    DETERMINE_TRAINENDDATE = 'DETERMINE_TRAINENDDATE'
    ANALYZE_PREDICTION = 'ANALYZE_PREDICTION'
    EXPORT_ANALYSIS_RESULTS = 'EXPORT_ANALYSIS_RESULTS'
    PLOT_RESULTS = 'PLOT_RESULTS'
    SAVE_ANALYSIS_PLOT = 'SAVE_ANALYSIS_PLOT'
    CALCULATE_ERRORATTRIBUTES = 'CALCULATE_ERRORATTRIBUTES'
    EXPORT_STLF_HISTORY_BUTTON = 'EXPORT_STLF_HISTORY_BUTTON'
    EXPORT_MTLF_HISTORY_BUTTON = 'EXPORT_MTLF_HISTORY_BUTTON'
    GET_LAST_TRAIN_DATE = 'GET_LAST_TRAIN_DATE'
    REMOVE_FILE_PATH = 'REMOVE_FILE_PATH'

class EventHandler():
    def __init__(self, data_folder_path):
        self.prediction = Logic(data_folder_path)

    def handle(self, event, **kwargs):
        if event == Event.IMPORT_DATA_BUTTON :
            return self.prediction.import_Data(**kwargs)
        elif event == Event.EXPORT_DATA_BUTTON :
            return self.prediction.export_Data(**kwargs)
        elif event == Event.FETCH_ONLINE_DATA :
            return self.prediction.fetch_OnlineData()
        elif event == Event.DISPLAY_DATA_BUTTON :
            return self.prediction.get_Data(**kwargs)
        elif event == Event.DISPLAY_ST_PREDICTION_BUTTON :
            return self.prediction.get_STPrediction(**kwargs)
        elif event == Event.DISPLAY_MT_PREDICTION_BUTTON :
            return self.prediction.get_MTPrediction(**kwargs)
        elif event == Event.EXPORT_Prediction_BUTTON :
            return self.prediction.export_Prediction(**kwargs)
        elif event == Event.STLF_TRAIN_BUTTON :
            return self.prediction.trainSTLF(**kwargs)
        elif event == Event.MTLF_TRAIN_BUTTON :
            return self.prediction.trainMTLF(**kwargs)
        elif event == Event.DATA_DISPLAY_RADIO_BUTTON:
            self.prediction.select_DataSet (**kwargs)
        elif event == Event.EDIT_DATA:
            return self.prediction.edit_DataSet ()
        elif event == Event.DOCUMENTATION:
            self.prediction.show_Documentation ()
        elif event == Event.DETERMINE_TRAINENDDATE:
            return self.prediction.determine_TrainEndDate ()
        elif event == Event.ANALYZE_PREDICTION:
            return self.prediction.analyze_Prediction (**kwargs)
        elif event == Event.EXPORT_ANALYSIS_RESULTS:
            return self.prediction.export_AnalysisResults (**kwargs)
        elif event == Event.PLOT_RESULTS:
            return self.prediction.plot_AnalysisResults (**kwargs)  
        elif event == Event.SAVE_ANALYSIS_PLOT:
            return self.prediction.save_AnalysisPlot (**kwargs)
        elif event == Event.CALCULATE_ERRORATTRIBUTES:
            return self.prediction.calculate_ErrorAttributes ()
        elif event == Event.EXPORT_STLF_HISTORY_BUTTON:
            return self.prediction.export_STPredictionHistory (**kwargs)
        elif event == Event.EXPORT_MTLF_HISTORY_BUTTON:
            return self.prediction.export_MTPredictionHistory (**kwargs)
        elif event == Event.GET_LAST_TRAIN_DATE:
            return self.prediction.get_LastTrainDate ()
        elif event == Event.REMOVE_FILE_PATH:
            self.prediction.remove_FilePath ()
    
    def get_Mode (self):
        return self.prediction.get_Mode ()

    def remove_AnalysisHistory (self):
        self.prediction.remove_AnalysisHistory ()
    
    def determine_PredictDates (self, from_date, to_date):
        self.prediction.determine_PredictDates (from_date, to_date)
        return self.prediction.predictDay.predictDates    