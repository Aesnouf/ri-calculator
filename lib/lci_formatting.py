import os
import collections

import pandas as pd

from lib.parameters import *


# SIMAPRO SYSTEM LCI FILES HAVE TO BE EXPORTED WITH THE OPTION "Detail" and "per categories"
# otherwise, some line are added and the algorithm lost itself !....


def localisation_compartment(lci):
    v = pd.DataFrame(lci.iloc[:, 0] == 'Resources', columns=["start"])
    w = pd.DataFrame(lci.iloc[:, 0] == 'Emissions to air', columns=["start"])
    x = pd.DataFrame(lci.iloc[:, 0] == 'Emissions to water', columns=["start"])
    z = pd.DataFrame(lci.iloc[:, 0] == 'Emissions to soil', columns=["start"])

    v = v[(v != 0).all(1)]
    w = w[(w != 0).all(1)]
    x = x[(x != 0).all(1)]
    z = z[(z != 0).all(1)]

    v = v.append(w)
    v = v.append(x)
    v = v.append(z)

    v.loc[:, 'start'] = v.index

    v["end"] = [0] * 4

    for i in v.index:
        j = i
        while lci.iloc[j, 0] == lci.iloc[j, 0]:
            j += 1
        v.loc[i, 'end'] = j

    v.index = ['Raw', 'Air', 'Water', 'Soil']
    # for

    return v


def extract_lci(lci_simapro, loca):
    liste_serie = list()
    liste_df = list()

    # Some elementary flows sub-compartment have to be modified to gat a right nomenclature for rosetta....
    lci_simapro.loc[lci_simapro.iloc[:, 1] != lci_simapro.iloc[:,
                                              1], 1] = "(unspecified)"  # if sub-comp is empty, i put unspecified
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

    for i in range(0, loca.shape[0]):
        elementary_flows = pd.DataFrame(lci_simapro.iloc[loca.iloc[i, 0] + 1:loca.iloc[i, 1], 2])
        elementary_flows.index = lci_simapro.iloc[loca.iloc[i, 0] + 1:loca.iloc[i, 1], 0] + ' to ' + loca.index[
            i] + ' ' + lci_simapro.iloc[loca.iloc[i, 0] + 1:loca.iloc[i, 1], 1]
        lci_table = lci_table.append(elementary_flows)

    lci_table.columns = [filename_caract]

    return lci_table  # liste_serie est liste de serie, meth_df est liste de dataframe


rosetta = pd.io.excel.read_excel(DIR + ROSETTA, sheetname="ee", header=0, skiprows=None)

# TODO GUS: Refactor path and constants usage

lcis_gathered = pd.DataFrame()

# for each lcis file exported from simapro and named in the list
# the location of each comparment (resources, air, water, soil) in the excel files are extracted
# then the elementary flows are gathered in the same dataframe 'lci_table'
# then all the lci_table are gathered in the same dataframe 'lcis_gathered'

for lci in LCIS:
    filename_caract = lci
    cwdd = os.path.expanduser("C:/Users/Esnoufa/Documents/Python_data/")

    lci_simapro = pd.io.excel.read_excel(cwdd + "/lci_from_simapro/" + filename_caract + ".XLSX", header=None,
                                         skiprows=None)

    loca = localisation_compartment(lci_simapro)
    lci_table = extract_lci(lci_simapro, loca)

    lcis_gathered = pd.DataFrame.join(lcis_gathered, lci_table, how='outer')
    lcis_gathered = lcis_gathered.fillna(value=0)

# lowercase for the index, otherwise it won't match...
lcis_gathered.index = lcis_gathered.index.str.lower()

# BUT i some dimensions are in double
# the duplicate have to be suppressed.
# they are here listed

dupli = lcis_gathered.index

dupli = [item for item, count in collections.Counter(dupli).items() if count > 1]

# I don't no if it is the right method but the results on each duplicate dimension are sumed and one of them is suppressed

# the two dimensions are considered the same and are sumed
# "water to air (unspecified)"
# "water/m3 to air (unspecified)"


for i in dupli:
    lcis_gathered.loc[i, :] = [lcis_gathered.loc[i, :].sum()] * (lcis_gathered.loc[i, :].shape[0])

lcis_gathered = lcis_gathered.fillna(value=0)
lcis_gathered = lcis_gathered[~lcis_gathered.index.duplicated(keep='first')]
