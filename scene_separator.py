
from sly import Lexer, Parser
import re

def read_scene():
    # Abre el archivo en modo lectura
    with open('Scene.txt', 'r') as archivo:
        # Lee el contenido del archivo
        a = archivo.read()
    contenido = a.split('\n')
    scene_options2 = sorted(contenido, key=len, reverse=True)
    Scene2='|'.join(scene_options2)
    return Scene2

def read_in_out():
    # Abre el archivo en modo lectura
    with open('InOut.txt', 'r') as archivo:
        # Lee el contenido del archivo
        a = archivo.read()
    contenido = a.split('\n')
    In_out_option = sorted(contenido, key=len, reverse=True)
    In_out2='|'.join(In_out_option)
    return In_out2

def read_moment():
    # Abre el archivo en modo lectura
    with open('Moment.txt', 'r', encoding='utf-8') as archivo:
        # Lee el contenido del archivo
        a = archivo.read()
    contenido = a.split('\n')
    Moment_option = sorted(contenido, key=len, reverse=True)
    Moment2='|'.join(Moment_option)
    return Moment2

class MyLexer(Lexer):
    tokens={SEPARADOR, SCENE_OPTIONS, IN_OUT_OPTIONS, MOMENT_OPTIONS, NUMBER,TEXT}

    ignore=' \t\n'

    SCENE_OPTIONS=rf'{read_scene()}'
    IN_OUT_OPTIONS = rf'{read_in_out()}'
    MOMENT_OPTIONS = rf'{read_moment()}'
    NUMBER = r'\d+'
    SEPARADOR = r'\-|\-\-|/|\.|\–|\–\–'
    TEXT = r'[^\s\n\t]+'

class MyParser(Parser):
    tokens = MyLexer.tokens

    # Regla principal de la gramática que reconoce la estructura general
    @_('opcional_escena opcional_numero in_out_opcion texto_con_separadores moment_options')
    def entrada(self, p):
        return ( p.opcional_escena, p.opcional_numero, p.in_out_opcion, p.texto_con_separadores, p.moment_options)

    # Reglas para manejar la opción de tener o no SCENE_OPTIONS
    @_('SCENE_OPTIONS')
    def opcional_escena(self, p):
        return p.SCENE_OPTIONS

    @_('empty')
    def opcional_escena(self, p):
        return None

    # Reglas para manejar la opción de tener o no NUMBER
    @_('NUMBER SEPARADOR')
    def opcional_numero(self, p):
        return p.NUMBER

    @_('empty')
    def opcional_numero(self, p):
        return None

    # Regla para manejar IN_OUT_OPTIONS seguido de un separador
    @_('IN_OUT_OPTIONS SEPARADOR')
    def in_out_opcion(self, p):
        return p.IN_OUT_OPTIONS

    @_('TEXT secuencia_de_texto')
    def texto_con_separadores(self, p):
        return f"{p.TEXT} {p.secuencia_de_texto}"
    
    @_('SEPARADOR TEXT secuencia_de_texto ')
    def secuencia_de_texto(self, p):
        return f"{p.SEPARADOR} {p.TEXT} {p.secuencia_de_texto}"
    
    @_('TEXT secuencia_de_texto')
    def secuencia_de_texto(self, p):
        return f"{p.TEXT} {p.secuencia_de_texto}"

    @_('SEPARADOR')
    def secuencia_de_texto(self, p):
        return ""
    
    @_('IN_OUT_OPTIONS secuencia_de_texto')
    def secuencia_de_texto(self, p):
        return f"{p.IN_OUT_OPTIONS}{p.secuencia_de_texto}"
    
    @_('NUMBER secuencia_de_texto')
    def secuencia_de_texto(self, p):
        return f"{p.NUMBER} {p.secuencia_de_texto}"
    
    
    @_('MOMENT_OPTIONS')
    def moment_options(self, p):
        return p.MOMENT_OPTIONS

    # Regla para manejar casos vacíos (ausencia de SCENE_OPTIONS o NUMBER)
    @_('')
    def empty(self, p):
        return None

    # Manejo de errores sintácticos
    def error(self, p):
        pass

class Scene_separator(object):
    def __init__(self):
        self.lexer = MyLexer()
        self.parser = MyParser()
  
    def __call__(self, script_text_per_page):
        scenes_headings = []
        past_line=["",0.0]
        index_scene=1
        text=["",0.0]
        old_result=None
        last_page=None

        # Obtener las llaves como una lista
        pages = list(script_text_per_page.keys())

        for i, page in enumerate(pages):
            is_last_page = (i == len(pages) - 1)
            page_content = script_text_per_page[page]
            page_content = re.split(r'\n+',page_content)
            second_per_line=60/len(page_content)
            for line in page_content:
                a = line.strip()
                result = self.parser.parse(self.lexer.tokenize(a))
                if old_result is None:
                    if result is None:
                        past_line[0]+=" "
                        result2= self.parser.parse(self.lexer.tokenize(past_line[0]+a))
                        if result2 is None:
                            if is_last_page:
                                past_line=[line.strip(),len(line)/17]
                            else:
                                past_line=[line.strip(),second_per_line]
                        else:
                            old_result=result2
                            past_line=["",0.0]
                            last_page=page
                    else:
                        old_result=result
                        past_line=["",0.0]
                        last_page=page
                    continue
                elif result is None:
                    past_line[0]+=" "
                    result3 = self.parser.parse(self.lexer.tokenize(past_line[0]+a))
                    if result3 is None:
                        text[0]+= "\n"+ past_line[0].strip()
                        text[1]+=past_line[1]
                        if is_last_page:
                            past_line=[line.strip(),len(line)/17]
                        else:
                            past_line=[line.strip(),second_per_line]
                    else:
                        if old_result[1] is None:
                            scenes_headings.append(Scene(index_scene,old_result[2],old_result[3],old_result[4],self.calculate_time(text[1]),last_page,text=text[0].strip()))
                        else:
                            scenes_headings.append(Scene(int(old_result[1]),old_result[2],old_result[3],old_result[4],self.calculate_time(text[1]),last_page,text=text[0].strip()))
                        past_line=["",0.0]
                        text=["",0.0]
                        old_result=result3
                        index_scene+=1
                        last_page=page
                else:
                    text[0]+= "\n"+ past_line[0].strip()
                    text[1]+=past_line[1]
                    if old_result[1] is None:
                        scenes_headings.append(Scene(index_scene,old_result[2],old_result[3],old_result[4],self.calculate_time(text[1]),last_page,text=text[0].strip()))
                    else:
                        scenes_headings.append(Scene(int(old_result[1]),old_result[2],old_result[3],old_result[4],self.calculate_time(text[1]),last_page, text=text[0].strip()))
                    past_line=["",0.0]
                    text=["",0.0]
                    old_result=result
                    index_scene+=1
                    last_page=page
        if old_result != None:
            text[0]+= "\n"+past_line[0].strip()
            text[1]+=past_line[1]
            if old_result[1] is None:
                scenes_headings.append(Scene(index_scene,old_result[2],old_result[3],old_result[4],self.calculate_time(text[1]),last_page,text=text[0].strip()))
            else:
                scenes_headings.append(Scene(int(old_result[1]),old_result[2],old_result[3],old_result[4],self.calculate_time(text[1]),last_page,text=text[0].strip()))

        return scenes_headings
    

    @staticmethod
    def calculate_time(sec):
        minutes, seconds = divmod(sec,60)
        return (int(minutes), int(seconds))

class Scene(object):
    def __init__(self, number, in_out, place, moment, time, page, characters=None, continuity=None, text=""):
        self.number = number
        self.in_out = in_out
        self.place = place
        self.moment = moment
        self.time = time
        self.page = page
        self.characters = characters if characters is not None else {}
        self.continuity = continuity if continuity is not None else {}
        self.text = text