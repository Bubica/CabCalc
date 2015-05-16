import numpy as np
from sklearn.metrics import mean_squared_error
from math import sqrt

def Rsquare(y_predicted, y_test):
	return 1 - (np.sum((y_predicted - y_test)**2) / np.sum((y_test - np.mean(y_test))**2))

def RMSE(y_predicted, y_test):
    return sqrt(mean_squared_error(y_test, y_predicted))