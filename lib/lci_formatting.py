"""
Functions used for LCI formatting.
"""


import collections

import pandas as pd
import scipy as np
from scipy import linalg

from lib.parameters import *


# TODO: Add these recommandations in a docstring. It will also depend on the final code organization
# SIMAPRO SYSTEM LCI FILES HAVE TO BE EXPORTED WITH THE OPTION "Detail" and "per categories"
# otherwise, some line are added and the algorithm lost itself !....

def compartment_coords(lci, compartments, new_names=None):
    """
    Gets the coordinates of given compartments in a Simapro LCI export.

    :param pd.DataFrame lci:
        Simapro LCI export converted in Pandas DataFrame
    :param iterable compartments:
        Iterable constituted by the names of the compartments
    :param iterable new_names:
        New compartments names (optional)
    :return: Dictionnary constituted by compartments names as keys and a tuple made of compartment first and last row as
        value
    :rtype: dict
    """

    # If new names is None, assigns compartments to it, otherwise, asserts there are one new name by compartment
    if new_names is None:
        new_names = compartments
    elif len(new_names) != len(compartments):
        raise Exception("New names number doesn't match compartments number")

    # Initializing compartment_dict
    compartment_dict = dict()

    # Looping over compartments to get their coordinates
    for compartment in compartments:

        # Getting the number of the first row of the compartment
        start = lci[lci.iloc[:, 0] == compartment].index[0] + 1

        # Looping on every rows until the first empty one to get the number of the last row of the compartment
        end = start
        while pd.notna(lci.iloc[end, 0]):
            end += 1

        # Sets the compartments name and coordinates
        compartment_dict[new_names[compartments.index(compartment)]] = (start, end)

    return compartment_dict


def extract_lci(lci_simapro, lci_name):
    """

    :param pd.DataFrame lci_simapro:
    :param str lci_name:
    :return:
    """
    compartments = compartment_coords(lci_simapro, COMPARTMENTS, NEW_NAMES)

    # Some elementary flows sub-compartment have to be modified to get a right nomenclature for rosetta....
    # If sub-comp is empty, I put unspecified
    lci_simapro.loc[lci_simapro.iloc[:, 1] != lci_simapro.iloc[:, 1], 1] = "(unspecified)"
    lci_simapro.loc[lci_simapro.iloc[:, 1] == 'in ground', 1] = "(unspecified)"
    lci_simapro.loc[lci_simapro.iloc[:, 1] == 'land', 1] = "(unspecified)"
    lci_simapro.loc[lci_simapro.iloc[:, 1] == 'in air', 1] = "(unspecified)"
    lci_simapro.loc[lci_simapro.iloc[:, 1] == 'in water', 1] = "(unspecified)"
    lci_simapro.loc[lci_simapro.iloc[:, 1] == 'in ground', 1] = "(unspecified)"
    lci_simapro.loc[lci_simapro.iloc[:, 1] == 'biotic', 1] = "(unspecified)"
    lci_simapro.loc[lci_simapro.iloc[:, 1] == 'river', 1] = "lake"

    # Bq was in kBq....
    lci_simapro.loc[lci_simapro.iloc[:, 3] == 'Bq', 2] = lci_simapro.loc[lci_simapro.iloc[:, 3] == 'Bq', 2] / 1000

    lci_simapro.loc[lci_simapro.iloc[:, 0] == 'Transformation, to pasture and meadow, extensive', 2] = \
        lci_simapro.loc[lci_simapro.iloc[:, 0] == 'Transformation, to pasture and meadow, extensive', 2] / 1000

    lci_table = pd.DataFrame()

    for compartment, coords in compartments.items():
        elementary_flows = pd.DataFrame(lci_simapro.iloc[coords[0]:coords[1], 2])
        elementary_flows.index = lci_simapro.iloc[coords[0]:coords[1], 0] + ' to ' + \
                                 compartment + ' ' + \
                                 lci_simapro.iloc[coords[0]:coords[1], 1]
        lci_table = lci_table.append(elementary_flows)

    lci_table.columns = [lci_name]

    # BUT i some dimensions are in double
    # the duplicate have to be suppressed.
    # they are here listed

    # Lowercase for the index, otherwise it won't match...
    lci_table.index = lci_table.index.str.lower()

    duplicates = lci_table.index

    duplicates = [item for item, count in collections.Counter(duplicates).items() if count > 1]

    # I don't no if it is the right method but the results on each duplicate dimension are sumed and one of them is
    # suppressed

    # the two dimensions are considered the same and are sumed
    # "water to air (unspecified)"
    # "water/m3 to air (unspecified)"

    for duplicate in duplicates:
        lci_table.loc[duplicate, :] = [lci_table.loc[duplicate, :].sum()] * \
                                      (lci_table.loc[duplicate, :].shape[0])

    lci_table = lci_table.fillna(value=0)
    lci_table = lci_table[~lci_table.index.duplicated(keep='first')]

    lci_table.loc["suspended solids, unspecified to water groundwater", :] = \
        lci_table.loc["suspended solids, unspecified to water groundwater", :] / 10000000
    lci_table.loc["suspended solids, unspecified to water (unspecified)", :] = \
        lci_table.loc["suspended solids, unspecified to water (unspecified)", :] / 10000000

    return lci_table


def gather_lcis(lcis, lci_dir):
    """



    :param iterable lcis:
        List of lcis filenames (without file extension)
    :param str lci_dir:
        Folder where all lcis files are gathered
    :return:
    :rtype: DataFrame
    """
    # for each lcis file exported from simapro and named in the list the location of each comparment
    # (resources, air, water, soil) in the excel files are extracted then the elementary flows are gathered in the same
    # dataframe 'lci_table' then all the lci_table are gathered in the same dataframe 'lcis_gathered'

    lcis_gathered = pd.DataFrame()

    for lci in lcis:
        filename = os.path.join(lci_dir, lci + ".XLSX")

        lci_simapro = pd.io.excel.read_excel(filename, header=None, skiprows=None)

        lci_table = extract_lci(lci_simapro, lci)

        lcis_gathered = pd.DataFrame.join(lcis_gathered, lci_table, how='outer')

    return lcis_gathered


def standardize_inventory(lci, db_geometric_mean):
    """

    :param pd.DataFrame lci:
    :param pd.DataFrame db_geometric_mean:
    :return:
    :rtype DataFrame
    """

    lci_standardized = pd.DataFrame.copy(lci, deep=True)  # sinon pas de réelle création d'un nouveau tableau

    for column in lci.columns:
        lci_standardized.loc[:, column] = (lci.loc[:, column]) / (db_geometric_mean.loc[:, 'gmean'])
        lci_standardized.fillna(value=0, inplace=True)
        lci_standardized.loc[:, column] = (lci_standardized.loc[:, column]) / \
                                          (np.linalg.norm(lci_standardized.loc[:, column]))

    # Data cleaning
    lci_standardized = lci_standardized.fillna(value=0)
    lci_standardized[lci_standardized == np.inf] = 0
    lci_standardized[lci_standardized == -np.inf] = 0

    return lci_standardized
