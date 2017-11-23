"""
One line short summary description

5-6 lines brief description of the program

Author: Antoine Esnouf
Contributor: Gustave Coste
Contact: antoine.esnouf@inra.fr
Date: November 2017
"""
# TODO: Write a brief description of the program in the above dosctring and copy it in README.md

import os

import pandas as pd

from lib.lci_formatting import gather_lcis, standardize_inventory
from lib.ri_calculation import calculate_representativeness_index_per_category, \
    calculate_representativeness_index_per_method
from lib.parameters import METHODS_LIST, GMEAN, METHODS

############################################### VALUES TO UPDATE #######################################################

# Directory where are stored the simapro lcis
LCIS_DIR = "Path/to/the/lcis/directory"

# Names of the simapro lci files (without file extension)
LCIS = ['lci1', 'lci2', '...', ]

# Directory to export the results
EXPORT_DIR = "Path/to/export/directory"


# Uncomment and change these if you want, defaults are ri_category.xlsx and ri_methods.xlsx
# RI_CATEGORY_FILENAME = "your_filename"
# RI_METHODS_FILENAME = "your_other_filename"

########################################################################################################################

# RI CALCULATION
def main():
    gmean = pd.io.excel.read_excel(GMEAN)
    methods = pd.io.excel.read_excel(METHODS)

    lcis = gather_lcis(LCIS, LCIS_DIR)
    lcis = lcis.reindex(index=methods.index)
    std_lci = standardize_inventory(lcis, gmean)
    ri_cat = calculate_representativeness_index_per_category(methods, std_lci)

    meth_to_study = methods.loc[:, [s for s in methods.columns if METHODS_LIST[0] in s]]
    ri_methods = calculate_representativeness_index_per_method(meth_to_study, METHODS_LIST[0], std_lci)

    # Exporting data
    try:
        ri_category_filename = RI_CATEGORY_FILENAME + ".xlsx"
    except NameError:
        ri_category_filename = "ri_category.xlsx"

    try:
        ri_methods_filename = RI_METHODS_FILENAME + ".xlsx"
    except NameError:
        ri_methods_filename = "ri_methods.xlsx"

    pd.DataFrame.to_excel(ri_cat, os.path.join(EXPORT_DIR, ri_category_filename))
    pd.DataFrame.to_excel(ri_methods, os.path.join(EXPORT_DIR, ri_methods_filename))


if __name__ == "__main__":
    main()
