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

            y_pred = []
            d = [output.predictDates [row]]
            for hour in range (24):
                output.predictDays [row].add_PreviousLoad (hour + 1)
                output.add_PreviousHourLoad (row , hour)
                inputX = output.predictDaysFeatures.iloc [row * 24 + hour] ['Eide Mazhabi':'PreviousLoad'].values
                X = IndependentVariables (inputX)
                X.data = np.array (X.data).reshape (1,-1)
                X.encode_OneHot_Transform (self.X_train)
                X.scale_Features (self.X_train)            
                y_pred.append (self.regressors.predict (X.data))

                d.append (y_pred [hour][0])
                output.make_ListOfOneRow (row, hour, y_pred [hour][0])
                R.dataSet.data.loc [R.dataSet.numberOfRecords] = output.predictedHourList [row * 24 + hour]
                R.dataSet.numberOfRecords += 1

            output.make_ListOfPredictedLoad (d)
            output.output.loc [row] = d
            
            # y_pred = y_pred.reshape (1,-1)
            temp_r =  len (R.outputHistory)  
            R.outputHistory.loc [len (R.outputHistory)] = output.predictedLoad

        R.dataSet.define_Path (R.selectedDataSet, R.path)   
        R.dataSet.revive ()
        R.save_outputHistory ()