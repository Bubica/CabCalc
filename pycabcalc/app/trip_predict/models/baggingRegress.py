import sklearn
import sklearn.linear_model as linear
import sklearn.ensemble as ensamble
import numpy as np

from sklearn.cross_validation import train_test_split
from sklearn.utils import check_random_state

#Validation
import ..err.err_score as err

def run(X_train, X_test, y_train, y_test, n_estimators=10, max_samples=10):
    
    if len(X_train.shape)==1:
        X_train = np.array([X_train]).T
        X_test = np.array([X_test]).T

    n_estimators = 5
    linregress =linear.LinearRegression
    logregress = linear.LogisticRegression
    rng = check_random_state(0) #random state object from np.random

    ens = ensamble.BaggingRegressor(base_estimator=linregress(), random_state=rng, max_samples=max_samples, n_estimators=n_estimators).fit(X_train, y_train)

    y_predicted = ens.predict(X_test)

    #Validation
    rmse = err.RMSE(y_predicted, y_test)
    r2 = err.Rsquare(y_predicted, y_test)

    return y_predicted, rmse, r2, None #Last value refers to feature importance index that this model does not provide