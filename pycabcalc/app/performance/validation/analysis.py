import sys
#sys.path.append("/Users/bubica/insight_link/code/python")
import pandas as pd
import numpy as np
from matplotlib import pyplot as pp


allroutes_fn='res_all_routes.txt'
local_fn='res_selected_route.txt'

names = "id_test,id_train,id_train_str,id_start,id_end,id_cl_test,id_cl_train,id_test_,id_train_,id_sz_test,id_sz_train,model,param1,param2,param3,rmse,r2,fe"
df_all = pd.io.parsers.read_csv(allroutes_fn, sep='|',comment='#',names = names.split(","))
df_local = pd.io.parsers.read_csv(local_fn, sep='|',comment='#',names = names.split(","))

### 1. local vs all

test_ids = list(df_local['id_test'].unique())
train_ids = list(df_local['id_train'].unique())

best_local = [ df_local[df_local['id_test'] == i]['r2'].max() for i in test_ids ]
best_all = [ df_all[df_all['id_test'] == i]['r2'].max() for i in test_ids ]
pp.scatter(best_local, best_all); pp.xlim([-0.5,1]); pp.ylim([-0.5,1]); pp.plot((0, 1), "r--"); pp.title('max(R2_local) vs max(R2_all)'); pp.show()

best_local = [ df_local[df_local['id_test'] == i]['r2'].median() for i in test_ids ]
best_all = [ df_all[df_all['id_test'] == i]['r2'].median() for i in test_ids ]
pp.scatter(best_local, best_all); pp.xlim([-1,1]); pp.ylim([-1,1]); pp.plot((0, 1), "r--"); pp.title('median(R2_local) vs median(R2_all)'); pp.show()

### 2. local vs all, grouped by radius

for tt in list(df_local['id_cl_train'].unique()):
    test_ids = list(df_local[df_local['id_cl_train']==tt]['id_test'].unique())
    train_ids = list(df_local[df_local['id_cl_train']==tt]['id_train'].unique())

    best_local = [ df_local[df_local['id_cl_train']==tt][df_local['id_test'] == i]['r2'].max() for i in test_ids ]
    best_all = [ df_all[df_all['id_test'] == i]['r2'].max() for i in test_ids ]
    pp.scatter(best_local, best_all); pp.xlim([-0.5,1]); pp.ylim([-0.5,1]); pp.plot((0, 1), "r--"); pp.title('Radius=' + str(tt) + ': max(R2_local) vs max(R2_all)'); pp.show()

    best_local = [ df_local[df_local['id_cl_train']==tt][df_local['id_test'] == i]['r2'].median() for i in test_ids ]
    best_all = [ df_all[df_all['id_test'] == i]['r2'].median() for i in test_ids ]
    pp.scatter(best_local, best_all); pp.xlim([-1,1]); pp.ylim([-1,1]); pp.plot((0, 1), "r--"); pp.title('Radius=' + str(tt) + ': median(R2_local) vs median(R2_all)'); pp.show()

### 3. local vs all, grouped by model

for m in list(df_local['model'].unique()):
    test_ids = list(df_local[df_local['model']==m]['id_test'].unique())
    train_ids = list(df_local[df_local['model']==m]['id_train'].unique())

    best_local = [ df_local[df_local['model']==m][df_local['id_test'] == i]['r2'].max() for i in test_ids ]
    best_all = [ df_all[df_all['model']==m][df_all['id_test'] == i]['r2'].max() for i in test_ids ]
    pp.scatter(best_local, best_all); pp.xlim([-0.5,1]); pp.ylim([-0.5,1]); pp.plot((0, 1), "r--"); pp.title('Model=' + str(m) + ': max(R2_local) vs max(R2_all)'); pp.show()

    best_local = [ df_local[df_local['model']==m][df_local['id_test'] == i]['r2'].median() for i in test_ids ]
    best_all = [ df_all[df_all['model']==m][df_all['id_test'] == i]['r2'].median() for i in test_ids ]
    pp.scatter(best_local, best_all); pp.xlim([-1,1]); pp.ylim([-1,1]); pp.plot((0, 1), "r--"); pp.title('Model=' + str(m) + ': median(R2_local) vs median(R2_all)'); pp.show()

####################################################################################################
### 4. pick the best local model

from tabulate import tabulate

train_radii = list(df_local['id_cl_train'].unique())
test_radii = list(df_local['id_cl_test'].unique())

# Step 1: Check R^2 on different train vs test radii

for m in list(df_local['model'].unique()):
    print tabulate([ [ m, train_r, test_r, df_local[df_local['model']==m][df_local['id_cl_train'] == train_r][df_local['id_cl_test'] == test_r]['r2'].max(), df_local[df_local['model']==m][df_local['id_cl_train'] == train_r][df_local['id_cl_test'] == test_r]['r2'].median() ] for train_r in train_radii for test_r in test_radii ], headers=['model','train_radius','test_radius','max(R^2)','median(R^2)'] )
    print ""

# Conclusion: GRAD obviously yields the best performance

# Step 2: Check distribution of GRAD parameters for different routes

start_ids = list(df_local['id_start'].unique())
end_ids = list(df_local['id_end'].unique())

print tabulate([ [ start_id, df_local[df_local['model']=='GRAD'][df_local['id_cl_train'] == 0.3][df_local['id_cl_test'] == 0.3][df_local['id_start'] == start_id]['r2'].max(), df_local[df_local['model']=='GRAD'][df_local['id_cl_train'] == 0.3][df_local['id_cl_test'] == 0.3][df_local['id_start'] == start_id]['r2'].median() ] for start_id in start_ids ], headers=['start_id','max(R^2)','median(R^2)'] )

# Conclusion: max and median are the same for all except one case -- the GRAD model is robust wrt training parameters!

# Step 3: Let's pick the parameters which maximized R^2 for start_ids[0] == '11 Wall street, NY'

df_index_best_model = df_local[df_local['model']=='GRAD'][df_local['id_cl_train'] == 0.3][df_local['id_cl_test'] == 0.3][df_local['id_start'] == start_ids[0]]['r2'].argmax()

# Read parameter settings 

df_local.ix[df_index_best_model]
