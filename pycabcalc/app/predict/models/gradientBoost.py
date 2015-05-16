import sklearn
import sklearn.linear_model as linear
import sklearn.ensemble as ensemble
import numpy as np

from sklearn.cross_validation import train_test_split
from sklearn.utils import check_random_state

#Validation
import err_score as err

"""
http://scikit-learn.org/stable/auto_examples/ensemble/plot_gradient_boosting_regression.html
"""
def run(X_train, X_test, y_train, y_test, n_estimators=500,  max_depth=4, learning_rate = 0.01):
    
    if len(X_train.shape)==1:
        X_train = np.array([X_train]).T
        X_test = np.array([X_test]).T

    # Prepare parameters
    params = {'n_estimators': n_estimators, 'max_depth': max_depth, 'min_samples_split': 1,
          'learning_rate': learning_rate, 'loss': 'ls'}

    clf = ensemble.GradientBoostingRegressor(**params)

    #Fit the model
    clf.fit(X_train, y_train)

    y_predicted = clf.predict(X_test)

    #Feature importance
    feature_importance_vals = clf.feature_importances_ #value of importance for each feature in X
    feature_importance_indx = np.argsort(feature_importance_vals)

    #Validation
    rmse = err.RMSE(y_predicted, y_test)
    r2 = err.Rsquare(y_predicted, y_test)

    return y_predicted, rmse, r2, feature_importance_indx