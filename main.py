import json
import os

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


file_name = os.path.abspath('./src/employers.json')


def reading_json(file_data):
    """
    Считывает данные из формата json
    :return: список вакансий
    """
    with open(file_data, 'r', encoding='utf-8') as file:
        data_1 = json.load(file)
    return data_1


a = reading_json(file_name)
print(a)
