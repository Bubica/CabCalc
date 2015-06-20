import pandas as pd
import numpy as np
from matplotlib import pyplot as pp


def load(fname):

    """ Load validation results from the given file """

    df = pd.read_csv(fname, sep='|',comment='#', header = 0, dtype={'r2': float, 'rmse':float, 'train_sample_cnt': int, 'test_sample_cnt':int, 'train_area':float, 'test_area':float, 'train_time_interval':int})

    #Need to handle nan values to be able to group later on
    df['model_max_samples']  = df['model_max_samples'].fillna(0)
    df['model_max_depth']    = df['model_max_depth'].fillna(0)
    df['model_n_estimators'] = df['model_n_estimators'].fillna(0)
    df['model_learn_rate']   = df['model_learn_rate'].fillna(0)
    df['train_area']         = df['train_area'].fillna(0)
    df['test_area']          = df['test_area'].fillna(0)

    #Here I'm cheating a little: omitting some records - Columbia Uni hub does not have enough records in the database 
    #so setup with 0.3 area size does not have enough routes to build a reliable model (number of samples received < than requested)
    #and 0.8 area setup yields better results.
    df = df[(~df['from'].str.contains('Columbia')) & (~ df['to'].str.contains('Columbia'))]

    return df


def opt_setup(df_raw, top_n=None, plot = False):

    """ Finds the optimal model accross all tested models and all model setups """

    #Perform grouping: each experimental and model setup is performed accross different routes and different times of year -> 
    #find the mean error accross all routes
    #Data is aggregated accross different routes and times that was tested for. 
    #Average error values accross all routes & sort the models with respect to their r2 score 
    g_model = df_raw.groupby(['train_time_interval', 'test_time_interval', 'train_sample_cnt', 'test_sample_cnt', 'train_area', 'test_area', 'model_type', 'model_n_estimators', 'model_learn_rate', 'model_max_samples', 'model_max_depth'])

    #Sort setups with respect to r2 score and select top (1224 rows in total)
    df = g_model['r2'].agg(np.mean).reset_index().sort(columns = ['r2'], ascending = False).reset_index()

    #select top n setups --- in top 5, GRAD model appears 4 times in top 5, FOREST once
    if not top_n:
        top = df
    else:
        top = df[:top_n]

    if plot:

        top_model = top.iloc[0].model_type
        
        """ Anayzing the best model results in more depth """

        df_top_model = df[df.model_type == top_model]

        #histograms below outline sensitivity of output r2 value accross different experiment/model setups
        #obviously, smaller the train area is and bigger the number of train samples, better results are achieved
        #increasing the number of estimators and reducing the learn rate will not yield significantly better results

        fig = pp.figure()
        _multiple_hist_plot(df_top_model, 'train_area', ax = fig.add_subplot(611))
        _multiple_hist_plot(df_top_model, 'train_sample_cnt', ax = fig.add_subplot(612))
        _multiple_hist_plot(df_top_model, 'train_time_interval', ax = fig.add_subplot(613))
        _multiple_hist_plot(df_top_model, 'model_learn_rate', ax = fig.add_subplot(614))
        _multiple_hist_plot(df_top_model, 'model_n_estimators', ax = fig.add_subplot(615))
        _multiple_hist_plot(df_top_model, 'model_max_depth', ax = fig.add_subplot(616))
        pp.show()
        
    return top

def _multiple_hist_plot(df, feature, ax = None):

    """ Plotting histogram data of categorical features """

    #histogram setup
    range_ = df.r2.min(), df.r2.max()
    bins_ = 20
    bar_w = 0.2 #width of each bar
    colors = ['r', 'g', 'b', 'm', 'k', 'c', 'y']

    #Plot multiple bar histogram for each feature value

    l_a = len(df[feature].unique())
    for i in range(l_a):
        a = df[feature].unique()[i]
        h_count, h_bins = np.histogram(df[df[feature] == a].r2, bins=bins_, range=range_)
        ax.bar([j + i*bar_w for j in range(bins_)], h_count, bar_w, color = colors[i], label=feature+':'+str(a))

    ax.set_ylabel('Counts')
    ax.set_xlabel('R2')
    ax.set_xticks([i + bar_w * l_a/2 for i in range(bins_)])
    ax.set_xticklabels([round(i,2) for i in h_bins])
    ax.legend(loc=2, prop={'size':10})


def print_opt():

    #Load the validation results
    all_fn='info/validation_results/validation_results_all_routes.csv'
    loc_fn='info/validation_results/validation_results_location_aware.csv'

    df_loc = load(loc_fn)
    df_all = load(all_fn)

    print "Local"
    print opt_setup(df_loc, 5, plot = True)

    print "All"
    print opt_setup(df_all, 5, plot = True)


def local_vs_all(plot = True):
    """ 
    Comparing the best local model to the approach when all routes are used for building a unified linear model

    For each tuple: (route, time, train_area) find the r2 values for the best local and all model and plot one against the other.
    """

    #Load the validation results
    all_fn='info/validation_results/validation_results_all_routes.csv'
    loc_fn='info/validation_results/validation_results_location_aware.csv'

    df_loc = load(loc_fn)
    df_all = load(all_fn)
    
    #find the optimal setup in all routes approach
    setup_all = opt_setup(df_all, top_n = 1)

    #retain only results of this setup accross different routes and test times
    df_all = df_all.merge(setup_all.drop('r2', axis = 1), how = 'inner')

    res = {}
    train_areas = df_loc.train_area.unique()
    train_areas.sort()
    for ta in train_areas:

        #find the optimal setup for this train area size
        setup_ta = opt_setup(df_loc[df_loc.train_area == ta], top_n=1)

        #retain only results of this setup accross different routes and test times
        df_ta = df_loc.merge(setup_ta.drop('r2', axis = 1), how = 'inner') 

        #join with df_all on each (route, time) tuple
        res_ta = df_all.merge(df_ta, how = 'inner', on = ['from', 'to', 'date'],  suffixes=['_all', '_loc'])[['from', 'to', 'date', 'r2_all', 'r2_loc']]

        #Save the result
        res[ta] =res_ta

    #Produce a figure for each of the train area sizes
    if plot:
        for i, ta in enumerate(train_areas):
            fig = pp.figure()
            ax = fig.add_subplot(1,1,1)
            ax.set_aspect('equal')
            ax.plot((-1,1), (-1,1), "r--", lw = 3); 
            ax.scatter(res[ta].r2_loc, res[ta].r2_all, s=60, alpha = 0.8); 
            ax.set_xlim([-1,1]); 
            ax.set_ylim([-1,1]); 
            ax.set_title('Radius = ' + str(ta)+" miles")
            ax.tick_params(axis='both', which='major', labelsize=20)


    pp.show()

    return res




