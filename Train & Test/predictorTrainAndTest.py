import datetime
import pandas as pd
import numpy as np
from independentVariablesTrainAndTest import IndependentVariables

class Predictor:
    def __init__ (self, X_train, X_train1, X_train2, X_train3, X_train4, y_train1, y_train2, y_train3, y_train4, regressors1, regressors2, regressors3, regressors4, dataSetType, classifier = None, clusterer = None):
        self.X_train = X_train
        self.X_train1 = X_train1
        self.X_train2 = X_train2
        self.X_train3 = X_train3
        self.X_train4 = X_train4
        self.y_train1 = y_train1
        self.y_train2 = y_train2
        self.y_train3 = y_train3
        self.y_train4 = y_train4
        self.classifier = classifier
        self.clusterer = clusterer
        self.regressors1 = regressors1
        self.regressors2 = regressors2
        self.regressors3 = regressors3
        self.regressors4 = regressors4
        self.dataSetType = dataSetType
        self.testSet = pd.read_excel (f'./Results/{datetime.date.today ()}/TestSet_{self.dataSetType}_{datetime.date.today ()}.xlsx', engine='openpyxl')
        self.variables = self.testSet.columns [1:-24]        

    def predict (self, R):
        X_test = R.X_test
        y_test = R.y_test

        # X_test.encode_Labels (self.X_train)
        
        X_test.encode_OneHot_Transform (self.X_train)
        X_test.scale_Features (self.X_train)

        self.X_test1 = IndependentVariables (np.append (X_test.data [:, :28], X_test.data [:, 46:52], axis=1))
        self.X_test2 = IndependentVariables (np.append (np.append (X_test.data [:, :22], X_test.data [:, 28:35], axis=1), X_test.data [:, 52:59], axis=1))
        self.X_test3 = IndependentVariables (np.append (np.append (X_test.data [:, :22], X_test.data [:, 35:42], axis=1), X_test.data [:, 59:66], axis=1))
        self.X_test4 = IndependentVariables (np.append (np.append (X_test.data [:, :22], X_test.data [:, 42:46], axis=1), X_test.data [:, 66:70], axis=1))

        self.y_test1 = y_test [:, :6]
        self.y_test2 = y_test [:, 6:13]
        self.y_test3 = y_test [:, 13:20]
        self.y_test4 = y_test [:, 20:]

        # X_testClassifier = self.fs.transform(X_test.data)
        try:
            predictedClasses = self.classifier.predict(X_test.data)
        except:
            print ('without clustering')
        y_pred1 = np.zeros ((len (self.X_test1.data), 6))
        y_pred2 = np.zeros ((len (self.X_test2.data), 7))
        y_pred3 = np.zeros ((len (self.X_test3.data), 7))
        y_pred4 = np.zeros ((len (self.X_test4.data), 4))

        try:
            for i in range (len (X_test.data)):
                for j in range (self.clusterer.numberOfClusters):
                    if predictedClasses [i] == j:
                        y_pred [i] = (self.regressors [j].predict (X_test.data [i].reshape (1,-1)))

        except:
            for i in range (len (X_test.data)): 
                pred = self.regressors1.predict (self.X_test1.data [i].reshape (1,-1))
                y_pred1 [i] = pred
                y_pred2 [i] = (self.regressors2.predict (self.X_test2.data [i].reshape (1,-1)))
                y_pred3 [i] = (self.regressors3.predict (self.X_test3.data [i].reshape (1,-1)))
                y_pred4 [i] = (self.regressors4.predict (self.X_test4.data [i].reshape (1,-1)))

        y_pred = np.append (np.append (np.append (y_pred1, y_pred2, axis=1), y_pred3, axis=1), y_pred4, axis=1)
        errors = []
        for i in range (len (y_pred)):
            errors.append ([abs((y-x)/y)*100 for x, y in zip(y_pred [i], y_test [i])])
        errors = np.array (errors)
        for i in range (24):
            self.testSet [f'Prediction{i+1}'] = y_pred [:, i]
        for i in range (24):
            self.testSet [f'error{i+1}'] = errors [:,i]
        self.testSet.to_excel (f'./Results/{datetime.date.today ()}/TestSet_{self.dataSetType}_{datetime.date.today ()}.xlsx')
        # sns.displot (x = errors)
        # plt.show ()
        # error = (sum([abs((y-x)/y) for x, y in zip(y_pred, y_test)])/len(y_test))*100
        dailyErrors = []
        for i in range (len (errors)):
            dailyErrors.append (np.average (errors [i]))
        averageError = np.average (dailyErrors)
        standardDevOfError = np.std (dailyErrors)
        varianceOfError = np.var (dailyErrors)
        print (f'Average = {averageError}')
        print (f'StdDev = {standardDevOfError}')
        print (f'Variance= {varianceOfError}')
        f = open (f'./Results/{datetime.date.today()}/Results&Description-{self.dataSetType}-{datetime.date.today()}.txt', "w+")
        f.write (f'Description:\n {self.dataSetType} \n Variables = {self.variables} \n Average = {averageError} \n StdDev = {standardDevOfError} \n Variance= {varianceOfError}')
        f.close ()