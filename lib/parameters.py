import os

LCIS = ["drive_100_km_chaeto_2", "drive_100_km_chaeto_3", "cellulase",
        "simapro_electricity, high voltage_market_CN",
        "simapro_electricity, high voltage_market_FR",
        "simapro_electricity, high voltage_market_DE",
        "simapro_electricity, high voltage_market_NPCC"]

# TODO: Reorganize files and folders
BASE_DIR = "C:/Users/Esnoufa/Documents/Python_data"
LCI_DIR = os.path.join(BASE_DIR, "lci_from_simapro")
ROSETTA = os.path.join(BASE_DIR, "from_simapro/rosetta_simapro8X_ecoinvent32_modified.xlsx")
