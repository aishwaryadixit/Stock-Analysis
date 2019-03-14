import requests
import pandas as pd
import sklearn
from sklearn import svm
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging
import ConfigParser
import os
from datetime import datetime


def get_config(config_file_name):
    # Read config file and return config object
    options = ConfigParser.ConfigParser()
    options.read(config_file_name)
    return options


def main():  # pragma: no cover
    """This function is where execution starts"""

    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf_rel = os.path.join(project_path, 'etc', 'config.ini')
    conf = get_config(conf_rel)
    var_dir = os.path.join(project_path, 'var')
    date = datetime.now().strftime('%Y_%m_%d')
    log_file = os.path.join(var_dir, 'log', 'open_src_logfile' + date)
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG)

    api_key = conf.get('technical', 'api_key')



if __name__ == "__main__":  # pragma: no cover
    main()













r = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&outputsize=full&apikey=LBQ67F59FL7NECLE'
package_json = requests.get(r).json()
dates = list(package_json['Time Series (Daily)'].keys())
l = package_json['Time Series (Daily)']

df = pd.DataFrame(columns=['timestamp',
                           'gap',
                           'high',
                           'low',
                           'volume'])
labels = []
gaps = []
highs = []
lows = []
volumes = []
arr = []
for i in range(len(dates) - 1):
    ts = dates[i]

    gap = float(l[dates[i]]['1. open']) - float(l[dates[i + 1]]['4. close'])
    gaps.append(gap)

    high = float(l[dates[i + 1]]['2. high'])
    highs.append(high)

    low = float(l[dates[i + 1]]['3. low'])
    lows.append(low)

    volume = float(l[dates[i + 1]]['5. volume'])
    volumes.append(volume)
    temp = []
    temp.append(gap)
    temp.append(high)
    temp.append(low)
    temp.append(volume)
    arr.append(temp)

    #df = df.append({'timestamp': ts, 'gap': gap, 'high': high, 'low': low, 'volume': volume}, ignore_index=True)

    if float(l[dates[i]]['1. open']) >= float(l[dates[i]]['4. close']):
        labels.append(0)
    else:
        labels.append(1)
df.set_index('timestamp', inplace=True) # setting timestamp as id

#X = np.array(df.values)
X = np.array(arr)
Y = labels

x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(X, Y, test_size=0.2)

scaler = StandardScaler()
x_train_scaled = scaler.fit(x_train).transform(x_train)
x_test_scaled = scaler.fit(x_test).transform(x_test)

clf = svm.SVC(C=200)
model = clf.fit(x_train_scaled, y_train)
predictions = clf.predict(x_test_scaled)

print(clf.score(x_train_scaled,y_train))
print(clf.score(x_test_scaled,y_test))