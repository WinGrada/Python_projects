# Дата создания: 20.04.2019
# Автор: Ходжаев Сергей Искандарович
# Почта автора: wingrada@gmail.com

# Название программы: Parsing html file to json

# Принцип работы: Берет необходимые данные из html файла и записывает их в jsonfile


import re
import json
 
BASE_PATH_HTML = 'cars_catalog.html'
BASE_PATH_JSON = 'cars_catalog.json'
 
def parser_html_to_json(path_html, path_json):
    with open(path_html, 'r', encoding='utf-8') as htmlfile:
        text_htmlfile = htmlfile.read()
 
    codes = find_codes(text_htmlfile)
    hex_codes = find_hex_codes(text_htmlfile)
    paints = find_paints(text_htmlfile)
    names = find_names(text_htmlfile)
    name_keys = ["code", "hex_code", "paints", "names"]
 
    pars_list = collect_dict(name_keys, codes, hex_codes, paints, names)
    
 
 
    with open(path_json, 'w', encoding='utf-8') as josnfile:
        json.dump(pars_list, josnfile, ensure_ascii=False, indent=4)
    ...
 
 
def find_codes(htmlfile):
    """ Returns a list of codes, shuch as int """
    list_str_num = re.findall(r'"c">(\d+)<', htmlfile)
    return [int(n) for n in list_str_num]
 
def find_hex_codes(htmlfile):
    return re.findall(r'bgcolor="(.*)["]', htmlfile)
 
def find_paints(htmlfile):
    return re.findall(r'<tr>\W\t.*\W\t.*\W\t.{4}(.*)[<]', htmlfile)
    
def find_names(htmlfile):
    return re.findall(r'<tr>\W\t.*\W\t.*\W\t.*\W\t.{4}(.*)[<]', htmlfile)
 
def collect_dict(list_names_key, list_codes, list_hex_codes, list_paints, list_names):
    """ Combines lists into a list, then collects ordered dictonaries into a list """
    """ Объединяет списки в список, затем собирает упорядоченные словари в список """
    list_of_all_list = []
    list_of_all_list.append(list_names_key)
    list_of_all_list.append(list_codes)
    list_of_all_list.append(list_hex_codes)
    list_of_all_list.append(list_paints)
    list_of_all_list.append(list_names)
 
    # ------- Grouping dictonaries -------
    result = []
 
    for cnt_part_list in range(len(list_codes)):
        final_dict = {}
 
        for cnt_keys in range(len(list_names_key)):
            final_dict[list_of_all_list[0][cnt_keys]] = list_of_all_list[cnt_keys+1][cnt_part_list]
 
        result.append(final_dict)
 
    return result
 
parser_html_to_json(BASE_PATH_HTML, BASE_PATH_JSON)
