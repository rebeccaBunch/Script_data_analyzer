# Importa las bibliotecas necesarias
import os
import streamlit as st
import pandas as pd
import threading 

from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from streamlit.runtime import get_instance


from data_extractor import pdf_extract_text_per_page, save_scenes_to_excel
from scene_separator import Scene_separator

def get_script_file():
    """
    Solicita al usuario que introduzca el nombre del guión a analizar a través de una barra de búsqueda en la parte superior de la aplicación Streamlit.
    Si el archivo no existe, muestra un error, de lo contario crea un archivo en la carpeta guiones con el nombre del guión y la fecha actual
    """
    script_file_name = st.text_input("Inserte el nombre del archivo")
    if(script_file_name):
        script_file_name += '.pdf'
        # if not script_file_name.match('*.pdf'):
        #     st.error("El archivo debe ser un pdf de la carpeta guiones")

        # Usa os.listdir para obtener una lista de todos los archivos en la carpeta 'guiones'
        for filename in os.listdir('guiones'):
            # Si el nombre del archivo coincide con el nombre dado, devuelve el nombre del archivo
            if filename == script_file_name:
                return filename

        # Si no se encuentra ningún archivo que coincida, devuelve None
        if(script_file_name):
            st.error("Ese archivo no se encuentra en la carpeta guiones")

# Solicita al usuario que introduzca el nombre del guión y devuelve el nombre del archivo en caso de que exista, en caso contrario lanza excepción
script_file_name = get_script_file()

# Si se ha introducido un nombre, crea en la carpeta encabezados un archivo con el nombre del guión más la fecha actual 
if script_file_name:
    pages_text = pdf_extract_text_per_page(os.path.join('guiones', script_file_name))
    sep = Scene_separator(["-"], ["-"], ["-"], ["--"], 
                      ["ESC:", "SEC:", "ESCENA:", "ESCENA", "SECUENCIA:", "SECUENCIA"], 
                      ["INT", "EXT", "INT./EXT", "EXT./INT"], 
                      ["DÍA", "DIA", "AMANECER", "MAÑANA", "TARDE", "ATARDECER", "ANOCHECER", "NOCHE", "MADRUGADA", "OCASO", "MÁS TARDE", "ALBA", "TARDE/OCASO", "AL DÍA SIGUIENTE", "MOMENTOS DESPUÉS", "CONTINÚA"])
    scenes = sep(pages_text)
    save_scenes_to_excel(scenes, script_file_name)



