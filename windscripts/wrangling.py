import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from collections import Counter
from scipy.special import psi
import io

def get_train_set(filename):
    """Filename or StringIO object is the full path pointing to the properly 
    formatted wind time series
    """
    #Read the wind time series and interpret the columns correctly
    windseries = pd.DataFrame.from_csv(filename,infer_datetime_format=True)
    assert len(windseries.columns) > 0
    #windseries = windseries.set_index(windseries.columns[0])
    #windseries.index = pd.to_datetime(windseries.index)
    
    #Prepare data set to be digestable by the training function
    windColumn = windseries.columns[0]
    windseries['hour'] = windseries.index.hour
    windseries['month'] = windseries.index.month
    windseries[[windColumn]] = np.round(windseries[[windColumn]])
    return windseries, windColumn

def plot_seasonality(windseries):
    pd.set_option('display.mpl_style', 'default')
    plt.rcParams['figure.figsize'] = (16, 10)
    
    windData = windseries.copy()
    if 'month' not in windData.keys(): windData = windData.index.month
    if 'hour' not in windData.keys(): windData['hour'] = windData.index.hour
    
    windmap = windData.groupby(['month','hour']).aggregate(np.mean).unstack(level=0)
    windmap = np.round(windmap*10)/10
    z = []
    for index, x in np.ndenumerate(windmap.as_matrix()):
        z.append([index[1],index[0],x])
    return z
    