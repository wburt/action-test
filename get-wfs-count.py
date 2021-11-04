
import os
import requests
import csv
import pandas as pd
import seaborn
from datetime import date, datetime

FEATURES=['WHSE_WATER_MANAGEMENT.WLS_WATER_LICENCED_WRK_LINE_SP','WHSE_WATER_MANAGEMENT.WLS_WATER_LICENCED_WRK_LOC_SP']

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

def make_plt(feature_name,input_csv='feature-counts.csv', output='plot.png'):
    df = pd.read_csv(input_csv)
    feat_plt = seaborn.lineplot(x='cnt_date',y='hitcount',data=df,hue='feature')
    fig = feat_plt.get_figure()
    fig.savefig(output)
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