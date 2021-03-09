import numpy as np
class Temperature:
    def __init__ (self, data):
        self.data = data

    def convert_ToCentigrade (self):
        self.values = np.zeros ((len (self.data), len (self.data [0])))
        for i in range (len (self.data)):
            for j in range (len (self.data [i])):
                self.values [i][j] = (float (self.data [i][j]) - 32)*5/9