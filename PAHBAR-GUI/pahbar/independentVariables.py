from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
import numpy as np

class IndependentVariables ():
    def __init__ (self, data):
        self.data = data

    def encode_OneHot_FitTransform_MTLF (self):
        self.ct_WeekDays = ColumnTransformer ([('one_hot_encoder', OneHotEncoder(), [8])], remainder='passthrough')
        self.data = np.array (self.ct_WeekDays.fit_transform (self.data), dtype= 'float64')
        self.data = self.data [:, 1:]

    def encode_OneHot_Transform_MTLF (self, X_train):
        self.data = np.array (X_train.ct_WeekDays.transform (self.data), dtype= 'float64')
        self.data = self.data [:, 1:]

    def fit_FeatureScaler_MTLF (self):
        self.sc_X = StandardScaler()
        self.sc_X.fit (self.data [:, 14:])

    def scale_Features_MTLF (self, X_train):        
        self.data [:, 14:]= X_train.sc_X.transform(self.data [:, 14:])

    def encode_OneHot_FitTransform_STLF (self):
        self.ct_WeekDays = ColumnTransformer ([('one_hot_encoder', OneHotEncoder(), [9])], remainder='passthrough')
        self.data = np.array (self.ct_WeekDays.fit_transform (self.data), dtype= 'float64')
        self.data = self.data [:, 1:]

    def encode_OneHot_Transform_STLF (self, X_train):
        self.data = np.array (X_train.ct_WeekDays.transform (self.data), dtype= 'float64')
        self.data = self.data [:, 1:]

    def fit_FeatureScaler_STLF (self):
        self.sc_X = StandardScaler()
        self.sc_X.fit (self.data [:, 14:])

    def scale_Features_STLF (self, X_train):        
        self.data [:, 14:]= X_train.sc_X.transform(self.data [:, 14:])

    def prepare_Data_MTLF (X_train):
        X_train.encode_OneHot_FitTransform_MTLF ()
        X_train.fit_FeatureScaler_MTLF ()
        X_train.scale_Features_MTLF (X_train)
        return X_train

    def prepare_Data_STLF (X_train):
        X_train.encode_OneHot_FitTransform_STLF ()
        X_train.fit_FeatureScaler_STLF ()
        X_train.scale_Features_STLF (X_train)
        return X_train