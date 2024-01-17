import ifcopenshell
import os




##### Im ifc_analyzer.py werden die relevanten Informationen des eingelesenen IFCs fürs GUI ausgelesen und verarbeitet.

### Analysiert IFC und gibt ifc_name, ifc_schema, ifc_size aus.
def ifc_analyze(input_file_path):

    file = ifcopenshell.open(input_file_path)
    ifc_name = os.path.basename(input_file_path)
    ifc_schema = file.schema
    ifc_size = int(os.path.getsize(input_file_path) / 1024)

    return ifc_name, ifc_schema, ifc_size


### Analysiert IFC und gibt storey_names aus, das ist eine Liste aller IfcBuildingStoreys.
def ifcBuildingStorey_analyze(input_file_path):

    file = ifcopenshell.open(input_file_path)
    ifc_BuildingStoreys = file.by_type("IfcBuildingStorey")

    storey_names = [storey.Name for storey in ifc_BuildingStoreys if storey.Name is not None]

    return storey_names


### Analysiert IFC und gibt building_names aus, das ist eine Liste aller IfcBuildings.
def ifcBuilding_analyze(input_file_path):

    file = ifcopenshell.open(input_file_path)
    ifc_Buildings = file.by_type("IfcBuilding")

    building_names = [building.Name for building in ifc_Buildings if building.Name is not None]

    return building_names


### Analysiert IFC und gibt site_names aus, das ist eine Liste aller IfcSites.
### Wird in der aktuellen Version nicht benötigt.
"""
def ifcSite_analyze(input_file_path):

    file = ifcopenshell.open(input_file_path)
    ifc_Sites = file.by_type("IfcSite")

    site_names = [site.Name for site in ifc_Sites if site.Name is not None]

    return site_names
"""


### Analysiert IFC und gibt keys_list aus, das sind alle Elementtypen, die im IFC vorkommen.
def ifcElement_analyze(input_file_path):
    
    file = ifcopenshell.open(input_file_path)
    ifc_Products = file.by_type("IfcProduct")

    # Erstellen eines Dictionaries, um IfcProducts nach Typ zu organisieren
    ifc_Products_by_type = {}
    for product in ifc_Products:
        product_type = product.is_a()
        if product_type not in ifc_Products_by_type:
            ifc_Products_by_type[product_type] = []
        ifc_Products_by_type[product_type].append(product.Name if product.Name else "Unnamed")

    # Erstellen einer Liste aller Keys im Dictionary
    keys_list = list(ifc_Products_by_type.keys())
    keys_list.sort()

    keys_to_remove = ("IfcBuilding", "IfcBuildingStorey", "IfcSite")
    for element in keys_to_remove:
        keys_list.remove(element)

    return keys_list



### Main-Methode
if __name__ == "__main__":

    input_file_path = "C:\\Users\\jurij\\OneDrive - Hochschule Luzern\\Semester 3\\DC_SCRIPT\\Semesterprojekt\\Input\\0032_731_ARC_LTM_T01_3DXX_31.ifc"
    output_path = "C:\\Users\\jurij\\OneDrive - Hochschule Luzern\\Semester 3\\DC_SCRIPT\\Semesterprojekt\\Output"

    ifc_name, ifc_schema, ifc_size = ifc_analyze(input_file_path)

    print(f"IFC-Name: {ifc_name}")
    print(f"IFC-Schema: {ifc_schema}")
    print(f"IFC-Größe: {ifc_size} kB")

    print()
    print("========================")
    print()

    storey_names = ifcBuildingStorey_analyze(input_file_path)
    print(f"Geschossnamen: {storey_names}")

    building_names = ifcBuilding_analyze(input_file_path)
    print(f"Gebäudenamen: {building_names}")

    element_names = ifcElement_analyze(input_file_path)
    print(f"Elementnamen: {element_names}")