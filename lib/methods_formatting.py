"""
Functions used for methods formatting.
"""

import pandas as pd
from scipy import linalg


def clean_method(method_standardized):
    """
    This function cleans a methods.

    Removes empty impact categories (constituted by 0 only) from the method and sort them by number of non zero values.

    :param pd.DataFrame method_standardized:
        Standardized method to be cleaned
    :return: Cleaned method
    :rtype DataFrame
    """

    method_standardized_cleaned = method_standardized.copy(deep=True)
    method_standardized_cleaned = method_standardized_cleaned.fillna(value=0)

    # If a category is empty, deletes it from the method
    categories = method_standardized_cleaned.columns.tolist()
    for category in categories:
        if linalg.norm(method_standardized_cleaned[category]) == 0:
            method_standardized_cleaned.drop(category, inplace=True, axis=1)

    # Sorting on the number of CF per category. Makes orthogonal projection easier in the next step.
    just_ones = method_standardized_cleaned.copy(deep=True)
    just_ones[just_ones != 0] = 1
    sum_ones = just_ones.sum(axis=0)
    sum_ones.sort_values(ascending=True, inplace=True)
    method_standardized_cleaned = method_standardized_cleaned[sum_ones.index]

    return method_standardized_cleaned


def orthonormation_method(method_standardized_cleaned):
    """
    Orthonormation of the impact categories according to the order resulting of clean_method()

    A loop on impact categories is performed. Each category is transformed by suppressing any componant belonging to
    each previous category in the loop. I.E each category is orthogonized related to the other categories.
    Impact categories are also normalized (norme = 1).

    :param pd.DataFrame method_standardized_cleaned:
        Standardized method sorted and cleaned of its empty impact categories with clean_method()
    :return: Orthonormed method
    :rtype pd.DataFrame
    """
    method_standardized_ortho = method_standardized_cleaned.copy(deep=True)

    categories = method_standardized_ortho.columns.tolist()

    # normation of the first category
    method_standardized_ortho[categories[0]] = method_standardized_ortho[categories[0]] / \
                                               linalg.norm(method_standardized_ortho[categories[0]])

    # Normation of every following categories
    j = 0
    while j < len(categories):
        i = 0
        while i < j:
            # Calculates the orthogonal projection of j on each i and substraction of the projection from j
            method_standardized_ortho[categories[j]] = \
                method_standardized_ortho[categories[j]] - method_standardized_ortho[categories[i]] * (
                        sum(method_standardized_ortho[categories[i]] * method_standardized_ortho[categories[j]]) /
                        sum(method_standardized_ortho[categories[i]] * method_standardized_ortho[categories[i]]))
            if linalg.norm(method_standardized_ortho[categories[j]]) == 0:
                # If after the projection, the j columns is null, it is droped (i.e it is linearly dependant with
                # the other columns) and the inner loop stops
                method_standardized_ortho.drop(method_standardized_ortho.columns[j], inplace=True, axis=1)
                categories.remove(categories[j])

                break
            else:
                # If the j column is not null, it is normed and the inner while loop keeps going
                method_standardized_ortho[categories[j]] = method_standardized_ortho[categories[j]] / \
                                                           (linalg.norm(method_standardized_ortho[categories[j]]))
                i += 1
        j += 1

    return method_standardized_ortho


def filter_methods(methods_standardized, methods_to_filter):
    """
    Filters a standardized methods DataFrame on methods name

    :param pd.DataFrame methods_standardized:
        Dataframe constituted one or many method(s) aggregated, ie. constituted of several columns representing impact
        categories normalized
    :param iterable or str methods_to_filter:
        Names of the methods to filter
    :return: Filtered methods
    :rtype: pd.DataFrame
    """

    # Ensuring methods_to_filter is a list. Usefull in case of usage with a string.
    if type(methods_to_filter) == str:
        methods_to_filter = [methods_to_filter]

    # Gets the columns containing an entity of methods_to_filter in their name
    columns = [column for column in methods_standardized.columns if any(x in column for x in methods_to_filter)]

    filtered_methods = methods_standardized.loc[:, columns]

    return filtered_methods
