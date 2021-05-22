from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
import numpy as np

class IndependentVariables ():
    def __init__ (self, data):
        self.data = data

    def encode_OneHot_FitTransform (self):
        self.ct_WeekDays = ColumnTransformer ([('one_hot_encoder', OneHotEncoder(), [7])], remainder='passthrough')
        self.data = np.array (self.ct_WeekDays.fit_transform (self.data), dtype= 'float64')
        self.data = self.data [:, 1:]

    def encode_OneHot_Transform (self, X_train):
        self.data = np.array (X_train.ct_WeekDays.transform (self.data), dtype= 'float64')
        self.data = self.data [:, 1:]

    def fit_FeatureScaler (self):
        self.sc_X = StandardScaler()
        self.sc_X.fit (self.data [:, 13:])

    def scale_Features (self, X_train):        
        self.data [:, 13:]= X_train.sc_X.transform(self.data [:, 13:])

    def prepare_Data (X_train):
        X_train.encode_OneHot_FitTransform ()
        X_train.fit_FeatureScaler ()
        X_train.scale_Features (X_train)
        return X_train