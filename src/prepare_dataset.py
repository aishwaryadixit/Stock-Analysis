import ConfigParser
from datetime import datetime
import logging
import os
import pickle
import time
import re
import pandas as pd
import prepare_ratios


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


def generate_data_frame(data_dir, stats_path, gather=None):
    global stock_1y_value, sp500_1y_value

    if gather is None:
        gather = pickle_get(os.path.join(data_dir, 'ratios'))

    stock_dir_list = [x[0] for x in os.walk(stats_path)]
    df = pd.DataFrame(columns=pickle_get(os.path.join(data_dir, 'features')))

    sp500_df = pd.DataFrame.from_csv(os.path.join(data_dir, 'GSPC.csv'))
    stock_df = pd.DataFrame.from_csv(os.path.join(data_dir, 'stock_prices.csv'))

    ticker_list = []

    for each_dir in stock_dir_list[1:]:
        each_file = os.listdir(each_dir)
        ticker = each_dir.split("\\")[9]
        ticker_list.append(ticker)

        if len(each_file) > 0:
            for f in each_file:
                date_stamp = datetime.strptime(f, '%Y%m%d%H%M%S.html')
                unix_time = time.mktime(date_stamp.timetuple())
                full_file_path = each_dir + '\\' + f
                source = open(full_file_path, 'r').read()
                try:
                    value_list = []

                    for each_data in gather:
                        try:
                            import pdb;pdb.set_trace()
                            regex = re.escape(each_data) + r'.*?(\d{1,8}\.\d{1,8}M?B?|N/A)%?'
                            value = re.search(regex, source)
                            value = (value.group(1))

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
                    try:
                        sp500_date = datetime.fromtimestamp(unix_time).strftime(
                            '%Y-%m-%d')

                        row = sp500_df[(sp500_df.index == sp500_date)]
                        if row is not None and not row.empty:
                            sp500_value = float(row["Adj Close"])
                    except Exception as e:
                        try:

                            sp500_date = datetime.fromtimestamp(unix_time - 259200).strftime(
                                '%Y-%m-%d')
                            # subtracting the weekend as sp500 is not available for weekends

                            row = sp500_df[(sp500_df.index == sp500_date)]
                            if row is not None and not row.empty:
                                sp500_value = float(row["Adj Close"])

                        except Exception as e:
                            logging.exception("Some error occurred (custom)" + str(e))

                    one_year_later = int(unix_time + 31536000)

                    try:
                        sp500_1y = datetime.fromtimestamp(one_year_later).strftime('%Y-%m-%d')

                        row = sp500_df[(sp500_df.index == sp500_1y)]
                        if row is not None and not row.empty:
                            sp500_1y_value = float(row["Adj Close"])

                    except Exception as e:
                        try:
                            sp500_1y = datetime.fromtimestamp(one_year_later - 259200).strftime(
                                '%Y-%m-%d')

                            row = sp500_df[(sp500_df.index == sp500_1y)]
                            if row is not None and not row.empty:
                                sp500_1y_value = float(row["Adj Close"])

                        except Exception as e:
                            logging.exception("sp500 1 year later issue" + str(e))

                    try:
                        stock_date_1_yr = datetime.fromtimestamp(one_year_later).strftime('%Y-%m-%d')
                        row = stock_df[(stock_df.index == stock_date_1_yr)][ticker.upper()]
                        if row is not None and not row.empty:
                            stock_1y_value = round(float(row), 2)

                    except Exception as e:  # STOCK PRICE VALUE AFTER A YEAR FROM NOW (UNIX TIME)
                        try:
                            stock_date_1_yr = datetime.fromtimestamp(one_year_later - 259200).strftime(
                                '%Y-%m-%d')
                            # subtracting the weekend as sp500 is not available for weekends

                            if ticker.upper in stock_df[(stock_df.index == stock_date_1_yr)].columns.values.tolist():
                                row = stock_df[(stock_df.index == stock_date_1_yr)][ticker.upper()]
                                if row is not None and not row.empty:
                                    stock_1y_value = round(float(row), 2)

                        except Exception as e:
                            import pdb;pdb.set_trace()
                            logging.exception("stock price 1 year later:" + str(e))

                    try:

                        stock_date = datetime.fromtimestamp(unix_time).strftime(
                            '%Y-%m-%d')
                        # NOW USING THE CURRENT VALUE

                        row = stock_df[(stock_df.index == stock_date)][ticker.upper()]
                        if row is not None and not row.empty:
                            stock_value = round(float(row), 2)

                    except Exception as e:
                        try:
                            stock_date = datetime.fromtimestamp(unix_time - 259200).strftime('%Y-%m-%d')

                            if ticker.upper in stock_df[(stock_df.index == stock_date)].columns.values.tolist():
                                row = stock_df[(stock_df.index == stock_date)][ticker.upper()]
                                if row is not None and not row.empty:
                                    stock_value = round(float(row), 2)
                        except Exception as e:
                            logging.exception("stock price:" + str(e))

                    stock_p_change = round((((stock_1y_value - stock_value) / stock_value) * 100), 2)
                    sp500_p_change = round((((sp500_1y_value - sp500_value) / sp500_value) * 100), 2)
                    # (NEW - OLD)/ OLD AND THEN ROUNDING TO TWO DECIMAL PLACES TO REDUCE THE DATA.

                    difference = stock_p_change - sp500_p_change

                    if difference > 0:
                        status = "outperform"
                    else:
                        status = "underperform"

                    if value_list.count("N/A") > 0:
                        pass
                    else:
                        df = df.append({'Date': date_stamp,
                                        'Unix': unix_time,
                                        'Ticker': ticker,
                                        'Price': stock_value,
                                        'stock_p_change': stock_p_change,
                                        'SP500': sp500_value,
                                        'sp500_p_change': sp500_p_change,
                                        'Difference': difference,
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
                                        'Status': status},
                                       ignore_index=True)
                except Exception as e:
                    pass
    df.to_csv(os.path.join(data_dir, 'key_stats_acc_perf_NO_NA.csv'))
    # We are not allowing any column to contain 'not available'


def main():  # pragma: no cover
    """This function is where execution starts"""

    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    var_dir = os.path.join(project_path, 'var')
    data_dir = os.path.join(var_dir, 'data')
    stats_path = os.path.join(data_dir, 'intraQuarter', '_KeyStats')

    date = datetime.now().strftime('%Y_%m_%d')
    log_file = os.path.join(var_dir, 'log', 'prepare_dataset_log_file' + date)
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG)

    prepare_ratios.main()
    generate_data_frame(data_dir, stats_path)
    print('made dataset')


if __name__ == "__main__":  # pragma: no cover
    main()
