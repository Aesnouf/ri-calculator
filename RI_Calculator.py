"""
This program determines the Representativeness Indexes of LCIA methods and their impact categories for one or several LCIs.

This program allows to apply the RI methodology developed by Esnouf, A et al. (see reference below) within the Life Cycle Assessment methodology (LCA).
RIs are indexes of the relevance of Life Cycle Impact Assessment methods (LCIA) or impact categories to study one or several system Life Cycle Inventories (or aggregated LCIs) in the global context of their database. This first version of the program is only compatible with simapro exports and LCIs modeled with ecoinvent 3.1 database version “allocation at the point of substitution”.
The version of the analyzed LCIA methods can be found in *methods.txt*. LCIA methods are provided with the Simapro nomenclature. The standardization of LCIA method has already been applied.

RIs for a LCIA method and for each of its impact categories can be obtained.
RIs from orthogonalized impact categories are also calculated to avoid over/underrepresentation of LCI when several impact categories are correlated.

**Usage**

*RI_Calculator.py* is the main script where directories and excel LCI names have to be specified by the user .
Running this script will use the different python modules supplied in the package. Needed external python packages are listed in requirements.txt.

The generated RIs results are stored as excel file in the second specified directory.

**Implementation**

Using *lci_formatting.py*, LCIs are formatted (to modify their format from the simapro export format) and standardized with the geometric means of the ecoinvent 3.1 dimensions.
The impact category RIs are then determined (*ri_calculation.py*).

To obtain the LCIA method RIs, methods have to be formatted to organize and orthogonalize them (*method_formatting.py*).
Then, RIs of LCIA methods are determined (*ri_calculation.py*).

**Reference:**
Esnouf, A et al. _Representativeness of environmental impact assessmentmethods regarding Life Cycle Inventories_,
Sci Total Environ (2017), https://doi.org/10.1016/j.scitotenv.2017.10.102

_This project is licensed under the terms of the MIT license._

Author: Antoine Esnouf
Contributor: Gustave Coste
Contact: antoine.esnouf@inra.fr
"""

import os

import pandas as pd

from lib.lci_formatting import gather_lcis, standardize_lci
from lib.ri_calculation import representativeness_index_per_category, representativeness_index_per_method, \
    representativeness_index_per_orthogonalized_category
from lib.methods_formatting import filter_methods
from lib.parameters import METHODS_LIST, GMEAN, METHODS

############################################### VALUES TO UPDATE #######################################################

# SIMAPRO SYSTEM LCI FILES HAVE TO BE EXPORTED WITH THE OPTIONS "Detail" and "per categories"

# Directory where are stored the simapro lcis
LCIS_DIR = "Path/to/the/lcis/directory"

# Names of the simapro lci files (without file extension)
LCIS = ['lci1', 'lci2', '...', ]

# Directory to export the results
EXPORT_DIR = "Path/to/export/directory"


# Names of the methods to study. Availaible methods names can be found in methods.txt.
# Comment the line to use every methods
# METHODS_NAMES = ['method1', 'method2', '...', ]


# Uncomment and change these if you want personalized filenames, defaults are ri_category.xlsx, ri_category_ortho.xlsx
# and ri_methods.xlsx
# RI_CATEGORY_FILENAME = "your_filename"
# RI_CATEGORY_ORTHO_FILENAME = "your_other_filename"
# RI_METHODS_FILENAME = "yet_another_filename"

########################################################################################################################

# RI CALCULATION
def main():
    gmean = pd.io.excel.read_excel(GMEAN)
    methods = pd.io.excel.read_excel(METHODS)

    lcis = gather_lcis(LCIS, LCIS_DIR)
    lcis = lcis.reindex(index=methods.index)
    standardized_lci = standardize_lci(lcis, gmean)
    ri_cat = representativeness_index_per_category(standardized_methods=methods,
                                                   standardized_lcis=standardized_lci)

    try:
        methods_names = METHODS_NAMES
    except NameError:
        methods_names = METHODS_LIST

    methods_to_study = filter_methods(methods, methods_names)
    ri_cat_ortho = representativeness_index_per_orthogonalized_category(standardized_methods=methods_to_study,
                                                                        method_names=methods_names,
                                                                        standardized_lcis=standardized_lci)
    ri_methods = representativeness_index_per_method(standardized_methods=methods_to_study,
                                                     methods_names=methods_names,
                                                     standardized_lcis=standardized_lci)

    # Exporting data
    try:
        ri_category_filename = RI_CATEGORY_FILENAME + ".xlsx"
    except NameError:
        ri_category_filename = "ri_category.xlsx"

    try:
        ri_category_ortho_filename = RI_CATEGORY_ORTHO_FILENAME + ".xlsx"
    except NameError:
        ri_category_ortho_filename = "ri_category_ortho.xlsx"

    try:
        ri_methods_filename = RI_METHODS_FILENAME + ".xlsx"
    except NameError:
        ri_methods_filename = "ri_methods.xlsx"

    pd.DataFrame.to_excel(ri_cat, os.path.join(EXPORT_DIR, ri_category_filename))
    pd.DataFrame.to_excel(ri_cat_ortho, os.path.join(EXPORT_DIR, ri_category_ortho_filename))
    pd.DataFrame.to_excel(ri_methods, os.path.join(EXPORT_DIR, ri_methods_filename))


if __name__ == "__main__":
    main()
