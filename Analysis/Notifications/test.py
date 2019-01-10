# from sklearn import neural_network.
#
# class Python:
#
#     vips = 'aa'
#
#     def __init__(self, name, age):
#         self.name = name
#         self.age = age
#
#     def print_data(self):
#         print(self.name, self.age)
#
#     @classmethod
#     def print_class(cls):
#         print(Python.vips)
#
#
# class Python3(Python):
#
#     def __init__(self, name, age, company):
#         Python.__init__(self, name, age)
#         self.company = company
#
#
#     def print_python3(self):
#         Python.print_class()
#
#
# a = Python3(5,10, 15)
# a.print_data()
# a.print_class()
# a.print_python3()
# Python.print_class()
#


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.preprocessing import Imputer

# Importing the dataset

df = pd.read_csv('Data.csv')
X = df.iloc[:, :-1].values
y = df.iloc[:, 3].values

imputer = Imputer(missing_values = 'Nan', strategy = 'mean', axis = 0)
imputer = imputer.fit(X[:, 1:3])

X[:, 1:3] = imputer.transform(X[:, 1:3])

