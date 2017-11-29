"""
The program determines the Representativeness Indexes of LCIA methods and their impact categories for one or several LCIs.

The program allows to apply the RI methodology developed by Esnouf, A et al. (see link in README.md).
RIs are indexes of the relevance of LCIA methods or impact categories to study one or several system (or aggregated
version) LCIs in the global context of their database. This first version of the program is only compatible with simapro
export and LCI modeled with ecoinvent 3.1 database version “allocation at the point of substitution”.
The directory of the folder where the excel files are stored have to be specified, as well as the names of the simapro
export files. When running the program, two excel files containing RIs results (for methods and impact categories)
are generated and stored in the specified directory.

Author: Antoine Esnouf
Contributor: Gustave Coste
Contact: antoine.esnouf@inra.fr
Date: November 2017
"""
# TODO: Write a brief description of the program in the above dosctring and copy it in README.md

import os

import pandas as pd

from lib.lci_formatting import gather_lcis, standardize_lci
from lib.ri_calculation import representativeness_index_per_category, representativeness_index_per_method
from lib.methods_formatting import filter_methods
from lib.parameters import METHODS_LIST, GMEAN, METHODS

############################################### VALUES TO UPDATE #######################################################

# SIMAPRO SYSTEM LCI FILES HAVE TO BE EXPORTED WITH THE OPTION "Detail" and "per categories"

# Directory where are stored the simapro lcis
LCIS_DIR = "Path/to/the/lcis/directory"

# Names of the simapro lci files (without file extension)
LCIS = ['lci1', 'lci2', '...', ]

# Directory to export the results
EXPORT_DIR = "Path/to/export/directory"

# Names of the methods to study. Availaible methods names can be found in methods.txt.
# Comment the line to use every methods
#METHODS_NAMES = ['method1', 'method2', '...', ]


# Uncomment and change these if you want personalized filenames, defaults are ri_category.xlsx and ri_methods.xlsx
# RI_CATEGORY_FILENAME = "your_filename"
# RI_METHODS_FILENAME = "your_other_filename"

########################################################################################################################

# RI CALCULATION
def main():
    gmean = pd.io.excel.read_excel(GMEAN)
    methods = pd.io.excel.read_excel(METHODS)

    lcis = gather_lcis(LCIS, LCIS_DIR)
    lcis = lcis.reindex(index=methods.index)
    standardized_lci = standardize_lci(lcis, gmean)
    ri_cat = representativeness_index_per_category(methods, standardized_lci)

    try:
        methods_names = METHODS_NAMES
    except NameError:
        methods_names = METHODS_LIST

    methods_to_study = filter_methods(methods, methods_names)
    ri_methods = representativeness_index_per_method(methods_to_study, methods_names, standardized_lci)

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
