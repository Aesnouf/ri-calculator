"""
Representativeness index calculation functions
"""

import pandas as pd
import scipy as np

from lib.methods_formatting import clean_method, orthonormation_method


def calculate_representativeness_index_per_category(method_standardized, lci_standardized):
    """

    :param pd.DataFrame method_standardized:
    :param pd.DataFrame lci_standardized:
    :return:
    :rtype: DataFrame
    """
    lci_standardized.fillna(value=0, inplace=True)
    method_standardized.fillna(value=0, inplace=True)

    # Checking substance flows (indexes) are the same between lci and method
    if all(method_standardized.index == lci_standardized.index):
        representativeness_index_category = pd.DataFrame(index=method_standardized.columns,
                                                         columns=lci_standardized.columns)
        for i in range(0, representativeness_index_category.shape[0]):
            residuals = np.linalg.lstsq(np.matrix(method_standardized.iloc[:, i]).T, lci_standardized)[1]
            representativeness_index_category.iloc[i, :] = np.cos(np.real(np.arcsin(np.sqrt(residuals)))).T

    else:
        raise Exception('Substance flows do not match between method and lci.')

    return representativeness_index_category


def calculate_representativeness_index_per_method(method_standardized, method_name, emission_standardized):
    """
    Calculates a Representativeness Index per category for a given method and LCI

    clean_method() just reorganizes impact categories by ordering them by ascending number of characterisation factor
    and drops methods if they are empty (as in the case of studying a piece of the emission)

    orthonomation_meth() transforms impact categories to get them orthonormed.
    Then it uses linalg.lstsq() to get euclidian distance between LCI and the most accurate modelisation point
    in the environmental basis. This euclidian distance is then used to get the angle (just some trigonometric trick).

    :param pd.DataFrame method_standardized:
        Dataframe composed by only one method agregated composed of several columns representing impact category
        normalised
    :param str method_name:
        Method name
    :param pd.DataFrame emission_standardized:
        Dataframe of all LCIs of the database
    :return:
    :rtype DataFrame
    """

    cos_method = pd.DataFrame(columns=emission_standardized.columns, dtype=float)

    method_standardized_cleaned = clean_method(method_standardized)

    method_standardized_ortho = orthonormation_method(method_standardized_cleaned)

    emission_standardized = emission_standardized.fillna(value=0)
    coeff, residual, rank, singular_values = np.linalg.lstsq(np.array(method_standardized_ortho.iloc[:, :]),
                                                             np.array(emission_standardized))  # .iloc[:,:]))

    # Emissions are then normed and values are stored in a dataframe

    emission_norm = pd.DataFrame(index=['norm'], columns=emission_standardized.columns)
    for column in emission_norm.columns:
        emission_norm[column] = np.linalg.norm(emission_standardized[column])

    # Residual are actually euclidean distance squared. We wanna angle or their cosinus.
    # The next code is just a trigonometric formula sin(alpa)=opposite side divided by hypothenus (norme)
    # Real function is used otherwise angle can get imaginary part (still don't know why... tried...)
    # Cosinus of the angle is then calculated

    cos_projection = pd.DataFrame(np.cos(np.real(np.arcsin(np.sqrt(residual) / (np.array(emission_norm))))),
                                  dtype='float', columns=emission_standardized.columns, index=['cos'])

    cos_method.loc[method_name] = cos_projection.iloc[0, :]

    return cos_method
