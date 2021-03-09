from sklearn.cluster import KMeans
import pandas as pd
import numpy as np


class Clusterer ():
    def __init__ (self, data):
        self.data = data

    def kMeans (self):
        self.numberOfClusters = 2
        self.kmeans = KMeans (n_clusters = self.numberOfClusters, init = 'k-means++', random_state = 42)
        self.kmeans.fit (self.data)
        self.labels = self.kmeans.labels_  