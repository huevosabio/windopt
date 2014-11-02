import os
from flask import Flask, request, redirect, url_for, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from app import app
import scipy.stats as stats
import plotly.plotly as py
from app.auth import *

def df_to_iplot(df):
    
    '''
    Coverting a Pandas Data Frame to Plotly interface
    '''
    x = df.index.values
    lines={}
    for key in df:
        lines[key]={}
        lines[key]["x"]=x
        lines[key]["y"]=df[key].values
        lines[key]["name"]=key

        #Appending all lines
    lines_plotly=[lines[key] for key in df]
    return lines_plotly

@app.route('/visualize')
@auth.login_required
def visualize():
    pd.set_option('display.mpl_style', 'default') # Make the graphs a bit prettier
    plt.rcParams['figure.figsize'] = (15, 5)
    plots = []
    
    ploturls = {}
    layout={'margin':{'l':40,'r':0,'t':0,'b':40},'xaxis':{'mirror':'false'},'yaxis':{'mirror':'false'}}
    
    windData = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], 'winddata.csv'), parse_dates=True, index_col=0)
    ws = list(windData.columns.values)[0]
    #historical = windData[[ws]]
    #plots.append([historical,'historical'])
    
    cleanData = np.array(windData[np.isfinite(windData[ws])][ws])
    parameters = stats.exponweib.fit(cleanData, loc=0)
    weibull= plt.figure()
    x = np.linspace(cleanData.min(), cleanData.max(), 1000)
    plt.plot(x, stats.exponweib.pdf(x, *parameters))
    _ = plt.hist(cleanData, bins=np.linspace(0, 20, 40), normed=True, alpha=0.5)
    plt.savefig(os.path.join(app.config['STATIC'], 'weibull.png'))
    #ploturls['weibull'] = py.plot_mpl(weibull,auto_open=False, filename='weibull',update={'layout':layout})
    ploturls['weibull'] = 'static/weibull.png'
    plt.close()
    
    byMonth = windData[[ws]]
    byMonth['month'] = byMonth.index.month
    byMonth = byMonth.groupby('month').aggregate(np.median)
    plots.append([byMonth,'byMonth'])
    
    byHour = windData[[ws]]
    byHour['hour'] = byHour.index.hour
    byHour = byHour.groupby('hour').aggregate(np.median)
    plots.append([byHour,'byHour'])
    
    windData['hour'] = windData.index.hour
    windData['week'] = windData.index.week
    windmap = windData.groupby(['week','hour']).aggregate(np.median).unstack(level=0)
    fig, ax = plt.subplots()
    im = ax.imshow(windmap.fillna(0), extent=(0, 53, 0, 24),origin='lower',aspect='auto')
    v = np.linspace(windmap.min().min(), windmap.max().max(), 15, endpoint=True)
    font = {'size'   : 16}
    fig.colorbar(im, ax=ax).set_label('Median Wind Speed in m/s',**font)
    plt.xlabel('Week of the Year',**font)
    plt.ylabel('Hour of Day',**font)
    ax.set_title('Seasonality of Wind', size=20)
    plt.savefig(os.path.join(app.config['STATIC'], 'historical.png'))
    ploturls['historical'] = 'static/historical.png'
     
    
    for each in plots:
        ax = each[0].plot()
        fig = ax.get_figure()
        fig.savefig(os.path.join(app.config['STATIC'], each[1]+'.png'))
        ploturls[each[1]] = 'static/'+each[1]+'.png'
        #ploturls.append(py.plot_mpl(fig,filename=each[1], auto_open=False))
        #ploturls[each[1]]=py.plot(df_to_iplot(each[0]),filename=each[1],auto_open=False, connectgaps=False,update={'layout':layout})
        plt.close()
    
    response = {}
    response['images'] = ploturls
    response['parameters'] = []
    for param in parameters:
        response['parameters'].append(param)
    
    return jsonify(response)