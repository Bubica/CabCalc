import statsmodels.api as sm
import numpy as np

from sklearn.preprocessing import normalize


from numpy.polynomial import polynomial
from pandas.stats.api import ols
import pandas as pd

#Validation
import ..err.err_score as err

def run(X_train, X_test, y_train, y_test):

    """
    if len(X_train.shape)==1:
        X_train = np.array([X_train]).T
        X_test = np.array([X_test]).T
    """

    res_ols = ols(y=pd.Series(y_train), x=pd.DataFrame(X_train))
    residuals = res_ols.resid.values  #residuals

    resid_mm = np.max(np.abs(residuals))
    resid_mean = np.mean(residuals)
    w_est = np.abs(np.round((residuals-resid_mean)/resid_mm,3))

    res_wls = ols(y=pd.Series(y_train), x=pd.DataFrame(X_train), weights = w_est)

    y_predicted = res_wls.predict(x = pd.DataFrame(X_test))

    #Validation
    rmse = err.RMSE(y_predicted, y_test)
    r2 = err.Rsquare(y_predicted, y_test)

    return y_predicted, rmse, r2, None #Last value refers to feature importance index that this model does not provide