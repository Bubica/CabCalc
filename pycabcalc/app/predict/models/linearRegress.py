import sklearn
import sklearn.linear_model as linear
import sklearn.ensemble as ensamble
import numpy as np

from sklearn.cross_validation import train_test_split
from sklearn.utils import check_random_state

#Validation
import err_score as err

def run(X_train, X_test, y_train, y_test):
    
    if len(X_train.shape)==1:
        X_train = np.array([X_train]).T
        X_test = np.array([X_test]).T

    linregress =linear.LinearRegression

    ens = linregress().fit(X_train, y_train)

    y_predicted = ens.predict(X_test)

    #Validation
    rmse = err.RMSE(y_predicted, y_test)
    r2 = err.Rsquare(y_predicted, y_test)

    return y_predicted, rmse, r2, None #Last value refers to feature importance index that this model does not provide