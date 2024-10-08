# from pypdf import PdfReader 
# reader = PdfReader("Roma-Screenplay-SPANISH.pdf") 
# page = reader.pages 
# print(page.extract_text())
from io import StringIO
import os
import re
import time
import pandas as pd

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from LLM_use import CharacterExtractor_Gemini
from scene_separator import Scene_separator

def pdf_extract_text_per_page(pdf_file):
    output_dict = {}
    #with open(pdf_file, 'rb') as file:
    # with open(pdf_file, 'rb') as in_file:
    #     parser = PDFParser(in_file)
    parser = PDFParser(pdf_file)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    for i, page in enumerate(PDFPage.create_pages(doc)):
        output_string = StringIO()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        interpreter.process_page(page)
        output_dict[i] = output_string.getvalue()

    return output_dict

def save_scenes_to_excel(scenes, script_file_name):
    """
    Toma una lista de objetos Scene y guarda sus atributos en un archivo Excel.
    Cada columna del archivo Excel representa una instancia de Scene y las filas corresponden a los atributos de la clase Scene.
    """
    # Crea un diccionario para almacenar los datos de las escenas
    data = {}

    # Recorre la lista de escenas
    for i, scene in enumerate(scenes):
        # Añade los atributos de la escena al diccionario
        data[f'Escena {i+1}'] = [scene.number, scene.in_out, scene.place, scene.moment, scene.time, scene.page]

    # Crea un DataFrame de pandas a partir del diccionario
    df = pd.DataFrame(data, index=['ESC #', 'INT/EXT', 'LUGAR', 'MOMENTO', 'DURACION DE ESCENA', 'PAGINA EN GUION'])

    # Define la ruta del directorio
    dir_path = 'encabezados'

    # Comprueba si el directorio existe
    if not os.path.exists(dir_path):
        # Si no existe, crea el directorio
        os.makedirs(dir_path)

    excel_name = script_file_name + '.xlsx'
    # Guarda el DataFrame en un archivo Excel en el directorio 'encabezados'
    df.to_excel(os.path.join(dir_path, excel_name))

########################################
####3Chat gpt##########################

def save_scenes_to_excel_with_characters(scenes, script_file_name, all_characters, buffer):
    """
    Toma una lista de objetos Scene y guarda sus atributos en un archivo Excel.
    Cada columna del archivo Excel representa una instancia de Scene y las filas corresponden a los atributos de la clase Scene.
    """
    # Crea un diccionario para almacenar los datos de las escenas
    data = {}

    # Recorre la lista de escenas
    for i, scene in enumerate(scenes):
        # Añade los atributos de la escena al diccionario
        previous = 'X'
        following = 'X'
        if scene.continuity["previous"]:
            previous = ", ".join(scene.continuity["previous"])
        if scene.continuity["following"]:
            following = ", ".join(scene.continuity["following"])
        continuity =  previous + " - " + following
        scene_data = [scene.number, scene.in_out, scene.place, scene.moment, scene.time, scene.page, continuity]
        
        # Añade una 'X' para los personajes que están en la escena
        for character in all_characters:
            if any(char == character for char in scene.characters.keys()):
                scene_data.append('X')
            else:
                scene_data.append('')
        
        characters_reasons= ""
        # Añade las razones por personaje
        for key, value in scene.characters.items():
            characters_reasons += key + ": " + value.context + ", "
        scene_data.append(characters_reasons)
        scene_data.append(scene.note)
        data[f'Escena {i+1}'] = scene_data

    # Crea un DataFrame de pandas a partir del diccionario
    index = ['ESC #', 'INT/EXT', 'LUGAR', 'MOMENTO', 'DURACION DE ESCENA', 'PAGINA EN GUION', 'CONTINUIDAD'] + list(all_characters) + ['RAZONES POR PERSONAJE', 'NOTAS']
    df = pd.DataFrame(data, index=index)

    # Guarda el DataFrame en un archivo Excel en memoria
    df.to_excel(buffer, index=True)



#####################################
##### No buffer #####################
#####################################


def save_scenes_to_excel_with_characters_no_buffer(scenes, script_file_name, all_characters):
    """
    Toma una lista de objetos Scene y guarda sus atributos en un archivo Excel.
    Cada columna del archivo Excel representa una instancia de Scene y las filas corresponden a los atributos de la clase Scene.
    """
    # Crea un diccionario para almacenar los datos de las escenas
    data = {}
    print("Entering save scenes to excel\n")
    # Recorre la lista de escenas
    for i, scene in enumerate(scenes):
        # Añade los atributos de la escena al diccionario
        previous = 'X'
        following = 'X'
        if scene.continuity["previous"]:
            previous = ", ".join(scene.continuity["previous"])
        if scene.continuity["following"]:
            following = ", ".join(scene.continuity["following"])
        continuity =  previous + " - " + following
        scene_data = [scene.number, scene.in_out, scene.place, scene.moment, scene.time, scene.page, continuity]
        
        # Añade una 'X' para los personajes que están en la escena
        for character in all_characters:
            if any(char == character for char in scene.characters.keys()):
                scene_data.append('X')
            else:
                scene_data.append('')
        
        characters_reasons= ""
        # Añade las razones por personaje
        for key, value in scene.characters.items():
            characters_reasons += key + ": " + value.context + ", "
        scene_data.append(characters_reasons)
        scene_data.append(scene.note)
        data[f'Escena {i+1}'] = scene_data

    # Crea un DataFrame de pandas a partir del diccionario
    index = ['ESC #', 'INT/EXT', 'LUGAR', 'MOMENTO', 'DURACION DE ESCENA', 'PAGINA EN GUION', 'CONTINUIDAD'] + list(all_characters) + ['RAZONES POR PERSONAJE', 'NOTAS']
    df = pd.DataFrame(data, index=index)

    # Define la ruta del directorio
    dir_path = 'encabezados'

    # Comprueba si el directorio existe
    if not os.path.exists(dir_path):
        # Si no existe, crea el directorio
        os.makedirs(dir_path)

    excel_name = script_file_name + '.xlsx'
    # Guarda el DataFrame en un archivo Excel en el directorio 'encabezados'
    df.to_excel(os.path.join(dir_path, excel_name))

# script_file_name = "Informe.pdf"
# start_time = time.time()
# pages_text = pdf_extract_text_per_page(os.path.join('guiones', script_file_name))
# def extract_durations(text):
#     # Regular expression to find durations in the format a:b
#     duration_pattern = re.compile(r'\b(\d+:\d+)\b')
#     durations = duration_pattern.findall(text)
#     return durations
# dur = []
# for i in pages_text:
#     tmp = extract_durations(pages_text[i])
#     for a in tmp:
#         dur.append(a)

# print(pages_text[0])

a = 5
# sep = Scene_separator()
# scenes = sep(pages_text)
# extractor = CharacterExtractor_Gemini()
# script_characters = extractor.extract_characters(scenes, 11)
# extractor.set_continuity(scenes, 11)
# extractor.add_notes(scenes,20)
# save_scenes_to_excel_with_characters(scenes, script_file_name, script_characters)
# result = 1
# while result:
#         # try:
#             script_characters = extractor.extract_characters(scenes,11)
#             extractor.set_continuity(scenes,11)
#             result = 0
#         # except:
#         #     print("Hubo un error con el LLM, por favor inténtelo de nuevo")
# end_time = time.time()

# execution_time = end_time - start_time
# print(f"Execution time: {execution_time} seconds")
# save_scenes_to_excel(scenes, script_file_name)



# Usage
# pages_text = pdf_extract_text_per_page('Roma-Screenplay-SPANISH.pdf')
# sep = Scene_separator(" ", ". ", ". ", " - ", 
#                       ["ESC:", "SEC:", "ESCENA:", "ESCENA", "SECUENCIA:", "SECUENCIA"], 
#                       ["INT", "EXT.", "INT./EXT."], 
#                       ["DÍA", "AMANECER", "MAÑANA", "TARDE", "ATARDECER", "ANOCHECER", "NOCHE", "MADRUGADA", "AL DÍA SIGUIENTE", "MOMENTOS DESPUÉS", "CONTINÚA"])




# sep = Scene_separator(" - ", " - ", " - ", " -- ", 
#                       ["ESC:", "SEC:", "ESCENA:", "ESCENA", "SECUENCIA:", "SECUENCIA"], 
#                       ["INT", "EXT", "INT/EXT", "EXT/INT"], 
#                       ["DÍA", "DIA", "AMANECER", "MAÑANA", "TARDE", "ATARDECER", "ANOCHECER", "NOCHE", "MADRUGADA", "OCASO", "MÁS TARDE", "ALBA", "TARDE/OCASO", "AL DÍA SIGUIENTE", "MOMENTOS DESPUÉS", "CONTINÚA"])


# result = sep(pages_text)
# print(len(result))
# def extract_non_alnum_chars_per_page(pdf_file):
#     output_dict = {}
#     with open(pdf_file, 'rb') as in_file:
#         parser = PDFParser(in_file)
#         doc = PDFDocument(parser)
#         rsrcmgr = PDFResourceManager()
#         for i, page in enumerate(PDFPage.create_pages(doc)):
#             output_string = StringIO()
#             device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
#             interpreter = PDFPageInterpreter(rsrcmgr, device)
#             interpreter.process_page(page)
#             text = output_string.getvalue()
#             non_alnum_chars = set(ch for ch in text if not ch.isalnum() and not ch.isspace() and ch not in string.punctuation and ch != '\n')
#             output_dict[i] = non_alnum_chars
#     return output_dict

# pages_non_alnum_chars = extract_non_alnum_chars_per_page('Roma-Screenplay-SPANISH.pdf')
# for page, chars in pages_non_alnum_chars.items():
#     print(f"Page {page}: Non-alphanumeric characters found: {chars}")
