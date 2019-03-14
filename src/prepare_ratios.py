import ConfigParser
import logging
import pickle
import os
from datetime import datetime


def pickle_set(data_set, path):
    """This function pickles the data structure passed into
    it as a parameter"""
    logging.info('pickling the data structure')
    pickle_out = open(path, 'wb')
    pickle.dump(data_set, pickle_out)
    pickle_out.close()


def get_config(config_file_name):
    # Read config file and return config object
    options = ConfigParser.ConfigParser()
    options.read(config_file_name)
    return options


def main():
    """This function is where execution starts"""

    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    var_dir = os.path.join(project_path, 'var')
    data_dir = os.path.join(var_dir, 'data')

    date = datetime.now().strftime('%Y_%m_%d')
    log_file = os.path.join(var_dir, 'log', 'prepare_ratios' + date)
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG)

    gather = ["Total Debt/Equity",
              'Trailing P/E',
              'Price/Sales',
              'Price/Book',
              'Profit Margin',
              'Operating Margin',
              'Return on Assets',
              'Return on Equity',
              'Revenue Per Share',
              'Market Cap',
              'Enterprise Value',
              'Forward P/E',
              'PEG Ratio',
              'Enterprise Value/Revenue',
              'Enterprise Value/EBITDA',
              'Revenue',
              'Gross Profit',
              'EBITDA',
              'Net Income Avl to Common ',
              'Diluted EPS',
              'Earnings Growth',
              'Revenue Growth',
              'Total Cash',
              'Total Cash Per Share',
              'Total Debt',
              'Current Ratio',
              'Book Value Per Share',
              'Cash Flow',
              'Beta',
              'Held by Insiders',
              'Held by Institutions',
              'Shares Short (as of',
              'Short Ratio',
              'Short % of Float',
              'Shares Short (prior ']

    features = ['Date',
                'Unix',
                'Ticker',
                'Price',
                'stock_p_change',
                'SP500',
                'sp500_p_change',
                'Difference',
                'DE Ratio',
                'Trailing P/E',
                'Price/Sales',
                'Price/Book',
                'Profit Margin',
                'Operating Margin',
                'Return on Assets',
                'Return on Equity',
                'Revenue Per Share',
                'Market Cap',
                'Enterprise Value',
                'Forward P/E',
                'PEG Ratio',
                'Enterprise Value/Revenue',
                'Enterprise Value/EBITDA',
                'Revenue',
                'Gross Profit',
                'EBITDA',
                'Net Income Avl to Common ',
                'Diluted EPS',
                'Earnings Growth',
                'Revenue Growth',
                'Total Cash',
                'Total Cash Per Share',
                'Total Debt',
                'Current Ratio',
                'Book Value Per Share',
                'Cash Flow',
                'Beta',
                'Held by Insiders',
                'Held by Institutions',
                'Shares Short (as of',
                'Short Ratio',
                'Short % of Float',
                'Shares Short (prior ',
                'Status']

    useful_f = ['DE Ratio',
                'Trailing P/E',
                'Price/Sales',
                'Price/Book',
                'Profit Margin',
                'Operating Margin',
                'Return on Assets',
                'Return on Equity',
                'Revenue Per Share',
                'Market Cap',
                'Enterprise Value',
                'Forward P/E',
                'PEG Ratio',
                'Enterprise Value/Revenue',
                'Enterprise Value/EBITDA',
                'Revenue',
                'Gross Profit',
                'EBITDA',
                'Net Income Avl to Common ',
                'Diluted EPS',
                'Earnings Growth',
                'Revenue Growth',
                'Total Cash',
                'Total Cash Per Share',
                'Total Debt',
                'Current Ratio',
                'Book Value Per Share',
                'Cash Flow',
                'Beta',
                'Held by Insiders',
                'Held by Institutions',
                'Shares Short (as of',
                'Short Ratio',
                'Short % of Float',
                'Shares Short (prior ']
    pickle_set(gather, os.path.join(data_dir, 'ratios'))
    pickle_set(features, os.path.join(data_dir, 'features'))
    pickle_set(useful_f, os.path.join(data_dir, 'useful_f'))


if __name__ == "__main__":  # pragma: no cover
    main()
