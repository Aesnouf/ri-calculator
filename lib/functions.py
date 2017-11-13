"""
Functions used for RI Calculation
"""

import scipy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import os
import pandas as pd
import xlrd
from mpl_toolkits.mplot3d import Axes3D
import math
import scipy.linalg
from sklearn import decomposition
import time
from numpy import inf


def standardize_inventory(lci, db_geometric_mean):
    """

    :param DataFrame lci:
    :param DataFrame db_geometric_mean:
    :return:
    :rtype DataFrame
    """

    lci_standardized = pd.DataFrame.copy(lci, deep=True)  # sinon pas de réelle création d'un nouveau tableau

    for column in lci.columns:
        lci_standardized.loc[:, column] = (lci.loc[:, column]) / (db_geometric_mean.loc[:, 'gmean'])

    # Data cleaning
    lci_standardized = lci_standardized.fillna(value=0)
    lci_standardized[lci_standardized == inf] = 0
    lci_standardized[lci_standardized == -inf] = 0

    return lci_standardized


def calculate_representativeness_index_category(method_standardized, lci_standardized):
    """

    :param method_standardized:
    :param lci_standardized:
    :return:
    """

    if all(method_standardized.index == lci_standardized.index):
        representativeness_index_category = pd.DataFrame(index=method_standardized.columns,
                                                         columns=lci_standardized.columns)
        for column in representativeness_index_category.columns:
            residuals = np.linalg.lstsq(np.matrix(method_standardized.loc[:, column]).T, lci_standardized)[1]
            representativeness_index_category.loc[column, :] = np.cos(np.real(np.arcsin(np.sqrt(residuals)))).T

    else:
        raise Exception('substance flows do not match')

    return representativeness_index_category
