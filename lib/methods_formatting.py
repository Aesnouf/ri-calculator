"""
Functions used for methods formatting.
"""

# TODO ANTOINE: Complete docstrings with explaination on what the functions does and how it must be used. Not with how it does it nor how it is implemented

import pandas as pd
from scipy import linalg


def clean_method(method_standardized):
    """
    This function cleans a methods.

    Removes empty categories (constituted by 0 only) from the method and sort them by number of non zero values.

    :param pd.DataFrame method_standardized:
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

    # Now it is just a sorting step with the number of CF per category. This will make get more proper orthogonal
    # projection for the next step
    just_ones = method_standardized_cleaned.copy(deep=True)
    just_ones[just_ones != 0] = 1
    sum_ones = just_ones.sum(axis=0)
    sum_ones.sort_values(ascending=True, inplace=True)
    method_standardized_cleaned = method_standardized_cleaned[sum_ones.index]

    return method_standardized_cleaned


def orthonormation_method(method_standardized_cleaned):
    """
    Orthonormation of the categories according to the order resulting of clean_method()

    A loop on categories is performed. Each category is transformed by supressing any composant belonging to
    each previous category in the loop. I.E each category is orthogonized related to the other categories.
    Categories are also normalised (norme = 1).

    :param pd.DataFrame method_standardized_cleaned:
        Standardized method sorted and cleaned of its empty categories with clean_method()
    :return: Orthonormed method
    :rtype DataFrame
    """
    method_standardized_ortho = method_standardized_cleaned.copy(deep=True)

    categories = method_standardized_ortho.columns.tolist()

    # normation of the first category
    method_standardized_ortho[categories[0]] = method_standardized_ortho[categories[0]] / linalg.norm(
        method_standardized_ortho[categories[0]])

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
            method_standardized_ortho[categories[j]] = \
                method_standardized_ortho[categories[j]] - method_standardized_ortho[categories[i]] * (
                    sum(method_standardized_ortho[categories[i]] * method_standardized_ortho[categories[j]]) / sum(
                        method_standardized_ortho[categories[i]] * method_standardized_ortho[categories[i]]))
            if linalg.norm(method_standardized_ortho[categories[j]]) == 0:
                # if after the projection, the j columns became null, it is droped (i.e it is linearly dependant with
                # the other columns)
                method_standardized_ortho.drop(method_standardized_ortho.columns[j], inplace=True, axis=1)
                categories.remove(categories[j])

                # then the inner while loop ends
                break
            else:
                # the non null columns j is normed and the inner while loop keeps going
                method_standardized_ortho[categories[j]] = method_standardized_ortho[categories[j]] / (
                    linalg.norm(method_standardized_ortho[categories[j]]))
                i += 1
        j += 1

    return method_standardized_ortho
