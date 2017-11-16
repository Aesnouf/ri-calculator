import collections

import pandas as pd

from lib.parameters import *


# TODO: Add these recommandations in a docstring. It will also depend on the final code organization
# SIMAPRO SYSTEM LCI FILES HAVE TO BE EXPORTED WITH THE OPTION "Detail" and "per categories"
# otherwise, some line are added and the algorithm lost itself !....

def compartment_coords(lci, compartments, new_names=None):
    """
    Gets the coordinates of given compartments in a Simapro LCI export.

    :param DataFrame lci:
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
        compartment_dict[new_names[compartments.index(compartment)]] = (start, end - 1)

    return compartment_dict


def extract_lci(lci_simapro):
    """

    :param lci_simapro:
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

    lci_simapro.loc["suspended solids, unspecified to water ground-", :] = \
        lci_simapro.loc["suspended solids, unspecified to water ground-", :] / 10000000
    lci_simapro.loc["suspended solids, unspecified to water unspecified", :] = \
        lci_simapro.loc["suspended solids, unspecified to water unspecified", :] / 10000000

    lci_table = pd.DataFrame()

    for compartment, coords in compartments.items():
        # TODO: Check that coordinates are OK (no need of +1 or -1)
        elementary_flows = pd.DataFrame(lci_simapro.iloc[coords[0]:coords[1], 2])
        elementary_flows.index = "{} to {} {}".format(lci_simapro.iloc[coords[0]:coords[1], 0],
                                                      compartment,
                                                      lci_simapro.iloc[coords[0]:coords[1], 1])
        lci_table = lci_table.append(elementary_flows)

    # TODO: What to put here?
    lci_table.columns = [filename]

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

        lci_table = extract_lci(lci_simapro)

        lcis_gathered = pd.DataFrame.join(lcis_gathered, lci_table, how='outer')
        lcis_gathered = lcis_gathered.fillna(value=0)

    # Lowercase for the index, otherwise it won't match...
    lcis_gathered.index = lcis_gathered.index.str.lower()

    # BUT i some dimensions are in double
    # the duplicate have to be suppressed.
    # they are here listed

    duplicates = lcis_gathered.index

    duplicates = [item for item, count in collections.Counter(duplicates).items() if count > 1]

    # I don't no if it is the right method but the results on each duplicate dimension are sumed and one of them is
    # suppressed

    # the two dimensions are considered the same and are sumed
    # "water to air (unspecified)"
    # "water/m3 to air (unspecified)"

    for duplicate in duplicates:
        lcis_gathered.loc[duplicate, :] = [lcis_gathered.loc[duplicate, :].sum()] * \
                                          (lcis_gathered.loc[duplicate, :].shape[0])

    lcis_gathered = lcis_gathered.fillna(value=0)
    lcis_gathered = lcis_gathered[~lcis_gathered.index.duplicated(keep='first')]

    return lcis_gathered
