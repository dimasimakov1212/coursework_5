import json
import os

# файл в формате json со списком работодателей
file_employers = os.path.abspath('../src/employers.json')


def reading_json(file_data):
    """
    Считывает данные из формата json
    :return:
    """
    with open(file_data, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


a = reading_json(file_employers)
for i in a:
    print(i['id'])
