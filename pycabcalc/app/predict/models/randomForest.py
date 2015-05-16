import sklearn
import sklearn.linear_model as linear
import sklearn.ensemble as ensemble
import numpy as np

from sklearn.cross_validation import train_test_split
from sklearn.utils import check_random_state

#Validation
import err_score as err

"""
http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html
"""
def run(X_train, X_test, y_train, y_test, n_estimators=10,  max_depth=None):
    
    if len(X_train.shape)==1:
        X_train = np.array([X_train]).T
        X_test = np.array([X_test]).T

    #Set default values
    if max_depth <0:
        max_depth = None

    if n_estimators < 0:
        n_estimators = None

    forest = ensemble.RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, max_features=None, n_jobs=-1)
    forest.fit(X_train, y_train)

    y_predicted = forest.predict(X_test)

    #Feature importance
    feature_importance_vals = forest.feature_importances_ #value of importance for each feature in X
    feature_importance_indx = np.argsort(feature_importance_vals)

    #Validation
    rmse = err.RMSE(y_predicted, y_test)
    r2 = err.Rsquare(y_predicted, y_test)

    return y_predicted, rmse, r2, feature_importance_indx