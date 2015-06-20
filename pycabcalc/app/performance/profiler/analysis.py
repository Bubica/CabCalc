import pandas as pandas
import numpy as np
from matplotlib import pyplot as pp

res_fn = 'info/profiler_results/full_db_forced.csv'

""" Load data """
df = pd.read_csv(res_fn, sep='|', comment='#', header = 0, dtype={'Area_size': float, 'Max_samples': int, 'Duration(s)':float, 'Number_of_records':int})


"""
Evaluate average fetch time as function of number of requested samples (with LIMIT n option in sql command)

Max_samples
1000           0.896599
5000           3.643657
10000          6.651186
Name: Duration(s), dtype: float64

"""
df.groupby(['Max_samples'])['Duration(s)'].agg(np.median)


"""
Display dependency of fetch duration against the returned number of samples (regardless of the requested number of samples).
Bin the number of returned samples.
"""
bins = np.linspace(df.Number_of_records.min(), df.Number_of_records.max()+1, 40)
bin_sz = bins[1]-bins[0]
df['Number_of_records_bin'] = np.digitize(df.Number_of_records, bins = bins) #Return the indices of the bins to which each value in input array belongs.
median_dur = df.groupby('Number_of_records_bin')['Duration(s)'].agg(np.median)

pp.plot([bins[i]-bin_sz for i in median_dur.index], median_dur, 'o')
pp.xlabel("Number of retrieved records")
pp.ylabel("Median duration(s)")
pp.show()


"""
Check if the size of the area influences retrieveal time.

Area_size
0.3          3.196758
0.8          3.742507
1.5          3.453917
Name: Duration(s), dtype: float64
"""
df.groupby('Area_size')['Duration(s)'].agg(np.median)
