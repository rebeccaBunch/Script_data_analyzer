# Importa las bibliotecas necesarias
import os
import streamlit as st
import pandas as pd
from io import BytesIO

from LLM_use import CharacterExtractor
from data_extractor import pdf_extract_text_per_page, save_scenes_to_excel, save_scenes_to_excel_with_characters
from scene_separator import Scene_separator

# def get_script_file():
#     """
#     Solicita al usuario que introduzca el nombre del guión a analizar a través de una barra de búsqueda en la parte superior de la aplicación Streamlit.
#     Si el archivo no existe, muestra un error, de lo contario crea un archivo en la carpeta guiones con el nombre del guión y la fecha actual
#     """
#     script_file_name = st.text_input("Inserte el nombre del archivo")
#     if(script_file_name):
#         script_file_name += '.pdf'
#         # if not script_file_name.match('*.pdf'):
#         #     st.error("El archivo debe ser un pdf de la carpeta guiones")

#         # Usa os.listdir para obtener una lista de todos los archivos en la carpeta 'guiones'
#         for filename in os.listdir('guiones'):
#             # Si el nombre del archivo coincide con el nombre dado, devuelve el nombre del archivo
#             if filename == script_file_name:
#                 return filename

#         # Si no se encuentra ningún archivo que coincida, devuelve None
#         if(script_file_name):
#             st.error("Ese archivo no se encuentra en la carpeta guiones")

# # Solicita al usuario que introduzca el nombre del guión y devuelve el nombre del archivo en caso de que exista, en caso contrario lanza excepción
# script_file_name = get_script_file()

# # Si se ha introducido un nombre, crea en la carpeta encabezados un archivo con el nombre del guión más la fecha actual 
# if script_file_name:
#     pages_text = pdf_extract_text_per_page(os.path.join('guiones', script_file_name))
#     sep = Scene_separator()
#     scenes = sep(pages_text)
#     extractor = CharacterExtractor()
#     result = 1
#     while result:
#         try:
#             script_characters = extractor.extract_characters(scenes,11)
#             extractor.set_continuity(scenes,11)
#             result = 0
#         except:
#             st.error("Hubo un error con el LLM, por favor cambie el api key o revise la vpn")
            
#     save_scenes_to_excel_with_characters(scenes, script_file_name, script_characters)


def process_script_file(uploaded_file):

    # Check if the uploaded file is a PDF
    if uploaded_file.type != "application/pdf":
        st.error("El archivo no es un PDF y no puede ser analizado.")
        return None, None
    # Read the uploaded file content
    file_content = uploaded_file.read()
    
    # Process the file content
    pages_text = pdf_extract_text_per_page(BytesIO(file_content))
    sep = Scene_separator()
    scenes = sep(pages_text)
    try:
            key = st.secrets["api_key"]["gemini_api_key1"]
            extractor = CharacterExtractor(key)
            script_characters = extractor.extract_characters(scenes, 11)
            extractor.set_continuity(scenes, 11)
    except:
          try:
                key = st.secrets["api_key"]["gemini_api_key2"]
                extractor = CharacterExtractor(key)
                script_characters = extractor.extract_characters(scenes, 11)
                extractor.set_continuity(scenes, 11)
          except Exception as e:
                  st.error(f"{e}")
    
    # Save the scenes to an Excel file in memory
    excel_buffer = BytesIO()
    script_file_name = uploaded_file.name.rsplit('.', 1)[0]  # Remove the .pdf extension
    save_scenes_to_excel_with_characters(scenes, script_file_name, script_characters, excel_buffer)
    
    return excel_buffer.getvalue(), script_file_name + '.xlsx'

st.title("Script Analysis App")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Process the uploaded file
    excel_data, excel_name = process_script_file(uploaded_file)
    
    # Provide a download button for the generated Excel file
    st.download_button(
        label="Download Processed Excel File",
        data=excel_data,
        file_name=excel_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )




