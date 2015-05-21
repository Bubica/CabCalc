import setup as config
import pandas as pd
from val_predict import ValidationPredictor
import sys
import log



folder = "/Users/bubica/insight_link/code/python/taxi/validation/result_logs/" #result logs folder


class Validator(object):
    
    """ Main class for running the validation """

    def __init__(self):
        self.predictor = ValidationPredictor()
        self.logger = log.Logger(folder+'validation_results.csv') 

        #Basic config stored in default.ini file
        config_fname = os.path.dirname(__file__)+"/"+"default.ini"
        config.set_config_file(config_fname)

        print "CONFIG FILE: ", config_fname
        print


    def run(self):

        expSetups = setup.loadExpSetups()
        modelSetups = setup.loadModelSetups()

        for is_ in range(len(expSetups)):

            #Update experimental setup - single data load for each model setup
            eSetup = expSetups.loc[is_]
            self.predictor.updateExpSetup(eSetup)

            print "Running experimental setup ", is_

            for im_ in range(len(modelSetups)):

                mSetup = modelSetups.loc[im_]

                print "        Running  model setup ", im_, mSetup

                self.predictor.updateModelSetup(mSetup) #Update model setup
                results = self.predictor.run() #Train the model and store results

                #LOG results
                self.logger.set_setup(eSetup, mSetup)
                self.logger.set_results(results)
                self.logger.log() #push to file


def main():
    validator = Validator()
    validator.run()


    # def _loadData(from_, to_, areaSz):
    #     # fetches all relevant data from the database and stores in the file
    #     # not the most elegant solution, but preserves persistance if the environment runs out of memory
    #     init()
    #     global params

    #     testset = itertools.product(params['routes'], params['cluster_sz_test']) #test setup

    #     tit=0
    #     for t in testset:
    #         print tit, t, "test_df_"+str(tit)+".csv"
            
    #         ps = gmh.getCoordFromAddress(t[0][0]) 
    #         pe = gmh.getCoordFromAddress(t[0][1]) 

    #         fn = "test_df_"+str(tit)+".csv"
    #         ft = open(folder + fn, 'w')

    #         print "Draw test cluster: ", t
    #         df_test = db_trip.query_Routes(ps,pe, t[1], lonLat=True, date_span = params['test_period'], fareJoin = True) 
    #         df_test = _trip_filter(df_test) #filter the data

    #         #Dump test sample to file
    #         df_test.to_csv(ft)
    #         ft.close()
    #         tit = tit+1



    # """
    # ############################### MODEL RUNNERS ################################
    # """

    # def runLinModels(self, df_train, df_test, data_func, params):

    #     """ Runs all (three) linear models and logs the results """

    #     logger = log.Logger() #log file set in the methods invoking this one
    #     X_train, X_test, y_train, y_test = data_func(df_train, df_test)

    #     #Run Linear regress
    #     print "LINEAR" 
    #     logger.log_model("LIN"); 
    #     if not logger.check_setup_logged(): 
    #         _, rmse, r2 = model_lin.run(X_train, X_test, y_train, y_test)
        
    #         logger.log_rmse(rmse);
    #         logger.log_r2(r2);
    #         logger.push()
    #         logger.reset_model()

    #     #Run weighted regress
    #     print "FLWS" 
    #     logger.log_model("FLWS");
    #     if not logger.check_setup_logged(): 
    #         try:
    #             _, rmse, r2 = model_fwls.run(X_train, X_test, y_train, y_test)
    #             logger.log_rmse(rmse);
    #             logger.log_r2(r2);
    #             logger.push()
    #             logger.reset_model()
    #         except Exception: 
    #             print "Skipping FLWS"
    #             pass #exception happens if the data is malformed (i.e. mutidimensional) - hack

    #     #Run Bag
    #     print "BAG" 
    #     mp = itertools.product(params['n_estimators']['BAG'], params['max_samples']['BAG'])
    #     for ip, jp in mp:

    #         logger.log_model("BAG")
    #         logger.log_param1(ip);
    #         logger.log_param2(jp);
    #         if logger.check_setup_logged(): continue
    #         _, rmse, r2 = model_bag.run(X_train, X_test, y_train, y_test, ip, jp)
            
    #         logger.log_rmse(rmse);
    #         logger.log_r2(r2);
    #         logger.push()
    #         logger.reset_model()


    # def runClassifRegressModels(self, df_train, df_test, data_func, params):

    #     """ Runs two regression classifiers and logs the results """

    #     logger = log.Logger()
    #     X_train, X_test, y_train, y_test = data_func(df_train, df_test)

    #     #Run random forest
    #     print "FOREST" 
    #     mp = itertools.product(params['n_estimators']['FOREST'], params['max_depth']['FOREST'])
    #     for ip, jp in mp:
    #         logger.log_model("FOREST")
    #         logger.log_param1(ip);
    #         logger.log_param2(jp);
    #         if logger.check_setup_logged(): continue
    #         yp, rmse, r2, fe = model_forest.run(X_train, X_test, y_train, y_test, ip, jp)
            
    #         logger.log_rmse(rmse);
    #         logger.log_r2(r2);
    #         logger.log_fe(fe);
    #         logger.push()
    #         logger.reset_model()

    #     #Run gradient
    #     print "GRAD" 
    #     mp = itertools.product(params['n_estimators']['GRAD'], params['max_depth']['GRAD'], params['learn_rate']['GRAD'])
    #     for ip, jp, kp in mp:

    #         logger.log_model("GRAD")
    #         logger.log_param1(ip);
    #         logger.log_param2(jp);
    #         logger.log_param3(kp)
    #         if logger.check_setup_logged(): continue

    #         yp, rmse, r2, fe = model_grad.run(X_train, X_test, y_train, y_test, ip, jp, kp)    
            
    #         logger.log_rmse(rmse);
    #         logger.log_r2(r2);
    #         logger.log_fe(fe);
    #         logger.push()
    #         logger.reset_model()


            
# """
# ############################### TRAIN & TEST DATA PREP ################################
# """

# def generate_test_data():
#     #fetches all train data form the database and stores in the file
#     # not the most elegant solution, but preserves persistance if the environment runs out of memory
#     init()
#     global params

#     testset = itertools.product(params['routes'], params['cluster_sz_test']) #test setup

#     tit=0
#     for t in testset:
#         print tit, t, "test_df_"+str(tit)+".csv"
        
#         ps = gmh.getCoordFromAddress(t[0][0]) 
#         pe = gmh.getCoordFromAddress(t[0][1]) 

#         fn = "test_df_"+str(tit)+".csv"
#         ft = open(folder + fn, 'w')

#         print "Draw test cluster: ", t
#         df_test = db_trip.query_Routes(ps,pe, t[1], lonLat=True, date_span = params['test_period'], fareJoin = True) 
#         df_test = _trip_filter(df_test) #filter the data

#         #Dump test sample to file
#         df_test.to_csv(ft)
#         ft.close()
#         tit = tit+1

# def generate_train_data():

#     init()
#     global params
    
#     trainset = itertools.product(params['routes'], params['cluster_sz_train']) 
#     tit = 0
#     for t in trainset:
#         print tit, t, "train_df_"+str(tit)+".csv"

#         ps = gmh.getCoordFromAddress(t[0][0]) 
#         pe = gmh.getCoordFromAddress(t[0][1]) 

#         #Draw train samples
#         print "Draw train cluster: ", t[1]
#         df_train = db_trip.query_Routes(ps, pe, t[1], lonLat=True, date_span = params['train_period'], fareJoin = True) 
#         df_train = ut._trip_filter(df_train) 

#         #Dump train sample to file
#         ft = open(folder + "train_df_"+str(tit)+"_"+str(t[1])+".csv", 'w')
#         df_train.to_csv(ft)
#         ft.close()
#         tit = tit+1


# """
# ############################### TRAIN & TEST DATA PREP ################################
# """


# def generate_train_data_all_routes():
#     init()
#     global params

#     df_train_compr = db_trip.query_Random(params['n_samples_all_routes'], months = params['train_months'], fareJoin = True)
#     fn = "train_df_all_routes_"+str(params['n_samples_all_routes'])+".csv"
#     ft = open(folder + fn, 'w')
#     df_train_compr.to_csv(ft)
#     ft.close()


# def _trip_filter(data, day_hours = range(0,24), weekend = True, workday = True):

#     #Filter
#     d2 = data.copy()
#     if not weekend: #weekends only
#         d2 = data.keep_workdays(data)
        
#     elif not workday: #work days only
#         d2 = data.keep_weekends(data)

#     if day_hours is not None and len(day_hours)>0:
#         d2 = tmanip.keep_daytimes(d2, day_hours)
      
#     #Crude way of removing outliers  
#     d2 = manip.filter_percentile(d2, 'trip_distance', 95,5)
#     return d2

    


# def _infile(fn, line):
#     ff = open(fn, 'r')
#     s = ff.read()
#     ff.close()

#     if s.find(line)>-1:
#         return True
#     else: 
#         return False

