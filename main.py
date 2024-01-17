import os
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import Analyzer
import Splitter



##### In der main.py Datei wird das ganze GUI definiert und die Analyzer- und Splitter-Funktionen ausgeführt.

### Globale Variablen
selected_file_path = ""
selected_output_folder = ""
split_setting = "IfcBuildingStorey"
file_path = ""
selected_values = []
checkboxes = {}
current_label_y_position = 80


### Farben, Schriftarten und Maße
color_blue_1 = "#023047"
color_blue_2 = "#2C5E77"
color_white = "#FFFFFF"
color_orange = "#FB8500"
glb_font = "Roboto Mono"
glb_width = 1000
glb_height = 600
header_heigth = 120



##### Utility-Funktionen

### Output Folder Abfrage
def select_output_folder():

    global selected_output_folder
    selected_output_folder = filedialog.askdirectory()


### Checkbox Auswahl Abfrage
def process_checkbox_selection():

    global selected_values

    selected_values = []
    for value, var in checkboxes.items():
        if var.get():
            selected_values.append(value)


### Generieren der Checkboxen
def create_checkboxes(checkbox_values):

    checkbox_frame.place(relx=0, rely=0, x=20, y=100, anchor="nw")

    for widget in checkbox_frame.winfo_children():
        widget.destroy()

    row = 0
    column = 0
    max_columns = 4  # Max Anzahl von Spalten
    spaltenbreite = 100  # Feste Breite für jede Spalte

    for i, value in enumerate(checkbox_values):
        # Erstellen einer Variable für den Zustand der Checkbox
        var = tk.BooleanVar()

        # Erstellen der Checkbox
        chkbox = ctk.CTkCheckBox(
            checkbox_frame,
            font=(glb_font, 16),
            text=value,
            border_color=color_orange,
            hover_color=color_orange,
            fg_color=color_orange,
            text_color=color_orange,
            variable=var
        )

        # Platzieren der Checkbox in der aktuellen Zeile und Spalte
        chkbox.grid(row=row, column=column, sticky="w", padx=10, pady=5)

        # Speichern der Checkbox und ihrer Zustandsvariable
        checkboxes[value] = var

        # Nach jeder 5. Checkbox, erhöhe die Spalte und setze die Zeile zurück
        if (i + 1) % 5 == 0:
            column += 1
            row = 0
        else:
            row += 1

    # Konfigurieren der Spaltenbreiten
    for col in range(max_columns):
        checkbox_frame.columnconfigure(col, minsize=spaltenbreite)


def add_storey_created_message(storey_name):
    global current_label_y_position
    # Erstellen Sie hier das Label mit der Nachricht
    new_label = ctk.CTkLabel(
        bg,
        font=(glb_font, 16),
        text_color=color_orange,
        text=f"{storey_name}.ifc has been generated!"
    )
    new_label.place(x=30, y=current_label_y_position)
    current_label_y_position += 30  # Anpassen für das nächste Label

    app.update()



##### Event-Handler-Funktionen

### IFC Auswahl
def select_ifc_file():

    loading_label.place(relx=0.5, rely=0.7, anchor="n")

    global file_path
    file_path = filedialog.askopenfilename(
        filetypes=[("IFC Files", "*.ifc"), ("All Files", "*.*")]
    )
    
    if file_path:
        try:

            btn_file.place_forget()
            loading_label.place_forget()

            second_page()

        except:

            fehler_label.place(relx=0.5, rely=0.5, anchor="n")
    
    else:

        btn_file.place_forget()
        loading_label.place_forget()

        fehler_label.place(relx=0.5, rely=0.5, anchor="n")


### Generieren der Hauptseite
def second_page():

    ifc_name, ifc_schema, ifc_size = Analyzer.ifc_analyzer.ifc_analyze(file_path)

    ifc_name_label.configure(text=ifc_name)
    ifc_schema_label.configure(text=ifc_schema)
    ifc_size_label.configure(text=f"{ifc_size} kB")
    ifc_detail_frame.place(relx=0, rely=1, x=30, y=-25, anchor="sw")

    split_by_label.place(relx=0, rely=0, x=30, y=30, anchor="nw")
    dropdown_menu.place(relx=0, rely=0, x=130, y=30, anchor="nw")  # Richtige Positionierung

    # Standard-Checkboxen anzeigen
    initial_checkbox_values = Analyzer.ifc_analyzer.ifcBuildingStorey_analyze(file_path)
    create_checkboxes(initial_checkbox_values)

    split_button.place(relx=1, rely=1, x=-30, y=-30, anchor="se")
 

### Dropdown Menü Auswahl Änderung
def on_dropdown_selection(selected_option):

    checkbox_frame.place_forget()

    global split_setting

    if selected_option == "IfcBuildingStorey":
        new_checkbox_values = Analyzer.ifc_analyzer.ifcBuildingStorey_analyze(file_path)
        split_setting = "IfcBuildingStorey"

    elif selected_option == "IfcBuilding":
        new_checkbox_values = Analyzer.ifc_analyzer.ifcBuilding_analyze(file_path)
        split_setting = "IfcBuilding"

    elif selected_option == "IfcElement":
        new_checkbox_values = Analyzer.ifc_analyzer.ifcElement_analyze(file_path)
        split_setting = "IfcElement"
        
    else:
        new_checkbox_values = []
        split_setting = "False"

    create_checkboxes(new_checkbox_values)


### Split-Funktion ausführen
def split():

    select_output_folder()

    if not selected_output_folder:
        error_message()
    
    else:
        process_checkbox_selection()
        hide_gui_elements_after_split()
        

        if split_setting == "IfcBuildingStorey":
            Splitter.Split_IfcBuildingStorey.patch(file_path, selected_output_folder, selected_values, add_storey_created_message, progress, app)
        
        elif split_setting == "IfcBuilding":
            Splitter.Split_IfcBuilding.patch(file_path, selected_output_folder, selected_values, add_storey_created_message, progress, app)

        elif split_setting == "IfcElement":
            Splitter.Split_IfcElement.patch(file_path, selected_output_folder, selected_values, add_storey_created_message, progress, app)

    show_button.place(relx=1, rely=1, x=-30, y=-30, anchor="se")


# Versteckt Checkboxen, Split_by_Label, Dropdown_Menu und Split_Button. Platziert die Progressbar.
def hide_gui_elements_after_split():
    
    checkbox_frame.place_forget()
    split_by_label.place_forget()
    dropdown_menu.place_forget()
    split_button.place_forget()

    progress.place(relx=0.5, rely=0.1, anchor="n")
    app.update()


# Öffnet den Speicherort und schliesst die App.
def show():
    os.startfile(selected_output_folder)
    app.destroy()


def error_message():
    checkbox_frame.place_forget()
    split_by_label.place_forget()
    dropdown_menu.place_forget()
    split_button.place_forget()
    ifc_detail_frame.place_forget()

    fehler_label.place(relx=0.5, rely=0.5, anchor="n")


##### GUI-Layout-Definitionen  

app = ctk.CTk()
app.geometry(f"{glb_width}x{glb_height}")
app.title("IFC Splitter")
app.configure(bg="blue")
app.iconbitmap("logo.ico")



### Startseite

# Header
header = ctk.CTkFrame(
    app,
    width=glb_width,
    height=header_heigth,
    fg_color=color_blue_2,
    corner_radius=0
    )
header.pack(fill='both', expand=True)


# Titel
title = ctk.CTkLabel(
    header,
    text="IFC Splitter",
    text_color=color_white,
    font=(glb_font, 48)
    )
title.place(relx=0.0, rely=0.5, x=30, anchor="w")


# Credentials
cred = ctk.CTkLabel(
    header,
    text="V1.0 - by Juri Jerg",
    text_color=color_white,
    font=(glb_font, 16)
    )
cred.place(relx=1.0, rely=0.0, x=-10, y=10, anchor="ne")


# Background
bg = ctk.CTkFrame(
    app,
    fg_color=color_blue_1,
    width=glb_width,
    height=glb_height-header_heigth,
    corner_radius=0
    )
bg.pack(fill='both', expand=True)


# Button - IFC Auswahl
btn_file = ctk.CTkButton(
    bg,
    width=250,
    height=60,
    corner_radius=90,
    fg_color=color_orange,
    hover_color=color_blue_2,
    text="Choose your File",
    font=(glb_font, 16),
    command=lambda: select_ifc_file()
    )
btn_file.place(relx=0.5, rely=0.5, anchor="n")


# Loading Label
loading_label = ctk.CTkLabel(
    bg,
    text="loading...",
    text_color=color_white,
    font=(glb_font, 16)
)



### Hauptseite

# IFC-Details Frame
ifc_detail_frame = ctk.CTkFrame(
    bg,
    width=250,
    height=150,
    fg_color=color_blue_1,
    corner_radius=0
    )


# IFC-Name-Label
ifc_name_label = ctk.CTkLabel(
    ifc_detail_frame,
    text="test",
    font=(glb_font, 26),
    text_color=color_orange
    )
ifc_name_label.grid(row=0, column=0, sticky="w", pady=0)


# IFC-Schema-Label
ifc_schema_label = ctk.CTkLabel(
    ifc_detail_frame,
    text="test",
    font=(glb_font, 16),
    text_color=color_orange
    )
ifc_schema_label.grid(row=1, column=0, sticky="w", pady=0)


# IFC-Size-Label
ifc_size_label = ctk.CTkLabel(
    ifc_detail_frame,
    text="test",
    font=(glb_font, 16),
    text_color=color_orange
    )
ifc_size_label.grid(row=2, column=0, sticky="w", pady=0)


# Checkboxen
checkbox_frame = ctk.CTkFrame(
    bg,
    width=800,
    height=300,
    fg_color=color_blue_1,
    corner_radius=0
    )


# Split by Label
split_by_label = ctk.CTkLabel(
    bg,
    text="Split by:",
    text_color=color_orange,
    font=(glb_font, 16),
    )


# Dropdown-Menü
dropdown_options = ["IfcBuildingStorey", "IfcBuilding", "IfcElement"]
dropdown_menu = ctk.CTkComboBox(
    bg,
    width=200,
    fg_color=color_orange,
    border_color=color_orange,
    button_color=color_orange,
    text_color=color_white,
    font=(glb_font, 16),
    values=dropdown_options,
    command=on_dropdown_selection
    )


# Split-Button
split_button = ctk.CTkButton(
    bg,
    width=150,
    height=60,
    corner_radius=90,
    fg_color=color_orange,
    hover_color=color_blue_2,
    text="Split!",
    font=(glb_font, 16),
    command=split
    )


# Show-Button
show_button = ctk.CTkButton(
    bg,
    width=150,
    height=60,
    corner_radius=90,
    fg_color=color_orange,
    hover_color=color_blue_2,
    text="Show!",
    font=(glb_font, 16),
    command=show
    )


# Progress-Bar
progress = ctk.CTkProgressBar(
    bg,
    orientation="horizontal",
    progress_color=color_orange,
    width=glb_width-60,
    )
progress.set(0)


# Fehler-Label
fehler_label = ctk.CTkLabel(
    bg,
    text="Error! Please restart the application.",
    text_color=color_white,
    font=(glb_font, 24)
    )



### Main-Methode
if __name__ == "__main__":
    
    app.mainloop()