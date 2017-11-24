"""
Representativeness index calculation functions
"""

import pandas as pd
import scipy as sp
from scipy import linalg

from lib.methods_formatting import clean_method, orthonormation_method, filter_methods


def representativeness_index_per_category(methods_standardized, lci_standardized):
    """
    Calculates a Representativeness Index per impact category on one or many standardized LCI(s)

    :param pd.DataFrame methods_standardized:
        Dataframe constituted one or many method(s) aggregated, ie. constituted of several columns representing impact 
        categories
    :param pd.DataFrame lci_standardized:
        LCI(s) data formatted with standardize_lci()
    :return:
        Representativeness index per impact category
    :rtype: pd.DataFrame
    """
    lci_standardized.fillna(value=0, inplace=True)
    methods_standardized.fillna(value=0, inplace=True)

    # Checking substance flows (indexes) are the same between lci and method
    if all(methods_standardized.index == lci_standardized.index):
        representativeness_index = pd.DataFrame(index=methods_standardized.columns,
                                                columns=lci_standardized.columns)
        for i in range(0, representativeness_index.shape[0]):
            residuals = linalg.lstsq(sp.matrix(methods_standardized.iloc[:, i]).T, lci_standardized)[1]
            representativeness_index.iloc[i, :] = sp.cos(sp.real(sp.arcsin(sp.sqrt(residuals)))).T

    else:
        raise Exception('Substance flows do not match between method and lci.')

    return representativeness_index


def representativeness_index_per_method(methods_standardized, methods_names, lci_standardized):
    """
    Calculates a Representativeness Index per method and LCI

    :param pd.DataFrame methods_standardized:
        Dataframe constituted one or many method(s) aggregated, ie. constituted of several columns representing impact
        categories normalized
    :param iterable methods_names:
        Iterable constituted by the names of the methods to study
    :param pd.DataFrame lci_standardized:
        LCI(s) data formatted with standardize_lci()
    :return:
        Representativeness index per method
    :rtype pd.DataFrame
    """

    representativeness_index = pd.DataFrame(columns=lci_standardized.columns, dtype=float)

    lci_standardized = lci_standardized.fillna(value=0)

    for method_name in methods_names:

        method = filter_methods(methods_standardized, method_name)

        method_cleaned = clean_method(method)
        method_ortho = orthonormation_method(method_cleaned)

        residual = linalg.lstsq(method_ortho, lci_standardized)[1]

        emission_norm = pd.DataFrame(index=['norm'], columns=lci_standardized.columns)
        for column in emission_norm.columns:
            emission_norm[column] = linalg.norm(lci_standardized[column])

        cos_projection = pd.DataFrame(sp.cos(sp.real(sp.arcsin(sp.sqrt(residual) / (sp.array(emission_norm))))),
                                      dtype='float', columns=lci_standardized.columns, index=['cos'])

        representativeness_index.loc[method_name] = cos_projection.iloc[0, :]

    return representativeness_index
