import re

import numpy as np
import pandas as pd
import sklearn
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import logging
import ConfigParser
import os
import pickle
from datetime import datetime
import requests
import prepare_dataset
import scipy
import lxml
import html5lib

def get_config(config_file_name):
    # Read config file and return config object
    options = ConfigParser.ConfigParser()
    options.read(config_file_name)
    return options


def pickle_get(path):
    """This function loads the pickled data
    structure and returns it"""
    logging.info('loading the pickle')
    if os.path.isfile(path):
        return pickle.load(open(path, 'rb'))
    else:
        logging.exception('No pickle found')
        return []


def build_feature_label_set(data_dir):
    features = pickle_get(os.path.join(data_dir, 'useful_f'))
    data_df = pd.DataFrame.from_csv(os.path.join(data_dir, 'key_stats_acc_perf_NO_NA.csv'))

    data_df = data_df.reindex(np.random.permutation(data_df.index))
    # randomizing the data frame so that the trained set is shuffled.

    X = np.array(data_df[features].values)
    y = (data_df["Status"]
         .replace("underperform", 0)
         .replace("outperform", 1)
         .values.tolist())
    return X, y


def fit_algo(data_dir):

    X,y = build_feature_label_set(data_dir)

    x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
                                                                                X,
                                                                                y,
                                                                                test_size=0.2,
                                                                                random_state=33)
    #clf = svm.SVC(kernel="linear", C=1.0)
    clf = MLPClassifier(hidden_layer_sizes=1500, alpha=0.03, max_iter=6000, random_state=42)

    scaler = StandardScaler()
    #scaling the features to increase the accuracy

    x_train_scaled = scaler.fit(x_train).transform(x_train)
    x_test_scaled = scaler.fit(x_test).transform(x_test)

    model = clf.fit(x_train_scaled, y_train)

    print(clf.score(x_train_scaled, y_train))
    print(clf.score(x_test_scaled, y_test))

    return model, clf


def extract(url, ticker, data_dir):
    page = requests.get(url + ticker.upper() + '/key-statistics?p=' + ticker.upper()).text
    gather = pickle_get(os.path.join(data_dir, 'ratios'))
    tables = pd.read_html(page)
    value_list = []

    for each_data in gather:
        value = 'N/A'
        try:
                if each_data == 'Total Debt/Equity':
                    value = tables[5].at[3, 1]
                elif each_data == 'Trailing P/E':
                    value = tables[0].at[2, 1]
                elif each_data == 'Price/Sales':
                    value = tables[0].at[5, 1]
                elif each_data == 'Price/Book':
                    value = tables[0].at[6, 1]
                elif each_data == 'Profit Margin':
                    value = tables[2].at[0, 1]
                elif each_data == 'Operating Margin':
                    value = tables[2].at[1, 1]
                elif each_data == 'Return on Assets':
                    value = tables[3].at[0, 1]
                elif each_data == 'Return on Equity':
                    value = tables[3].at[1, 1]
                elif each_data == 'Revenue Per Share':
                    value = tables[4].at[1, 1]
                elif each_data == 'Market Cap':
                    value = tables[0].at[0, 1]
                elif each_data == 'Enterprise Value':
                    value = tables[0].at[1, 1]
                elif each_data == 'Forward P/E':
                    value = tables[0].at[3, 1]
                elif each_data == 'PEG Ratio':
                    value = tables[0].at[4, 1]
                elif each_data == 'Enterprise Value/Revenue':
                    value = tables[0].at[7, 1]
                elif each_data == 'Enterprise Value/EBITDA':
                    value = tables[0].at[8, 1]
                elif each_data == 'Revenue':
                    value = tables[4].at[0, 1]
                elif each_data == 'Gross Profit':
                    value = tables[4].at[3, 1]
                elif each_data == 'EBITDA':
                    value = tables[0].at[8, 1]
                elif each_data == 'Net Income Avl to Common ':
                    value = tables[4].at[5, 1]
                elif each_data == 'Diluted EPS':
                    value = tables[4].at[3, 1]
                elif each_data == 'Earnings Growth':
                    value = tables[4].at[7, 1]
                elif each_data == 'Revenue Growth':
                    value = tables[4].at[2, 1]
                elif each_data == 'Total Cash':
                    value = tables[5].at[0, 1]
                elif each_data == 'Total Cash Per Share':
                    value = tables[5].at[1, 1]
                elif each_data == 'Total Debt':
                    value = tables[5].at[2, 1]
                elif each_data == 'Current Ratio':
                    value = tables[5].at[4, 1]
                elif each_data == 'Book Value Per Share':
                    value = tables[5].at[5, 1]
                elif each_data == 'Cash Flow':
                    value = tables[6].at[0, 1]
                elif each_data == 'Beta':
                    value = tables[7].at[0, 1]
                elif each_data == 'Held by Insiders':
                    value = tables[8].at[4, 1]
                elif each_data == 'Held by Institutions':
                    value = tables[8].at[5, 1]
                elif each_data == 'Shares Short (as of':
                    value = tables[8].at[6, 1]
                elif each_data == 'Short Ratio':
                    value = tables[8].at[7, 1]
                elif each_data == 'Short % of Float':
                    value = tables[8].at[8, 1]
                elif each_data == 'Shares Short (prior ':
                    value = tables[8].at[9, 1]

                if "B" in value:
                    value = float(value.replace("B", '')) * 1000000000

                elif "M" in value:
                    value = float(value.replace("M", '')) * 1000000

                elif "%" in value:
                    value = float(value.replace("%", ''))

                value_list.append(value)

        except Exception as e:
            value = "N/A"
            value_list.append(value)

    return value_list


def predict(url, ticker, data_dir):
    value_list = extract(url, ticker, data_dir)
    df = pd.DataFrame(columns=pickle_get(os.path.join(data_dir, 'useful_f')))
    df = df.append({
                    'DE Ratio': value_list[0],
                    'Trailing P/E': value_list[1],
                    'Price/Sales': value_list[2],
                    'Price/Book': value_list[3],
                    'Profit Margin': value_list[4],
                    'Operating Margin': value_list[5],
                    'Return on Assets': value_list[6],
                    'Return on Equity': value_list[7],
                    'Revenue Per Share': value_list[8],
                    'Market Cap': value_list[9],
                    'Enterprise Value': value_list[10],
                    'Forward P/E': value_list[11],
                    'PEG Ratio': value_list[12],
                    'Enterprise Value/Revenue': value_list[13],
                    'Enterprise Value/EBITDA': value_list[14],
                    'Revenue': value_list[15],
                    'Gross Profit': value_list[16],
                    'EBITDA': value_list[17],
                    'Net Income Avl to Common ': value_list[18],
                    'Diluted EPS': value_list[19],
                    'Earnings Growth': value_list[20],
                    'Revenue Growth': value_list[21],
                    'Total Cash': value_list[22],
                    'Total Cash Per Share': value_list[23],
                    'Total Debt': value_list[24],
                    'Current Ratio': value_list[25],
                    'Book Value Per Share': value_list[26],
                    'Cash Flow': value_list[27],
                    'Beta': value_list[28],
                    'Held by Insiders': value_list[29],
                    'Held by Institutions': value_list[30],
                    'Shares Short (as of': value_list[31],
                    'Short Ratio': value_list[32],
                    'Short % of Float': value_list[33],
                    'Shares Short (prior ': value_list[34],
                    },
                   ignore_index=True)
    X = np.array(df.values)
    model, clf = fit_algo(data_dir)
    print(clf.classes_)
    print(model.predict(X))
    print(model.predict_proba(X))


def main():  # pragma: no cover
    """This function is where execution starts"""

    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf_rel = os.path.join(project_path, 'etc', 'config.ini')
    conf = get_config(conf_rel)
    var_dir = os.path.join(project_path, 'var')
    data_dir = os.path.join(var_dir, 'data')
    url =conf.get('fundamental', 'url')

    date = datetime.now().strftime('%Y_%m_%d')
    log_file = os.path.join(var_dir, 'log', 'fundamental_analysis' + date)
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG)
    predict(url, 'AAPL', data_dir)


if __name__ == "__main__":  # pragma: no cover
    main()

#24 94 44 73
#nn 42