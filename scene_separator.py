from typing import Any
import string

class Scene_separator(object):
    def __init__(self, scene_number_separator, number_in_out_separator, in_out_place_separator, moment_separator, scene_options, in_out_options, moment_options):
        self.Scene_number_separator = scene_number_separator
        self.Number_in_out_separator = number_in_out_separator
        self.In_out_place_separator = in_out_place_separator
        self.Moment_separator = moment_separator
        self.Scene_options = scene_options
        self.In_out_options = in_out_options
        self.Moment_options = moment_options
  
    def __call__(self, script_text_per_page):
        scenes_headings = []
        scene_found = False
        char_count = 0
        allows_epsilon_derivation = False
        for page in script_text_per_page.keys():
            page_content = script_text_per_page[page]
            page_content = page_content.split('\n')
            for i in range(len(page_content)):
                line = page_content[i]
                scene = "No especificada"
                number = "No especificado"
                # line = ''.join(ch for ch in line if ch in string.printable and not ch.isspace())
                parts = line.split(self.Scene_number_separator, 1)  # Split at first occurrence of separator
                if(len(parts) <= 1):
                    if(scene_found):
                        char_count += len(line)
                    continue
                scene_part = parts[0].strip()
                line = parts[1]
                if(scene_part in self.Scene_options):# .lower()
                    scene = scene_part
                    parts = line.split(self.Number_in_out_separator, 1)
                    if(len(parts) <= 1):
                        if(scene_found):
                            char_count += len(line)
                        continue
                    number_part = parts[0].strip()
                    line = parts[1]
                    if(number_part.isdigit()):
                        number = number_part
                        parts = line.split(self.In_out_place_separator, 1)
                        if(len(parts) <= 1):
                            if(scene_found):
                                char_count += len(line)
                            continue
                        in_out_part = parts[0].strip()
                        line = parts[1]
                        if(in_out_part in self.In_out_options):
                            in_out = in_out_part
                        else:
                            if(scene_found):
                                char_count += len(line)
                            continue
                    else: 
                        if(scene_found):
                            char_count += len(line)
                        continue
                            
                            
                else:
                    allows_epsilon_derivation = True
                    if(self.Scene_number_separator == self.Number_in_out_separator and scene_part.isdigit()):
                        number = scene_part
                        allows_epsilon_derivation = False
                        parts = line.split(self.In_out_place_separator, 1)
                        if(len(parts) <= 1):
                            if(scene_found):
                                char_count += len(line)
                            continue
                        in_out_part = parts[0].strip()
                        line = parts[1]
                        if(in_out_part in self.In_out_options):
                            in_out = in_out_part
                        else:
                            if(scene_found):
                                char_count += len(line)
                            continue

                    else:
                        if(self.Scene_number_separator == self.In_out_place_separator and scene_part in self.In_out_options):
                            in_out = scene_part
                        else:
                            if(scene_found):
                                char_count += len(line)
                            continue
                parts = line.split(self.Moment_separator, 1)
                if(len(parts) <= 1 or parts[1].strip() == ""):
                    # puede que no encuentre el momento porque sea una cabeza de escena de dos líneas
                    if(i >= len(page_content)):
                        if(scene_found):
                            char_count += len(line)
                        continue
                    tmp = len(line)
                    parts = line
                    parts += page_content[i+1]
                    parts = parts.split(self.Moment_separator, 1)
                    if(len(parts) <= 1):
                        if(scene_found):
                            char_count += tmp
                        continue
                place = parts[0].strip()
                moment = parts[1].strip()
                if(moment in self.Moment_options):
                    if(scene_found):
                        time = self.calculate_time(char_count)
                        scenes_headings[len(scenes_headings)-1].time = time
                    scenes_headings.append(Scene(number, in_out, place, moment, 0, page))
                    scene_found = True   

        return scenes_headings


    @staticmethod
    def calculate_time(char_count):
        # quotient, remainder = divmod(a, b)
        minutes, seconds = divmod(char_count, 1020)
        return (minutes, seconds)

class Scene(object):
    def __init__(self, number, in_out, place, moment, time, page):
        self.number = number
        self.in_out = in_out
        self.place = place
        self.moment = moment
        self.time = time
        self.page = page