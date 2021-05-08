from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
import numpy as np
# from sklearn.decomposition import PCA

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
        self.sc_X.fit (self.data [:, 6:])

    def scale_Features (self, X_train):        
        self.data [:, 6:] = X_train.sc_X.transform (self.data [:, 6:])