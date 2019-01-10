# from abc import ABC, abstractmethod
# import unittest

# import unittest
#
# class TestFixtures(unittest.TestCase):
#
#    @classmethod
#    def setUpClass(cls):
#        print('Start')
#
#    @classmethod
#    def tearDownClass(cls):
#       print('\ncalled once after all tests in class')
#
#    def setUp(self):
#       self.a = 10
#       self.b = 20
#       name = self.shortDescription()
#       print('\n',name)
#    def tearDown(self):
#       print('\nend of test',self.shortDescription())
#
#    def test1(self):
#       """One"""
#       result = self.a+self.b
#       self.assertTrue(True)
#    def test2(self):
#       """Two"""
#       result = self.a-self.b
#       self.assertTrue(False)
#
# if __name__ == '__main__':
#     unittest.main()





from pandas import DataFrame, read_sql
import pandas as pd
import pymysql
import config


import matplotlib.pyplot as plt
import matplotlib
import sys

print('Python Version:' + sys.version)
print('Pandas Version:' + pd.__version__)
print('Matplotlib version:' + matplotlib.__version__)
#connstr = 'foodfie.cteforntuvsh.ap-south-1.rds.amazonaws.com'
#connstr = 'Actix_load_monitor/xitca@lonrnd-ora07.actix.com:1521/oms01'
SQL = 'Select date(OrderTime), DAYOFWEEK(OrderTime) as OrderTime, sum(TotalAmount) as TotalSales from foodfie.Order group by date(OrderTime)'
#
#
# ##########################################################
# #               GET DATA                                 #
# #                                                        #
# ##########################################################
db_connect = pymysql.connect(host = config.host, port=config.port, user= config.user, password = config.password, db= config.db)
df = pd.read_sql(SQL,db_connect)
print(df.dtypes)
print(df.head())

order_day, total_sales = df['OrderTime'], df['TotalSales']

plt.scatter(order_day, total_sales)
plt.show()
pass

#
# ##########################################################
# #               PREPARE DATA                             #
# #                                                        #
# ##########################################################
#
#
# ##########################################################
# #               ANALYZE DATA                             #
# #                                                        #
# ##########################################################
#
#
# ##########################################################
# #               PRESENT DATA                             #
# #                                                        #
# ##########################################################
#
# # Create graph
# df['LOADID'].plot()
#
# # Maximum value in the data set
# MaxValue = df['LOADID'].max()

#
# import requests
# from bs4 import BeautifulSoup as bs
# from requests.auth import HTTPBasicAuth
# headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
# r = requests.get("https://www.naukri.com/python-jobs", headers = headers)#auth = HTTPBasicAuth('vipspulyani@gmail.com', 'jaimatadi'))
#
# soup = bs(r.content)
# for link in soup.find_all("a"):
#     print(link.get("href"))

