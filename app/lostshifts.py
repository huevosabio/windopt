import os
from flask import Flask, request, redirect, url_for, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from app import app
import scipy.stats as stats
from flask_wtf.csrf import CsrfProtect
from app.dbmodel import *

#csrf = CsrfProtect(app)

def windDayProb(shift,dayLength,maxSpeed,param):
    #Shift denotes the minimum number of consecutive hours required to work
    #daylength is the number of available hours in the day.
    #maxSpeed is the maximum tolerable windspeed
    W = np.zeros((shift+1, shift+1))
    for i in range(shift):
        W[i, 0] = stats.exponweib.cdf(maxSpeed, *param)
        W[i, i + 1] = 1-stats.exponweib.cdf(maxSpeed, *param)
    W[shift, shift] = 1.0
    return np.linalg.matrix_power(W,dayLength)[0,shift]

#@csrf.exempt
@app.route('/lostShifts',methods=['POST'])
@auth.login_required
def lostShifts():
    #Probability of a Wind Day
    wdprob = windDayProb(request.json['consecutive'],request.json['workWindow'],request.json['maxWS'],request.json['params'])
    
    #Plot set up
    pd.set_option('display.mpl_style', 'default') # Make the graphs a bit prettier
    plt.rcParams['figure.figsize'] = (15, 5)
    ppf = plt.figure()
    #Plotting
    x = np.linspace(0.01,0.99,1000)
    z = stats.binom.ppf(x,request.json['projectLength'],wdprob)
    plt.plot(x,z)
    plt.savefig(os.path.join(app.config['STATIC'], 'lostshifts.png'))
    ploturl = 'static/lostshifts.png'
    #layout={'margin':{'l':40,'r':0,'t':0,'b':40},'xaxis':{'mirror':'false'},'yaxis':{'mirror':'false'}}
    #ploturl = py.plot_mpl(ppf,auto_open=False, filename='shiftLostDistr',update={'layout':layout})
    
    return jsonify({'ploturl': ploturl})
