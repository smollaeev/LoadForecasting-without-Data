from repositoryTrainAndTest import Repository
from predictorTrainAndTest import Predictor
from trainerTrainAndTest import Trainer

def main ():
    dataSetType = input ('Please enter the DataSet Name: ')
    R = Repository (dataSetType)
    R.get_TrainSet ()
    R.prepare_Data ()

    trainer = Trainer (R.X_train, R.y_train, dataSetType, R.variables)
    trainer.train ()
    #with clustering
    # predictor = Predictor (R.X_train, R.y_train, trainer.regressors, classifier = trainer.classifier, clusterer = trainer.clusterer, )
    #without clustering
    predictor = Predictor (R.X_train, trainer.X_train1, trainer.X_train2, trainer.X_train3, trainer.X_train4, trainer.y_train1, trainer.y_train2, trainer.y_train3, trainer.y_train4, trainer.regressors1, trainer.regressors2, trainer.regressors3, trainer.regressors4, dataSetType)
    predictor.predict (R)

if __name__ == "__main__":
    main ()