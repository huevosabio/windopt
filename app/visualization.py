import os
from flask import Flask, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
from app import app

@app.route('/visualize')
def visualize():
    pd.set_option('display.mpl_style', 'default') # Make the graphs a bit prettier
    plt.rcParams['figure.figsize'] = (15, 5)
    windData = pd.read_csv('tmp/winddata.csv', parse_dates=['Date_time'], index_col='Date_time')
    windData['w_80'].plot()
    plt.savefig(os.path.join(app.config['STATIC'], 'historical.png'))
    return '<img src=' + url_for('static',filename='historical.png') + '>'