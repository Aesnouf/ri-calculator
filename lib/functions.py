"""
Functions used for RI Calculation
"""

import scipy as np
import pandas as pd
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


def clean_method(method_standardized):
    """
    This function cleans a methods.

    Removes empty categories (constituted by 0 only) from the method and sort them by number of non zero values.

    :param DataFrame method_standardized:
    :return: Cleaned method
    :rtype DataFrame
    """

    method_standardized = method_standardized.fillna(value=0)

    # If a category is empty, deletes it from the method
    categories = method_standardized.columns.tolist()
    for category in categories:
        if np.linalg.norm(method_standardized[category]) == 0:
            method_standardized.drop(category, inplace=True, axis=1)

    # Now it is just a sorting step with the number of CF per category. This will make get more proper orthogonal
    # projection for the next step
    just_ones = method_standardized.copy(deep=True)
    just_ones[just_ones != 0] = 1
    sum_ones = just_ones.sum(axis=0)
    sum_ones.sort_values(ascending=True, inplace=True)
    method_standardized_cleaned = method_standardized[sum_ones.index]

    return method_standardized_cleaned


def orthonormation_method(method_standardized_cleaned):
    """
    Orthonormation of the categories according to the order resulting of clean_method()

    A loop on categories is performed. Each category is transformed by supressing any composant belonging to
    each previous category in the loop. I.E each category is orthogonized related to the other categories.
    Categories are also normalised (norme = 1).

    :param DataFrame method_standardized_cleaned:
        Standardized method sorted and cleaned of its empty categories with clean_method()
    :return: Orthonormed method
    :rtype DataFrame
    """
    categories = method_standardized_cleaned.columns.tolist()

    # normation of the first category
    method_standardized_cleaned[categories[0]] = method_standardized_cleaned[categories[0]] / np.linalg.norm(
        method_standardized_cleaned[categories[0]])

    # normation of every following categories in a loop
    # j is a cursor that will pass every category (columns). The loop is stoped by the total number of category in the
    # method
    j = 0
    while j < len(categories):
        # i is a cursor that will pass every columns from 0 to j (j not included)
        # loop is a boolean used to end the next loop
        i = 0
        while i < j:
            # calculate the orthogonal projection of j on each i and substraction of the projection from j
            method_standardized_cleaned[categories[j]] = \
                method_standardized_cleaned[categories[j]] - method_standardized_cleaned[categories[i]] * (
                sum(method_standardized_cleaned[categories[i]] * method_standardized_cleaned[categories[j]]) / sum(
                    method_standardized_cleaned[categories[i]] * method_standardized_cleaned[categories[i]]))
            if np.linalg.norm(method_standardized_cleaned[categories[j]]) == 0:
                # if after the projection, the j columns became null, it is droped (i.e it is linearly dependant with
                # the other columns)
                method_standardized_cleaned.drop(method_standardized_cleaned.columns[j], inplace=True, axis=1)
                categories.remove(categories[j])

                # then the inner while loop ends
                break
            else:
                # the non null columns j is normed and the inner while loop keeps going
                method_standardized_cleaned[categories[j]] = method_standardized_cleaned[categories[j]] / (
                    np.linalg.norm(method_standardized_cleaned[categories[j]]))
                i += 1
        j += 1

    return method_standardized_cleaned


def calculate_representativeness_index_per_category(method_standardized, lci_standardized):
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


def calculate_representativeness_index_per_method(method_standardized, method, emission_normal, cos_method):
    """
    method_standardized is a dataframe with only one method agregated composed of several columns representing
    impact category normalised
    'method' is just a string naming the method
    emission_normal is the dataframe of all LCI
    cos_meth is a dataframe with method as row and process as columns. for each process it give the cosinus between
    the LCI and its projected on the environmental basis

    df_to_study just reorganize impact category by ordering them with a ascending number of characterisation factor
    and drop method if they are empty (like in the case of studying a piece of the emission)

    orthonomation_meth transforme impact categories to get them orthonormised
    find_cos_residual used linalg.lstsq to get euclidian distance between LCI and the most accurate modelisation point
    in the environmental basis. This euclidian distance is then used to get the angle (just some trigonometric trick)

    :param method_standardized:
    :param method:
    :param emission_normal:
    :param cos_method:
    :return:
    """

    (method_standardized_cleaned, cols) = clean_method(method_standardized)

    # !!! the next step moodify method_standardized_cleaned !!!
    method_standardized_ortho = orthonormation_method(method_standardized_cleaned)

    coeff, residual, rank, singular_values = np.linalg.lstsq(np.array(method_standardized_ortho.iloc[:, :]),
                                                             np.array(emission_normal))  # .iloc[:,:]))

    # emissions are then normed and values are stored in a dataframe

    emission_norm = pd.DataFrame(index=['norm'], columns=emission_normal.columns)
    for column in emission_norm.columns:
        emission_norm[column] = np.linalg.norm(emission_normal[column])

    # Residual are actually euclidean distance squared. We wanna angle or their cosinus.
    # The next code is just a trigonometric formula sin(alpa)=opposite side divided by hypothenus (norme)
    # Real function is used otherwise angle can get imaginary part (still don't know why... tried...)
    # Cosinus of the angle is then calculated

    cos_projection = pd.DataFrame(np.cos(np.real(np.arcsin(np.sqrt(residual) / (np.array(emission_norm))))),
                                  dtype='float', columns=emission_normal.columns, index=['cos'])

    cos_method.loc[method] = cos_projection.iloc[0, :]

    return method_standardized_ortho, cos_method
