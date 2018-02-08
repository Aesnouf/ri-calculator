"""
Representativeness index calculation functions
"""

import pandas as pd
import scipy as sp
import numpy as np
from scipy import linalg

from lib.methods_formatting import clean_method, orthonormation_method, filter_methods


def representativeness_index_per_category(standardized_methods, standardized_lcis):
    """
    Calculates a Representativeness Index per impact category on one or many standardized LCI(s)

    :param pd.DataFrame standardized_methods:
        Dataframe constituted by one or many method(s) aggregated, ie. constituted by several columns representing
        impact categories
    :param pd.DataFrame standardized_lcis:
        LCI(s) data formatted with standardize_lci()
    :return:
        Representativeness index per impact category
    :rtype: pd.DataFrame
    """
    standardized_lcis.fillna(value=0, inplace=True)
    standardized_methods.fillna(value=0, inplace=True)

    # Checking substance flows (indexes) are the same between lci and method
    if all(standardized_methods.index == standardized_lcis.index):
        representativeness_index = pd.DataFrame(index=standardized_methods.columns,
                                                columns=standardized_lcis.columns)
        for i in range(0, representativeness_index.shape[0]):
            residuals = linalg.lstsq(sp.matrix(standardized_methods.iloc[:, i]).T, standardized_lcis)[1]
            representativeness_index.iloc[i, :] = sp.cos(sp.real(sp.arcsin(sp.sqrt(residuals)))).T

    else:
        raise Exception('Substance flows do not match between method and lci.')

    return representativeness_index


def representativeness_index_per_method(standardized_methods, methods_names, standardized_lcis):
    """
    Calculates a Representativeness Index per method and LCI

    :param pd.DataFrame standardized_methods:
        Dataframe constituted by one or many method(s) aggregated, ie. constituted by several columns representing
        impact categories normalized
    :param iterable methods_names:
        Iterable constituted by the names of the methods to study
    :param pd.DataFrame standardized_lcis:
        LCI(s) data formatted with standardize_lci()
    :return:
        Representativeness index per method
    :rtype pd.DataFrame
    """

    representativeness_index = pd.DataFrame(columns=standardized_lcis.columns, dtype=float)

    standardized_lcis = standardized_lcis.fillna(value=0)

    for method_name in methods_names:

        method = filter_methods(standardized_methods, method_name)

        method_cleaned = clean_method(method)
        method_ortho = orthonormation_method(method_cleaned)

        residual = linalg.lstsq(method_ortho, standardized_lcis)[1]

        emission_norm = pd.DataFrame(index=['norm'], columns=standardized_lcis.columns)
        for column in emission_norm.columns:
            emission_norm[column] = linalg.norm(standardized_lcis[column])

        cos_projection = pd.DataFrame(sp.cos(sp.real(sp.arcsin(sp.sqrt(residual) / (sp.array(emission_norm))))),
                                      dtype='float', columns=standardized_lcis.columns, index=['cos'])

        representativeness_index.loc[method_name] = cos_projection.iloc[0, :]

    return representativeness_index


def representativeness_index_per_orthogonalized_category(standardized_methods, method_names, standardized_lcis):
    """
    Calculates a Representativeness Index per orthogonalized impact category on one or many standardized LCI(s)

    :param pd.DataFrame standardized_methods:
        Dataframe constituted by one or many method(s) aggregated, ie. constituted by several columns representing
        impact categories normalized
    :param iterable method_names:
        Iterable constituted by the names of the methods to study
    :param pd.DataFrame standardized_lcis:
        LCI(s) data formatted with standardize_lci()
    :return:
        Representativeness index per orthogonalized category
    :rtype pd.DataFrame
    """

    ri_cat_original = representativeness_index_per_category(standardized_methods=standardized_methods,
                                                            standardized_lcis=standardized_lcis)
    ri_cat_original_sq = ri_cat_original.applymap(np.square)

    result = pd.DataFrame(columns=standardized_lcis.columns)

    for method_name in method_names:
        categories = filter_methods(standardized_methods, method_name)
        category_names = categories.columns

        # Categories normation
        for category in category_names:
            categories[category] = categories[category] / linalg.norm(categories[category])

        # Calculating correlation matrix
        correlation_matrix = pd.DataFrame(index=category_names, columns=category_names)

        for j in range(0, correlation_matrix.shape[0]):
            for i in range(0, j + 1):
                correlation_matrix.iloc[j, i] = abs(categories.iloc[:, i] * categories.iloc[:, j]).sum()
                correlation_matrix.iloc[i, j] = abs(categories.iloc[:, i] * categories.iloc[:, j]).sum()

        # Reordering categories
        ordered_category_names = correlation_matrix.sum().sort_values(ascending=False).index
        ordered_categories = categories.loc[:, ordered_category_names]

        # Orthonorming categories
        orthonormed_categories = orthonormation_method(ordered_categories)

        # Calculating RI for orthonormed categories
        ri_cat_ortho = representativeness_index_per_category(standardized_methods=orthonormed_categories,
                                                             standardized_lcis=standardized_lcis)
        ri_cat_ortho_sq = ri_cat_ortho.applymap(np.square)

        # Creating a DataFrame containing differences between ri_cat_original and ri_cat_ortho
        diff = ri_cat_original_sq.loc[ri_cat_ortho_sq.index, :] - ri_cat_ortho_sq

        # Creating a copy of ri_cat_ortho_sq that will be modified to obtain the final result for this method
        result_per_method = ri_cat_original_sq.copy(deep=True)

        # Looping on ordered categories and lcis to update values in result_per_method
        for category in ordered_categories:
            correlated_categories = correlation_matrix.loc[:, correlation_matrix.loc[:, category] != 0].columns
            correlated_categories_ri = ri_cat_original_sq.loc[correlated_categories, :]

            # Looping on lcis
            for lci in standardized_lcis.columns:
                result_per_method.loc[correlated_categories, lci] -= diff.loc[category, lci] * \
                                                                     (correlated_categories_ri.loc[:, lci] /
                                                                      correlated_categories_ri.loc[:, lci].sum(axis=0))
        # Appending the result per method to the final result
        result = result.append(result_per_method.loc[category_names, :])

    result = result.applymap(np.sqrt)

    return result
