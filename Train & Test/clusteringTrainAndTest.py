from sklearn.cluster import KMeans
import sklearn.cluster as cluster
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np


class Clusterer ():
    def __init__ (self, data):
        self.data = data

    # def find_TheOptimumNumberOfClustersForKMeans (self):
    #     wcss = []
    #     for i in range(1, 21):
    #         kmeans = KMeans(n_clusters = i, init = 'k-means++', random_state = 42)
    #         kmeans.fit (self.data)
    #         wcss.append (kmeans.inertia_)

    #     plt.plot(range(1, 21), wcss)
    #     plt.title('The Elbow Method')
    #     plt.xlabel('Number of clusters')
    #     plt.ylabel('WCSS')
    #     plt.grid ()
    #     plt.savefig ('The Elbow Method for Clustering.jpg')
    #     plt.show ()
    #     self.numberOfClusters = int (input ("Enter the number of clusters according to the curve: "))

    # def kMeans (self):
    #     self.find_TheOptimumNumberOfClustersForKMeans ()
    #     self.kmeans = KMeans(n_clusters = self.numberOfClusters, init = 'k-means++', random_state = 42)
    #     self.kmeans.fit (self.data)
    #     self.labels = self.kmeans.labels_
    #     self.save_ClusterCenters ()
    #     self.plot_Centroids ()

    # def save_ClusterCenters (self):
    #     self.clusterCenters = pd.DataFrame ()
    #     for i in range (self.numberOfClusters):
    #         self.clusterCenters [f'{i}'] = self.kmeans.cluster_centers_ [i]
    #     self.clusterCenters.to_excel ('Cluster Centers.xlsx')

    # def plot_Centroids (self):
    #     fig = plt.figure ()
    #     ax = plt.axes (projection = '3d')           
    #     xData = self.clusterCenters.iloc [0,:]
    #     yData = self.clusterCenters.iloc [1,:]
    #     zData = self.clusterCenters.iloc [2,:]
    #     ax.scatter3D (xData, yData, zData)
    #     plt.show ()
    #     plt.savefig ('ClusterCenters.jpg')

    def plot_LoadData (self):
        # fig = plt.figure ()
        # self.ax = plt.axes (projection = '3d')
        xData = self.data [0]
        yData = self.data [1]
        # zData = self.data [2]
        # self.ax.scatter3D (xData, yData, zData)

    def plot_Clusters (self, algorithm, args, kwds):
        # self.plot_LoadData ()
        self.numberOfClusters = 2
        self.labels = algorithm (*args, **kwds).fit_predict (self.data)
        palette = sns.color_palette ('deep', np.unique (self.labels).max () + 1)
        colors = [palette [x] if x >= 0 else (0.0, 0.0, 0.0) for x in self.labels]
        # self.ax = plt.axes (projection = '3d')
        plt.scatter (self.data.T[0], self.data.T[1], c = colors)
        plt.title ('Clusters Found by {}'.format (str (algorithm.__name__)), fontsize = 24)
        plt.show ()

    def kMeans (self):
        self.numberOfClusters = 2
        self.kmeans = KMeans (n_clusters = self.numberOfClusters, init = 'k-means++', random_state = 42)
        self.kmeans.fit (self.data)
        self.labels = self.kmeans.labels_  



    

