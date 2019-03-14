#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module is primarily used for extracting javascript files
from the npm repository"""
import ConfigParser
import urllib
from datetime import datetime
import logging
import pickle
import os
from urllib2 import HTTPError
import _mssql
import requests
import dbconnect
import database_utils
import package_iterator


def pickle_set(data_set, path):
    """This function pickles the data structure passed into
    it as a parameter"""
    logging.info('pickling the data structure')
    pickle_out = open(path, 'wb')
    pickle.dump(data_set, pickle_out)
    pickle_out.close()


def pickle_get(path):
    """This function loads the pickled data
    structure and returns it"""
    logging.info('loading the pickle')
    if os.path.isfile(path):
        return set(pickle.load(open(path, 'rb')))
    else:
        logging.exception('No pickle found')
        return set()


def get_package_list(url, parameters, stars, packagepickle):
    """This function sends api requests, and according to the
    criteria adds the package to the set and returns it"""
    logging.info('Getting package list...')
    page = 0
    names = set()
    while True:
        page += 1
        last_stars = 0
        logging.info('page : {}'.format(str(page)))
        parameters['page'] = str(page)
        built_url = url + '/search?' + urllib.urlencode(parameters)
        try:
            package_json = requests.get(built_url).json()
        except HTTPError:
            logging.debug('API server may be down')
            return pickle_get(packagepickle)
        for package in package_json:
            if 'stars' not in package:
                continue
            last_stars = package['stars']
            if package['stars'] >= stars:
                logging.info(package['name'])
                names.add(package['name'])
                logging.info(last_stars)
        if last_stars < stars:
            logging.info('finished getting packages!')
            pickle_set(names, packagepickle)
            break
    return names


def clean_set(names, discardpickle):
    """This function cleans the data structure(set)
        of all unresponsive and erroneous links """
    logging.info('finished getting packages...')
    for i in pickle_get(discardpickle):
        names.discard(i)
    return names


def get_json_from_link(link):
    """This function returns the json from the
    package name by sending a get request"""
    logging.info('getting JSON from link :' + link)
    try:
        return requests.get(link, verify=False).json()
    except (requests.exceptions.ConnectionError, HTTPError):
        logging.exception('JSON not available at ' + link)
        return {}


def check_json(json_data):
    """This checks if the json object passed
        is valid and returns true if it is"""
    logging.info('Checking if valid JSON...')
    if '_id' not in json_data or 'dist-tags' not in json_data:
        logging.debug('JSON object has missing keys , skipping...')
        return False
    if 'latest' not in json_data['dist-tags']:
        logging.debug('JSON object has missing keys , skipping...')
        return False
    if 'versions' not in json_data:
        logging.debug('JSON object has missing keys , skipping...')
        return False
    version = json_data['dist-tags']['latest']
    if 'dist' not in json_data['versions'][version]:
        logging.debug('JSON object has missing keys , skipping...')
        return False
    if 'tarball' not in json_data['versions'][version]['dist']:
        logging.debug('JSON object has missing keys , skipping...')
        return False
    return True


def get_exe_link_from_json(json_data, version):
    """This function returns the download link from json object"""
    logging.info('Getting Download Link from JSON...')
    return json_data['versions'][version]['dist'][
        'tarball'].encode('ascii', 'ignore')


def get_name_from_json(json_data):
    """This function returns the package name from json object"""
    logging.info('Getting package name from JSON...')
    return json_data['_id'].encode('ascii', 'ignore')


def get_latest_version_from_json(json_data):
    """This function returns the latest package version from json object"""
    logging.info('Getting latest package version from JSON...')
    return json_data['dist-tags']['latest'].encode('ascii', 'ignore')


def get_licence_type_from_json(json_data):
    """This function returns the license type from json object"""
    logging.info('Getting license type from JSON...')
    if 'licence' not in json_data:
        return ''
    return json_data['license'].encode('ascii', 'ignore')


def get_producer_name_from_json(json_data):
    """This function returns the author name from json object"""
    logging.info('Getting author name from JSON...')
    if 'author' not in json_data or 'name' not in json_data['author']:
        return ''
    return json_data['author']['name'].encode('ascii', 'ignore')


def get_pub_website_from_json(json_data):
    """This function returns the publishers website from json object"""
    logging.info('Getting publishers website from JSON...')
    if 'homepage' not in json_data:
        return ''
    return json_data['homepage'].encode('ascii', 'ignore')


def get_release_date_from_json(json_data, version):
    """This function returns the release date for that version from json object"""
    logging.info('Getting release date for that version from JSON...')
    if 'time' not in json_data or version not in json_data['time']:
        return ''
    return json_data['time'][version].encode('ascii', 'ignore')


def get_config(config_file_name):
    """Read config file and return config object
    """
    options = ConfigParser.ConfigParser()
    options.read(config_file_name)
    return options


class PasswordNotSetException(Exception):
    """Raise for DB password not set"""
    pass


class GetJs(object):
    """This class extracts JS files
        from the npm registry"""

    def __init__(self, init_config):
        """This is a constructor to initialize the api url
         and database details"""

        self.table = init_config['table']
        self.url = init_config['url']
        try:
            self.dbo = database_utils.MSSQLDB(init_config['host'],
                                              init_config['dbo'],
                                              init_config['user'],
                                              init_config['password'])
        except dbconnect.DBConnectError:
            logging.critical('DB password not set correctly!')
            raise PasswordNotSetException

    def insert_sql(self, params):
        """This function inserts package and version into db"""
        query = ('INSERT INTO _TestHarvest.dbo.opensrcjs '
                 '(ProductName, ProducerName, LicType, DownloadLink, '
                 'PubWebsite, ReleaseDate, ExeLink, Version, Category, '
                 'Ext, OSType, DateAddedtoDatabase) '
                 'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, getdate())')

        try:
            logging.info('Inserting into opensrcjs...')
            self.dbo.run_query(query, params)
            return True
        except (IndexError, _mssql.MssqlDatabaseException):
            logging.exception('Could not insert into opensrcjs')
            return False

    def insert_master_sql(self, params):
        """This function inserts package and version into db"""
        query = ('INSERT INTO _TestHarvest.dbo.MasterHarvest '
                 '(ProductName, ProducerName, LType, DownloadLink, '
                 'PubWebsite, ReleaseDate, ExeLink, Version, Category,'
                 ' Source, OSType, Status, DownloadStatus, '
                 'ScanStatus,Priority, DateAddedtoDatabase) '
                 'VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?, getdate())')

        try:
            logging.info('Inserting into MasterHarvest...')
            self.dbo.run_query(query, params)
            return True
        except (IndexError, _mssql.MssqlDatabaseException):
            logging.exception('Could not insert into MasterHarvest')
            return False

    def select_sql(self, table, producer_name, product_name, version):
        """This function gets version from db"""

        query = ('Select * from {} where ProducerName = {} '
                 'AND ProductName = {} '
                 'And Version = {}'.format(table, "'" + producer_name +
                                           "'", "'" + product_name + "'",
                                           "'" + version + "'"))
        try:
            logging.info('selecting from opensrcjs...')
            return self.dbo.run_query(query)
        except (IndexError, _mssql.MssqlDatabaseException):
            logging.exception('Please check the type of data for select query')
            return None

    def select_master_sql(self, table_params):
        """This function gets version from db"""

        query = (
            'Select Sub_Id,Status,DownloadStatus from {} where ProducerName = {} '
            'AND ProductName = {} '
            'And Version = {} And Source = {}'.format(
                table_params[0],
                "'" + table_params[1] + "'",
                "'" + table_params[2] + "'",
                "'" + table_params[3] + "'",
                "'" + table_params[4] + "'"))
        try:
            logging.info('selecting from MasterHarvest...')
            return self.dbo.run_query(query)
        except (IndexError, _mssql.MssqlDatabaseException):
            logging.exception('Please check the type of data for select query')
            return None

    def update_master_sql(self, params):
        """This function updates the masterHarvest db"""

        query = (
            "UPDATE _TestHarvest.dbo.MasterHarvest SET DownloadLink = ?, ExeLink = ?,Source = ?, "
            "DateAddedtoDatabase = getdate(),Status = 'NEW',DownloadStatus = 'NOT_COMPLETED', "
            "ScanStatus='NOT_COMPLETED',TtlDownloads = 'updated',Priority=1 WHERE Sub_ID = ?")
        try:
            logging.info('Updating MasterHarvest...')
            self.dbo.run_query(query, params)
            return True
        except(IndexError, _mssql.MssqlDatabaseException):
            logging.exception(
                'Update into MasterHarvest failed, please check the values')
            return False

    def get_all_js(self, link, pickle_paths, parameters=None, stars=1000):  # pragma: no cover
        """This function downloads and saves the packages read
            from the pickle saved earlier"""

        priority_feed = True
        discard_set = []
        for name in get_package_list(
                self.url,
                parameters,
                stars,
                pickle_paths['package_pickle']):
            try:
                json_data = get_json_from_link(link + name)
            except HTTPError as error:
                logging.exception('Got error code : ' + error.code)
                discard_set.append(link + name)
                continue

            if check_json(json_data):
                for version in json_data['versions']:

                    product_name = get_name_from_json(json_data)
                    producer_name = get_producer_name_from_json(json_data)
                    lic_type = ('open source' +
                                get_licence_type_from_json(json_data))
                    download_link = get_exe_link_from_json(json_data, version)
                    pub_website = get_pub_website_from_json(json_data)
                    release_date = get_release_date_from_json(
                        json_data, version)

                    params = [
                        product_name,
                        producer_name,
                        lic_type,
                        download_link,
                        pub_website,
                        release_date,
                        download_link,
                        version,
                        'javascript',
                        'js',
                        'OS Independent',
                    ]

                    if len(
                            self.select_sql(
                                self.table,
                                producer_name,
                                product_name,
                                version)) == 0:
                        self.insert_sql(params)

                    if priority_feed is True:
                        record = self.select_master_sql(
                            ['_TestHarvest.dbo.MasterHarvest',
                             producer_name,
                             product_name,
                             version,
                             'open source'])
                        if len(record) == 0:

                            params = [
                                product_name,
                                producer_name,
                                lic_type,
                                download_link,
                                pub_website,
                                release_date,
                                download_link,
                                version,
                                'javascript',
                                'npm',
                                'OS Independent',
                                'NEW',
                                'NOT_COMPLETED',
                                'NOT_COMPLETED',
                                1,
                            ]
                            self.insert_master_sql(params)
                        else:
                            if (record[0][1] == 'Submission_Error' or
                                    record[0][2] == 'DOWNLOAD_FAILED' or
                                    record[0][2] == 'PARSING_FAILED'):
                                self.update_master_sql([download_link, download_link,
                                                        'npm', record[0][0]])
            else:

                discard_set.append(link + name)
                logging.debug('Bad Link...cleaning...' + link + name)
                continue
        pickle_set(discard_set, pickle_paths['discard_pickle'])


def main():  # pragma: no cover
    """This function is where execution starts"""
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf_rel = os.path.join(project_path, 'etc', 'config.ini')
    conf = get_config(conf_rel)

    host = conf.get('mssql', 'host')
    base_api_url = conf.get('mssql', 'base_api_url')
    dbo = conf.get('mssql', 'db')
    link = conf.get('mssql', 'link')
    table = conf.get('mssql', 'table')
    user = conf.get('mssql', 'user')
    var_dir = os.path.join(project_path, 'var')
    date = datetime.now().strftime('%Y_%m_%d')
    log_file = os.path.join(var_dir, 'log', 'open_src_logfile' + date)
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG)
    password = os.getenv('TEST_HARVEST_PASSWD')
    api_key = os.getenv('API_KEY')
    if api_key is None:
        logging.critical('API KEY not set..')
        return None

    init_config = {
        'url': base_api_url,
        'host': host,
        'dbo': dbo,
        'table': table,
        'user': user,
        'password': password}
    try:
        obj = GetJs(init_config)
    except PasswordNotSetException:
        logging.critical('Closing down..')
        return None

    parameters = {'languages': 'JavaScript', 'order': 'desc', 'page': '1',
                  'platforms': 'Bower', 'sort': 'stars',
                  'api_key': api_key, 'api_url': base_api_url}

    package_pickle_path = os.path.join(var_dir, 'data', 'package_list.pickle')
    discard_pickle_path = os.path.join(var_dir, 'data', 'discard.pickle')

    pickle_paths = {'package_pickle': package_pickle_path,
                    'discard_pickle': discard_pickle_path}
    obj.get_all_js(
        link, pickle_paths, parameters, int(
            conf.get(
                'mssql', 'stars')))


if __name__ == "__main__":  # pragma: no cover
    main()
