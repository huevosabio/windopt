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
    
    windmap = windData.groupby(['month','hour']).aggregate(np.median).unstack(level=0)
    fig, ax = plt.subplots()
    im = ax.imshow(windmap.fillna(0), extent=(1, 12, 0, 23),origin='lower',aspect='auto')
    v = np.linspace(windmap.min().min(), windmap.max().max(), 15, endpoint=True)
    font = {'size'   : 16}
    fig.colorbar(im, ax=ax).set_label('Median Wind Speed in m/s',**font)
    plt.xlabel('Month of the Year',**font)
    plt.ylabel('Hour of the Day',**font)
    ax.set_title('Seasonality of Wind', size=20)
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf
    
def train_mcm_hm(trainData,windcolumn):
    """Training function for a binned dataset
    assumes the dataset is properly formatted:
    index: datetiem
    windcolumn: wind speeds column
    hour: hour of the day column
    month: month of the year column"""
    #First, let's find our alphas (required for bayesian approach)
    count_tmat = np.zeros((trainData[windcolumn].max()+1,trainData[windcolumn].max()+1))
    for (x,y), c in Counter(zip(trainData[windcolumn][1:], trainData[windcolumn])).iteritems():
        if np.isnan((x,y)).any(): continue
        count_tmat[x,y] = c
    alphas = np.ones(len(count_tmat))
    def new_alpha(tmatrix,current_alpha):
        #get the numerator
        num = psi(tmatrix+current_alpha) - psi(current_alpha)
        num = num.sum(axis=0)
        den = psi(tmatrix.sum(axis=1)+current_alpha.sum())-psi(current_alpha.sum())
        den = den.sum()
        f = num/den
        result = np.multiply(current_alpha,f)
        return result
    tolerance = 0.0001
    diff = 1000
    while diff > tolerance:
        alphas_0 = new_alpha(count_tmat,alphas)
        diff = np.abs((alphas_0-alphas).sum())
        alphas = alphas_0
    
    #Now, let's get the full set of transition matrices
    count_tmat_hm = np.zeros((12,24,trainData[windcolumn].max()+1,trainData[windcolumn].max()+1))
    for (m,h,x,y), c in Counter(zip(trainData['month']-1,trainData['hour'],trainData[windcolumn][1:], trainData[windcolumn])).iteritems():
        if np.isnan((m,h,x,y)).any(): continue
        count_tmat_hm[m,h,x,y] = c
    bayes_tmat_hm = count_tmat_hm + alphas
    for i in range(len(bayes_tmat_hm)):
        for j in range(len(bayes_tmat_hm[i])):
            bayes_tmat_hm[i][j] = np.divide(bayes_tmat_hm[i][j],bayes_tmat_hm[i][j].sum(axis=0)).transpose()
    
    return bayes_tmat_hm


