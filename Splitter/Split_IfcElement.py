import ifcopenshell
from shutil import copyfile
import os




##### In Split_IfcElement.py wird die Patch-Funktion definiert, die ein IFC in einzelne IfcElement-Typen splittet und in einzelnen Dateien abspeichert.

### Patch-Funktion
def patch(input_file_path, output_path, element_types, callback_function, progressbar, app):

    # Öffne die IFC-Datei
    file = ifcopenshell.open(input_file_path)

    # Anzahl aller Elemente für Progressbar
    total_elements = len(element_types)

    # Gehe durch jeden Elementtyp in der Liste
    for index, element_type in enumerate(element_types):

        # Erstelle den Ausgabedateipfad
        dest_filename = '{}-{}.ifc'.format(index, element_type)
        dest_file_path = os.path.join(output_path, dest_filename)

        # Kopiere die Ursprungsdatei
        copyfile(input_file_path, dest_file_path)

        # Öffne die kopierte Datei und erstelle eine neue IFC-Datei
        old_ifc = ifcopenshell.open(dest_file_path)
        new_ifc = ifcopenshell.file(schema=file.schema)

        # Hole alle Elemente des spezifizierten Typs
        elements = old_ifc.by_type(element_type)
        for element in elements:
            new_ifc.add(element)

        # Speichere die neue IFC-Datei im Ausgabepfad
        new_ifc.write(dest_file_path)
        
        # Text im GUI, welche IFCs erstellt wurden
        callback_function(element_type)

        # Progressbar im GUI
        progressbar.set((index + 1) / total_elements)
        app.update()

    progressbar.set(1)



### Main-Methode
if __name__ == "__main__":

    input_file = "C:\\Users\\jurij\\OneDrive - Hochschule Luzern\\Semester 3\\DC_SCRIPT\\Semesterprojekt\\Input\\ARC_Modell_NEST_230328.ifc"
    output_folder = "C:\\Users\\jurij\\OneDrive - Hochschule Luzern\\Semester 3\\DC_SCRIPT\\Semesterprojekt\\Output"
    element_types = ["IfcDoor", "IfcWall", "IfcSlab"]

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

    patch(input_file, output_folder, element_types, mock_callback_function, mock_progress_bar, mock_app)