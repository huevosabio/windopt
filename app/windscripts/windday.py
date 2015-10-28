import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import scipy.stats as stats
from statsmodels.tsa import stattools
from statsmodels.tools import eval_measures
import statsmodels.graphics.tsaplots as tsaplots
from collections import Counter
from scipy.special import psi
import itertools

def compute_stationary(transmat):
    """Estimatres the stationary (long-term) distribution of
    the wind speed"""
    tolerance = 0.00001
    diff = 1000
    dist = np.eye(*transmat[0][0].shape)
    while diff > tolerance:
        oldDist = dist.copy()
        for month in range(12):
            for hour in range(24):
                dist = np.dot(dist,transmat[month][hour])
        diff = np.abs(oldDist-dist).sum()
    return dist

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
        
    #Smooth the alphas, just in case of NaN
    zeroed = np.nan_to_num(alphas)
    alphas = (zeroed + 1/zeroed.sum())/zeroed.sum()
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


def estimate_windday(starthour,daylength,month,tmatrix,maxhours,maxSpeed,stationary=None,consecutive=True):
    """Estimates the probability of a wind day for a given month"""
    maxSpeed = np.round(maxSpeed)
    
    if maxSpeed >len(tmatrix[0][0]): return 0.0
    
    assert maxSpeed <= len(tmatrix[0][0]) and maxSpeed >= 0
    
    assert maxhours > 0
    
    if not stationary:
        stationary = compute_stationary(tmatrix)
        
    #Estimate the stationary distribution at the start of the day
    startStat = stationary.copy()
    for mes in range(month):
        for day in range(30):
            for hour in range(24):
                startStat = np.dot(startStat,tmatrix[mes][hour])
    for hour in range(starthour):
        startStat = np.dot(startStat,tmatrix[month][hour])
    
    #Now we have a stationary distribution, we need to get matrix probabilities at each hour
    startDist = stats.rv_discrete(name='Starting Distribution',values=(range(len(startStat)),startStat[0]))
    
    #The first hour is based solely on the stationary distribution
    if consecutive: k = 0
    else: k = 1
    W = np.zeros((maxhours+1, maxhours+1))
    for i in range(maxhours):
        W[i, i*k] = startDist.cdf(maxSpeed)
        W[i, i + 1] = 1-startDist.cdf(maxSpeed)
    W[maxhours, maxhours] = 1.0
    #Update startStat
    startStat = np.dot(startStat,tmatrix[month][starthour])
    
    #TODO: This Part may need further mathematical check, but should be mostly correct
    for hour in range(starthour+1,starthour+daylength):
        hour = hour%24
        W0 = np.zeros((maxhours+1,maxhours+1))
        
        #Now, we give weights to our transition matrix based on startStat
        weighted = np.multiply(tmatrix[month][hour].transpose(),startStat[0]).transpose()
        #weighted = tmat[month][hour]
        
        #Get the probabilities given that it is BELOW maxspeed
        wbelow = weighted[:maxSpeed,:].sum()
        pbelow_below = (weighted[:maxSpeed,:maxSpeed]/wbelow).sum()
        pabove_below = (weighted[:maxSpeed,maxSpeed:]/wbelow).sum()
        #Get the probabilities given that it is ABOVE maxspeed
        wabove = weighted[maxSpeed:,:].sum()
        pbelow_above = (weighted[maxSpeed:,:maxSpeed]/wabove).sum()
        pabove_above = (weighted[maxSpeed:,maxSpeed:]/wabove).sum()
        
        #Estimate the state transitions
        W0[0,0] = pbelow_below
        W0[0,1] = pabove_below
        for i in range(1,maxhours):
            W0[i,i*k] = pbelow_above
            W0[i,i+1] = pabove_above
        W0[maxhours,maxhours] = 1.0
        
        #Update W
        W = np.dot(W,W0)
        
        #Update startStat
        startStat = np.dot(startStat,tmatrix[month][hour])
    
    return W[0,maxhours]
    
def transform_height(originalHeight,targetHeight,windspeed,a=0.143):
    targetSpeed = windspeed*(float(originalHeight)/targetHeight)**a
    return targetSpeed

def estimate_winddays(measureHeight,height,maxws,maxhours,starthour,daylength,tmatrix,certainty,consecutive=True):
    #TODO: Improve this such that it is based on the projects actual timeline
    #TODO: Improve this with actual workdays per month
    maxws = transform_height(measureHeight,height,maxws)
    monthlyLoss = []
    cumulative = []
    for month in range(12):
        p = estimate_windday(starthour,daylength,month,tmatrix,maxhours,maxws,consecutive=consecutive)
        monthlyLoss.append(float(stats.binom.ppf([certainty],25,p)))
        cumulative.append(float(np.array(monthlyLoss).sum()))
    return monthlyLoss,cumulative

def risk_by_hour_and_month(measureHeight,height,maxws,maxhours,daylength,tmatrix,consecutive=True):
    maxws = transform_height(measureHeight,height,maxws)
    combinations = list(itertools.product(range(12),range(24)))
    def windday_byHnM(hourNMonth):
        hour = hourNMonth[1]
        month = hourNMonth[0]
        return [month,hour, round(estimate_windday(hour,daylength,month,tmatrix,maxhours,maxws,consecutive=consecutive)*100)/100]
    risks = map(windday_byHnM,combinations)
    return risks