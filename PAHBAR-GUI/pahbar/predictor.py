from pahbar.predictDay import PredictDay
from pahbar.independentVariables import IndependentVariables
import numpy as np
import pickle

class Predictor:
    def __init__ (self, X_train, regressors):
        self.X_train = X_train
        self.regressors = regressors
        
    def predict (self, output, R):
        for row in range (len (output.predictDates)):
            output.predictDays [row].add_HistoricalLoadData (R)
            output.add_HistoricalLoadData (row)
            inputX = output.predictDaysFeatures

            y_pred = []
            d = [output.predictDates [row]]
            for hour in range (24):
                X = IndependentVariables (inputX.iloc [row * 24 + hour] ['Eide Mazhabi':'YesterdayLoad'].values)
                X.data = np.array (X.data).reshape (1,-1)
                X.encode_OneHot_Transform (self.X_train)
                X.scale_Features (self.X_train)            
                y_pred.append (self.regressors.predict (X.data))

                d.append (y_pred [hour][0])
            output.output.loc [row] = d
            output.make_ListOfOneRow (row)
            # y_pred = y_pred.reshape (1,-1)
            
            
            for hour in range (24):
                R.dataSet.data.loc [R.dataSet.numberOfRecords] = output.predictedDayList [row * 24 + hour]
                R.dataSet.numberOfRecords += 1
            temp_r =  len (R.outputHistory)  
            R.outputHistory.loc [len (R.outputHistory)] = output.predictedLoad

        R.dataSet.define_Path (R.selectedDataSet, R.path)   
        R.dataSet.revive ()
        R.save_outputHistory ()