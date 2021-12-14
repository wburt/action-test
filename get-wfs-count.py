
import os
import requests
import csv
import pandas as pd
from datetime import datetime, timedelta

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

FEATURES=['WHSE_WATER_MANAGEMENT.WLS_WATER_LICENCED_WRK_LINE_SP','WHSE_WATER_MANAGEMENT.WLS_WATER_LICENCED_WRK_LOC_SP',
'WHSE_WATER_MANAGEMENT.WLS_WATER_RESERVE_LOC_SVW','WHSE_WATER_MANAGEMENT.WLS_WATER_RESTRICTION_LOC_SVW']

def get_wfs_count(feature_name='WHSE_WATER_MANAGEMENT.WLS_WATER_LICENCED_WRK_LINE_SP',url="https://openmaps.gov.bc.ca/geo/pub/ows?"):
    ''' Returns the total feature count for the feature at wfs url'''
    params = {'service':'WFS',
        'version':'2.0.0',
        'request':'GetFeature',
        'typeName':f'pub:{feature_name}',
        'resultType':'hits',
        'outputFormat':'json'}

    r = requests.get(url,params)

    matched = [s for s in r.text.split(' ') if "numberMatched=" in s]
    count = int(matched[0].split('=')[1].replace('"',''))
    return count


def record(feature_name,count,filename='feature-counts.csv'):
    if not os.path.exists(filename):
        with open(filename,'w',newline='') as newfile:
            csv_writer = csv.writer(newfile)
            csv_writer.writerow(['cnt_date','feature','hitcount'])
    with open(filename,'a',newline='') as f:
        csv_writer = csv.writer(f)
        day = datetime.now().strftime('%Y-%m-%d')
        csv_writer.writerow([day,feature_name,count])
    return True

def make_plt(feature_name, input_csv='feature_counts.csv', output='plot.png'):
    df = pd.read_csv(input_csv,parse_dates=['cnt_date'])
    x_min = datetime.now() - timedelta(weeks=12)
    filter = (df['cnt_date']>x_min)
    df = df.loc[filter]
    feat_plot = df.plot(kind='line', x='cnt_date', y='hitcount', grid='True')
    feat_plot.set(xlabel='Date', ylabel='Count',)
    feat_plot.patch.set_facecolor('gainsboro')
    feat_plot.grid(color='white')
    L = feat_plot.legend()
    L.get_texts()[0].set_text(feature_name)
    fig = feat_plot.get_figure()
    fig.savefig(output,bbox_inches='tight')
    fig.clf()   

if __name__=='__main__':
    for feature in FEATURES:
        feature_name = feature.split('.')[-1]
        csv_file = feature_name + '_counts.csv'
        c = get_wfs_count(feature_name=feature)
        r = record(feature_name=feature_name,count=c,filename=csv_file)
        if r is True:
            f = feature_name + '.png'
            make_plt(feature_name=feature_name,input_csv=csv_file,output=f)
