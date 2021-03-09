from repositoryTrainAndTest import Repository
from predictorTrainAndTest import Predictor
from trainerTrainAndTest import Trainer

def main ():
    R = Repository ()
    R.get_TrainSet ()
    R.prepare_Data ()

    trainer = Trainer (R.X_train, R.y_train)
    trainer.train ()
    #with clustering
    # predictor = Predictor (R.X_train, R.y_train, trainer.regressors, classifier = trainer.classifier, clusterer = trainer.clusterer, )
    #without clustering
    predictor = Predictor (R.X_train, R.y_train, trainer.regressors)
    predictor.predict (R)

if __name__ == "__main__":
    main ()