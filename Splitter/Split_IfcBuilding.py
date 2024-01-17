import ifcopenshell
from shutil import copyfile
import os




##### In Split_IfcBuilding.py wird die Patch-Funktion definiert, die ein IFC in einzelne Gebäude splittet und in einzelnen Dateien abspeichert.

### Hilfsfunktion, um zu prüfen, ob ein Element in einem Gebäude ist. Gibt True oder False zurück.
def is_in_building(element, building, checked_elements=None):
    if checked_elements is None:
        checked_elements = set()

    if element.id() in checked_elements:
        return False

    checked_elements.add(element.id())

    if hasattr(element, 'ContainedInStructure') and element.ContainedInStructure:
        for structure in element.ContainedInStructure:
            if structure.RelatingStructure.is_a('IfcBuildingStorey'):
                storey = structure.RelatingStructure
                if is_storey_in_building(storey, building):
                    return True

    if hasattr(element, 'HasAssociations') and element.is_a('IfcOpeningElement') or element.is_a('IfcStairFlight') or element.is_a('IfcPlate') or element.is_a('IfcMember'):
        for association in element.HasAssociations:
            if association.RelatedObjects:
                for associated_element in association.RelatedObjects:
                    if is_in_building(associated_element, building, checked_elements):
                        return True

    return False


### Hilfsfunktion, um zu prüfen, ob ein IfcBuildingStorey in einem Gebäude ist. Gibt True oder False zurück. 
def is_storey_in_building(storey, building):
    if storey.Decomposes:
        for decompose in storey.Decomposes:
            if decompose.RelatingObject.is_a('IfcBuilding'):
                return decompose.RelatingObject.GlobalId == building.GlobalId
    return False


### Patch-Funktion,
def patch(input_file_path, output_path, export_buildings, callback_function, progressbar, app):

    # Öffne die IFC-Datei
    file = ifcopenshell.open(input_file_path)

    # Hole alle Gebäude
    buildings = file.by_type('IfcBuilding')

    # Anzahl aller Gebäude für Progressbar
    total_buildings = len(buildings)

    # Gehe durch jedes Gebäude
    for index, building in enumerate(buildings):

        # Prüfe, ob das Gebäude exportiert werden soll
        if building.Name in export_buildings:

            # Erstelle den Ausgabedateipfad
            dest_filename = '{}-{}.ifc'.format(index, building.Name)
            dest_file_path = os.path.join(output_path, dest_filename)

            copyfile(input_file_path, dest_file_path)

            old_ifc = ifcopenshell.open(dest_file_path)
            new_ifc = ifcopenshell.file(schema=file.schema)

            # Hole Elemente abhängig vom Schema
            elements = old_ifc.by_type('IfcProject') + old_ifc.by_type('IfcProduct') if file.schema == 'IFC2X3' else old_ifc.by_type('IfcContext') + old_ifc.by_type('IfcProduct')

            inverse_elements = []

            # Gehe durch jedes Element und füge sie dem neuen IFC hinzu
            for element in elements:

                if element.is_a('IfcElement') and not is_in_building(element, building):
                    element.Representation = None
                    continue

                new_ifc.add(element)
                inverse_elements.extend(old_ifc.get_inverse(element))

            # Füge inverse Elemente hinzu
            for inverse_element in inverse_elements:
                new_ifc.add(inverse_element)

            # Entferne Elemente, die nicht im Gebäude sind
            for element in new_ifc.by_type('IfcElement'):
                if not is_in_building(element, building):
                    new_ifc.remove(element)

            # Speichere die neue IFC-Datei im Ausgabepfad
            new_ifc.write(dest_file_path)
            print(f'{building.Name}.ifc wurde erstellt!')

            # Text im GUI, welche IFCs erstellt wurden
            callback_function(building.Name)

            # Progressbar im GUI
            progressbar.set((index + 1) / total_buildings)
            app.update()

    progressbar.set(1)


### Main-Methode
if __name__ == "__main__":

    input_file_path = "C:\\Users\\jurij\\OneDrive - Hochschule Luzern\\Semester 3\\DC_SCRIPT\\Semesterprojekt\\Input\\ARC_Modell_NEST_230328.ifc"
    output_path = "C:\\Users\\jurij\\OneDrive - Hochschule Luzern\\Semester 3\\DC_SCRIPT\\Semesterprojekt\\Output"
    export_buildings = ['GA']

    ### Mock-Funktionen um GUI-Funktionen zu simulieren
    def mock_callback_function(building_name):
        print(f"{building_name}.ifc has been generated!")

    class MockProgressBar:
        def set(self, value):
            print(f"ProgressBar Wert: {value}")

    class MockApp:
        def update(self):
            pass
    
    patch(input_file_path, output_path, export_buildings)