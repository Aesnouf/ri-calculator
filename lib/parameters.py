import os

# Used for extracting data from simapro lci
COMPARTMENTS = ('Resources',
                'Emissions to air',
                'Emissions to water',
                'Emissions to soil')

NEW_NAMES = ('Raw',
             'Air',
             'Water',
             'Soil')

# List of standardized methods composing simapro_standardized_methods.xlsx
METHODS_LIST = ["ILCD_Mid+_V1.05",
                "ReCiPe_Mid_E_V1.11", "ReCiPe_Mid_H_V1.11", "ReCiPe_Mid_I_V1.11",
                "ReCiPe_End_E_V1.11_Damage", "ReCiPe_End_H_V1.11_Damage", "ReCiPe_End_I_V1.11_Damage",
                "ReCiPe_End_E_V1.11_End_", "ReCiPe_End_H_V1.11_End_", "ReCiPe_End_I_V1.11_End_",
                "CML-IA_baseline_V3.02",
                "TRACI_2.1_V1.02",
                "Impact_2002+_V2.12",
                "Eco_Scarc_2013_V1.01",
                "EPD_2013_V1.01", "EPS_2000_V2.08", "EDIP_2003_V1.05",
                "USEtox_(consensus_only)_V1.04", "USEtox_(recommended+interim)_V1.04",
                "IPCC_2013_GWP_100a",
                "BEES_V4.05",
                "Cumul_Energy_Demand_V1.09", "Eco_Footprint_V1.01",
                "GHG_Prot_V1.01"]

# Files paths
BASEDIR = os.path.dirname(os.path.dirname(__file__))

GMEAN = os.path.join(BASEDIR, "data/ecoinvent_geometric_mean.xlsx")
METHODS = os.path.join(BASEDIR, "data/simapro_standardized_methods.xlsx")
