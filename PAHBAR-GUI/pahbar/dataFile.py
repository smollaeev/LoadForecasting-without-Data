import pandas as pd

class DataFile:
    def check_ForNull(path):
        data = pd.read_excel (path, engine='openpyxl')
        temp = data.isnull().values.any()
        return bool(temp)
        
    def check_ForZero(path):
        data = pd.read_excel (path, engine='openpyxl')
        zeroTemp = data.eq(0).any().any()
        return bool(zeroTemp)
            