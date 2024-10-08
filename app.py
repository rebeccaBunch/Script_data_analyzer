# Importa las bibliotecas necesarias
import os
import re
import streamlit as st
import pandas as pd
from io import BytesIO

from LLM_use import CharacterExtractor_Gemini
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

def extract_durations(text):
    # Regular expression to find durations in the format a:b
    duration_pattern = re.compile(r'\b(\d+:\d+)\b')
    durations = duration_pattern.findall(text)
    return durations

def get_time_per_scene_from_file(b):
    dur = []
    for i in b:
        tmp = extract_durations(b[i])
        for a in tmp:
            dur.append(a)
    dur.pop(0)
    return dur

def process_script_file(uploaded_file, informe):

    # Check if the uploaded file is a PDF
    if uploaded_file.type != "application/pdf" or (informe.type != "application/pdf" and informe):
        st.error("El archivo no es un PDF y no puede ser analizado.")
        return None, None
    # Read the uploaded file content
    file_content = uploaded_file.read()

    
    # Process the file content
    pages_text = pdf_extract_text_per_page(BytesIO(file_content))
    sep = Scene_separator()
    scenes = sep(pages_text)
    if informe_content:
        informe_content = informe.read()
        time_per_scene = pdf_extract_text_per_page(BytesIO(informe_content))
        times = get_time_per_scene_from_file(time_per_scene)
        for i, scene in enumerate(scenes):
            scene.time = times[i]

    try:
            key = st.secrets["api_keys"]["gemini_api_key1"]
            extractor = CharacterExtractor_Gemini(key)
            script_characters = extractor.extract_characters(scenes, 11)
            extractor.set_continuity(scenes, 11)
    except:
                key = st.secrets["api_keys"]["gemini_api_key2"]
                extractor = CharacterExtractor_Gemini(key)
                script_characters = extractor.extract_characters(scenes, 11)
                extractor.set_continuity(scenes, 11)

    
    # Save the scenes to an Excel file in memory
    excel_buffer = BytesIO()
    script_file_name = uploaded_file.name.rsplit('.', 1)[0]  # Remove the .pdf extension
    extractor.add_notes(scenes,20)
    save_scenes_to_excel_with_characters(scenes, script_file_name, script_characters, excel_buffer)
    
    return excel_buffer.getvalue(), script_file_name + '.xlsx'

def test(uploaded_file, informe):

    # Check if the uploaded file is a PDF
    if uploaded_file.type != "application/pdf" or (informe.type != "application/pdf" and informe):
        st.error("El archivo no es un PDF y no puede ser analizado.")
        return None, None
    # Read the uploaded file content
    file_content = uploaded_file.read()
    informe_content = informe.read()
    time_per_scene = pdf_extract_text_per_page(BytesIO(informe_content))
    times = get_time_per_scene_from_file(time_per_scene)
    for i in times:
         print(i)

st.title("Script Analysis App")
st.session_state.script = None 
st.session_state.informe=None
# File uploaders
uploaded_script_file = st.file_uploader("Seleccione un guion", type="pdf")
if uploaded_script_file:
    st.session_state.script = uploaded_script_file
uploaded_informe_file = st.file_uploader("Seleccione archivo con duración de escenas", type="pdf")
if uploaded_informe_file:
    st.session_state.informe = uploaded_informe_file
st.session_state.start = st.button("Procesar sin informe")

if st.session_state.script is not None and (st.session_state.informe is not None or st.session_state.start):
    # Process the uploaded files
    excel_data, excel_name = process_script_file(st.session_state.script, st.session_state.informe if st.session_state.informe else None)
    # test(st.session_state.script, st.session_state.informe if st.session_state.informe else None)

    # Provide a download button for the generated Excel file
    st.download_button(
        label="Download Processed Excel File",
        data=excel_data,
        file_name=excel_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )





