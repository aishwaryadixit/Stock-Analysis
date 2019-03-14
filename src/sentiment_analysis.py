import ConfigParser
from datetime import datetime, timedelta
import logging
import os
import pysentiment as ps
import tweepy
import time
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup


def get_config(config_file_name):
    # Read config file and return config object
    options = ConfigParser.ConfigParser()
    options.read(config_file_name)
    return options


def get_twitter_sentiment(ticker, company, auth_keys):
    # fetch oath tokens from config.ini to secure them

    ckey = auth_keys.get('ckey')
    csecret = auth_keys.get('csecret')
    atoken = auth_keys.get('atoken')
    asecret = auth_keys.get('asecret')

    auth = tweepy.OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)
    api = tweepy.API(auth)

    hiv4 = ps.HIV4()
    ss = '!!'  # cleaning mark
    t = ""
    s = ''
    d = datetime.today()
    d7 = d - timedelta(days=7)
    d = d.strftime("%Y-%m-%d")
    d7 = d7.strftime("%Y-%m-%d")
    try:
        for tweet in tweepy.Cursor(api.search, q=company, since=str(d7), until=str(d), lang="en").items():
            s = ss + tweet.text
            # cleaning the tweets
            s = s.replace(ss + 'RT ', '')
            result = re.sub(r"http\S+", "", s)
            # http  matches literal characters
            # \S+ matches all non-whitespace characters (the end of the url)

            t = t + result + '\n'
    except Exception as e:
        time.sleep(10)

        try:
            for tweet in tweepy.Cursor(api.search, q=ticker, since=d7, until=d, lang="en").items():
                s = ss + tweet.text
                # cleaning the tweets
                s = s.replace(ss + 'RT ', '')
                result = re.sub(r"http\S+", "", s)
                # http  matches literal characters
                # \S+ matches all non-whitespace characters (the end of the url)

                t = t + result + '\n'
        except Exception as e:
            time.sleep(10)

    tokens = hiv4.tokenize(t)
    score = hiv4.get_score(tokens)
    return score


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

    auth_keys = {'ckey': conf.get('twitter', 'ckey'),
            'csecret': conf.get('twitter', 'csecret'),
            'atoken': conf.get('twitter', 'atoken'),
            'asecret': conf.get('twitter', 'asecret')}


if __name__ == "__main__":  # pragma: no cover
    main()
