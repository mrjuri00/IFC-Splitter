import ifcopenshell
from shutil import copyfile
import os



##### In Split_IfcBuildingStorey.py wird die Patch-Funktion definiert, die ein IFC in einzelne Stockwerke splittet und in einzelnen Dateien abspeichert.

### Hilfsfunktion, um zu prüfen, ob ein IfcSpace in einem Stockwerk ist. Gibt True oder False zurück.
def is_space_in_storey(space, target_storey):
    for relDefines in space.IsDefinedBy:
        if relDefines.is_a("IfcRelDefinesByProperties"):
            propertySet = relDefines.RelatingPropertyDefinition
            if propertySet.is_a("IfcPropertySet"):
                for property in propertySet.HasProperties:
                    if property.is_a("IfcPropertySingleValue") and property.Name == "Geschoss":
                        space_storey = property.NominalValue.wrappedValue
                        state = space_storey == target_storey.Name
                        #print(space.Name, space_storey, target_storey.Name, state)
                        return state


### Hilfsfunktion, um zu prüfen, ob ein Element in einem Stockwerk ist. Gibt True oder False zurück.
def is_in_storey(element, storey):
    return element.ContainedInStructure and element.ContainedInStructure[0].RelatingStructure.is_a('IfcBuildingStorey') and element.ContainedInStructure[0].RelatingStructure.GlobalId == storey.GlobalId


### Patch-Funktion
def patch(input_file_path, output_path, export_storeys, callback_function, progressbar, app):

    # Öffne die IFC-Datei
    file = ifcopenshell.open(input_file_path)
    
    # Hole alle Stockwerke
    storeys = file.by_type('IfcBuildingStorey')
    
    # Anzahl aller Geschosse für Progressbar
    total_storeys = len(storeys)

    # Gehe durch jedes Stockwerk
    for index, storey in enumerate(storeys):

        # Prüfe, ob das Stockwerk exportiert werden soll
        if storey.Name in export_storeys:

            # Erstelle den Ausgabedateipfad
            dest_filename = '{}-{}.ifc'.format(index, storey.Name)
            dest_file_path = os.path.join(output_path, dest_filename)

            copyfile(input_file_path, dest_file_path)

            old_ifc = ifcopenshell.open(dest_file_path)
            new_ifc = ifcopenshell.file(schema=file.schema)

            # Hole Elemente abhängig vom Schema
            elements = old_ifc.by_type('IfcProject') + old_ifc.by_type('IfcProduct') if file.schema == 'IFC2X3' else old_ifc.by_type('IfcContext') + old_ifc.by_type('IfcProduct')

            inverse_elements = []

            # Gehe durch jedes Element und füge sie dem neuen IFC hinzu
            for element in elements:

                if element.is_a('IfcElement') and not is_in_storey(element, storey):
                    element.Representation = None
                    continue

                if element.is_a('IfcElement'):
                    styled_rep_items = [i for i in old_ifc.traverse(element) if i.is_a('IfcRepresentationItem') and i.StyledByItem]
                    for i in styled_rep_items:
                        new_ifc.add(i.StyledByItem[0])
                
                new_ifc.add(element)
                inverse_elements.extend(old_ifc.get_inverse(element))

            # Füge inverse Elemente hinzu
            for inverse_element in inverse_elements:
                new_ifc.add(inverse_element)

            # Entferne Elemente, die nicht im Stockwerk sind
            for element in new_ifc.by_type('IfcElement'):
                if not is_in_storey(element, storey):
                    new_ifc.remove(element)

            # Entferne IfcSpaces, die nicht im Stockwerk sind
            for space in new_ifc.by_type("IfcSpace"):
                if not is_space_in_storey(space, storey):
                    new_ifc.remove(space)

            # Soll auch die Storeys entfernen.. funktioniert noch nicht.
            """
            for i in storeys:
                print(storeys)
                if i == storey:
                    print(f"{i.Name} wird in Ruhe gelassen.")
                    continue
                else:
                    print(f"{i.Name} wird entfernt.")
                    new_ifc.remove(i)
            """
            
            # Speichere die neue IFC-Datei im Ausgabepfad
            new_ifc.write(dest_file_path)

            # Text im GUI, welche IFCs erstellt wurden
            callback_function(storey.Name)

            # Progressbar im GUI
            progressbar.set((index + 1) / total_storeys)
            app.update()

    progressbar.set(1)



### Main-Methode
if __name__ == "__main__":
    
    input_file_path = "C:\\Users\\jurij\\OneDrive - Hochschule Luzern\\Semester 3\\DC_SCRIPT\\Input\\ARC_Modell_NEST_230328.ifc"
    output_path = "C:\\Users\\jurij\\OneDrive - Hochschule Luzern\\Semester 3\\DC_SCRIPT\\Output"
    export_storeys = ['OG02', 'OG03', 'OG04']

    ### Mock-Funktionen um GUI-Funktionen zu simulieren
    def mock_callback_function(storey_name):
        print(f"{storey_name}.ifc has been generated!")

    class MockProgressBar:
        def set(self, value):
            print(f"ProgressBar Wert: {value}")

    class MockApp:
        def update(self):
            pass

    mock_progress_bar = MockProgressBar()
    mock_app = MockApp()

    patch(input_file_path, output_path, export_storeys, mock_callback_function, mock_progress_bar, mock_app)