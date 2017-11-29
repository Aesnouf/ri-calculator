**RI Calculator**

This program allows to apply the RI methodology developed by Esnouf, A et al. (see reference below).
RIs are indexes of the relevance of LCIA methods or impact categories to study one or several system LCIs  (or aggregated LCIs) in the global context of their database. This first version of the program is only compatible with simapro export and LCI modeled with ecoinvent 3.1 database version “allocation at the point of substitution”.
The version of the analyzed LCIA methods can be found in methods.txt. LCIA methods are provided with the Simapro nomenclature. The standardization of LCIA method has already been applied.

**Usage**

RI_Calculator.py is the main script where directories and excel LCI names have to be specified. 
Running this program will use the different python files supplied in the package.

Using lci_formatting.py, LCIs are formatted (to modify their fromat from the simapro export format) and standardized with the geometric means of the ecoinvent 3.1 dimensions.
The impact category RIs are then determined (ri_calculation.py).

To obtain the LCIA method RIs, methods have to be formatted to organize and orthogonalize them (method_formatting.py).
Then, RIs of LCIA methods are determined (ri_calculation.py).

The generated RIs results are stored as excel file in the second specified directory.

**Reference:**
Esnouf, A et al. _Representativeness of environmental impact assessmentmethods regarding Life Cycle Inventories_,
Sci Total Environ (2017), https://doi.org/10.1016/j.scitotenv.2017.10.102

_This project is licensed under the terms of the MIT license._