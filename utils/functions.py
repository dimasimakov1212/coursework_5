import json
import os
import requests
import time
import psycopg2
from configparser import ConfigParser
from tqdm import tqdm


# файл в формате json со списком работодателей
# file_employers = os.path.abspath('./src/employers.json')
file_employers = os.path.abspath('./src/test.json')

# файл с параметрами для создания базы данных
file_config = os.path.abspath('./database.ini')

# файл с sql запросами
file_sql_queries = os.path.abspath('../src/queries.sql')


def reading_json(file_data):
    """
    Считывает данные из формата json
    :return:
    """
    with open(file_data, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def get_number_vacancies_by_employer(data_in):
    """
    Из ответа на запрос о вакансиях работодателя получает количество вакансий
    :param data_in: список вакансий, полученный из запроса к API
    :return: num_vacancies: количество вакансий работодателя
    """

    num_vacancies = data_in['found']  # получаем количество вакансий работодателя
    name_employer = data_in['items'][0]['employer']['name']  # получаем наименование работодателя

    # проверяем количество вакансий на случай превышения лимита
    if num_vacancies > 2000:
        print(f'Количество вакансий работодателя {name_employer} превышает лимит запросов\n'
              f'Будут загружены последние 2000 вакансий, ожидайте...')
        num_vacancies = 2000

    return num_vacancies


def get_number_pages_for_search(num_vacancies):
    """
    Определяет количество страниц, необходимых для поиска вакансий
    :param num_vacancies: количество вакансий работодателя
    :return: num_pages
    """
    num_pages = round((num_vacancies + 50) / 100)

    return num_pages


def get_vacancies_by_employer(employer_id, page_num):
    """
    Формирует запрос на API сайта HeadHunter для получения выборки вакансий
    по работодателю
    employer_id - id работодателя
    page_num - номер страницы поиска
    :return: список вакансий по запросу на одной странице поиска
    """

    url_api = 'https://api.hh.ru/vacancies'  # адрес запроса вакансий через API

    # формируем справочник для параметров GET-запроса
    params = {
        'employer_id': employer_id,
        'page': page_num,  # Индекс страницы поиска на HH
        'per_page': 100  # Кол-во вакансий на 1 странице
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 "
                      "Safari/537.36",
    }

    req = requests.get(url_api, params=params, headers=headers)  # Посылаем запрос к API

    if req.status_code == 200:  # проверяем на корректность ответа

        data_in = req.content.decode()  # Декодируем ответ API, чтобы Кириллица отображалась корректно
        req.close()

        data_out = json.loads(data_in)  # преобразуем полученные данные из формата json

    if req.status_code != 200:
        print("В настоящий момент сайт недоступен. Попробуйте позже.")

    return data_out


def get_vacancy_dict(vacancy):
    """
    Формирует словарь с необходимыми данными о вакансии из словаря, полученного по API
    :return: словарь с данными о вакансии
    """
    vacancy_dict = {}  # словарь для данных о вакансии

    vacancy_dict['vacancy_id'] = int(vacancy['id'])  # id вакансии
    vacancy_dict['vacancy_name'] = vacancy['name']  # название вакансии
    if vacancy['salary']:
        if vacancy['salary']['from'] is None or vacancy['salary']['from'] == 0:  # проверяем наличие зарплаты "от"
            vacancy_dict['salary_from'] = vacancy['salary']['to']  # в случае отсутствия приравниваем к зарплате "до"
        else:
            vacancy_dict['salary_from'] = vacancy['salary']['from']  # нижний предел зарплаты

        if vacancy['salary']['to'] is None or vacancy['salary']['to'] == 0:  # проверяем наличие зарплаты "до"
            vacancy_dict['salary_to'] = vacancy['salary']['from']  # в случае отсутствия приравниваем к зарплате "от"
        else:
            vacancy_dict['salary_to'] = vacancy['salary']['to']  # верхний предел зарплаты

        if vacancy['salary']['currency'] is None:  # проверяем наличие данных о валюте зарплаты
            vacancy_dict['currency'] = 'RUR'
        else:
            vacancy_dict['currency'] = vacancy['salary']['currency']  # валюта зарплаты
    else:
        vacancy_dict['salary_from'] = 0
        vacancy_dict['salary_to'] = 0
        vacancy_dict['currency'] = 'RUR'
    vacancy_dict['employer_id'] = vacancy['employer']['id']  # id работодателя
    vacancy_dict['employer_name'] = vacancy['employer']['name']  # наименование работодателя
    vacancy_dict['vacancy_url'] = vacancy['alternate_url']  # ссылка на вакансию

    return vacancy_dict


def get_all_vacancies_by_employer(employer_id, num_pages):
    """
    Запускает цикл по страницам с вакансиями работодателя
    :param employer_id: id работодателя
    :param num_pages: количество страниц для поиска
    :return: список всех вакансий работодателя
    """
    employer_vacancies = []  # задаем список, в который будут записаны все вакансии работодателя
    vacancies_count = 0  # задаем счетчик вакансий

    for page in range(num_pages):  # запускаем перебор страниц с вакансиями
        vacancies_per_page = get_vacancies_by_employer(employer_id, page)  # получаем вакансии на одной странице

        for count in vacancies_per_page['items']:  # запускаем перебор вакансий на странице
            vacancy = get_vacancy_dict(count)  # формируем словарь с вакансией с необходимыми данными
            employer_vacancies.append(vacancy)  # добавляем словарь вакансии в список
            vacancies_count += 1  # увеличиваем счетчик вакансий

        if vacancies_count == vacancies_per_page['found']:  # проверка на наличие вакансий на странице
            break

        time.sleep(0.2)  # временная задержка во избежание блокировки большого количества запросов

    return employer_vacancies


def get_employers_list(employers_data):
    """
    Создает список работодателей, который содержит
    id работодателя, наименование работодателя, количество вакансий
    :param employers_data: json файл с работодателями
    :return: список работодателей
    """
    employers_list = []  # создаем список для работодателей

    # получаем список работодателей
    employers = reading_json(employers_data)
    print(f"Получен список из {len(employers)} работодателей")
    print('>>> Полчаем данные о вакансиях')

    # запускаем перебор работодателей
    for employer in employers:
        employer_dict = {}  # создаем пустой словарь для работодателя

        employer_id = employer['id']  # получаем id работодателя

        req = get_vacancies_by_employer(employer_id, 0)  # делаем запрос о вакансиях работодателя
        number_vacancies = get_number_vacancies_by_employer(req)  # получаем количество вакансий работодателя

        if number_vacancies == 0:  # если у работодателя нет вакансий переходим к следующему
            print(f"У работодателя {employer['employer']} нет свободных вакансий")
            continue

        # формируем словарь
        employer_dict['employer_id'] = employer['id']
        employer_dict['employer_name'] = req['items'][0]['employer']['name']
        employer_dict['vacancies_count'] = number_vacancies

        employers_list.append(employer_dict)  # добавляем словарь с работодателем в список

    return employers_list


def get_all_vacancies(employers_data):
    """
    Формирует список всех вакансий всех работодателей
    :param employers_data: список с работодателями
    :return: список всех вакансий по всем работодателям
    """
    vacancies_all = []  # задаем список, в который будут записаны все вакансии

    print("\n>>> Загружаем данные по вакансиям\n"
          "В зависимости от количества вакансий, это может занять продолжительное время. Подождите...\n")

    # запускаем перебор работодателей
    for employer in tqdm(employers_data, desc='Загрузка', leave=False):

        # получаем количество страниц с вакансиями работодателя
        number_pages = get_number_pages_for_search(employer['vacancies_count'])

        # получаем список всех вакансий работодателя
        vacancies_by_employer = get_all_vacancies_by_employer(employer['employer_id'], number_pages)

        # записываем все вакансии в общий список
        for vacancy in vacancies_by_employer:
            vacancies_all.append(vacancy)

    print("------------ Загрузка завершена ------------")
    print(f"Всего получено {len(vacancies_all)} вакансий\n")

    return vacancies_all


def get_params(filename, section):
    """
    Получает параметры конфигурации из файла с данными
    :return: словарь с параметрами
    """
    parser = ConfigParser()  # создаем парсер
    parser.read(filename)  # считываем содержимое файла

    params_dict = {}  # создаем словарь для хранения параметров

    if parser.has_section(section):  # проверяем существует ли нужный раздел
        params = parser.items(section)  # присваиваем переменной данные из раздела
        for param in params:  # записываем данные в словарь
            params_dict[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(section, filename))
    return params_dict


def create_database(database_name: str, params: dict):
    """
    Создает базу данных для хранения вакансий
    :param database_name: имя БД
    :param params: параметры соединения
    :return:
    """
    print(f">>> Создаем базу данных {database_name}")
    conn = psycopg2.connect(dbname='postgres', **params)  # создаем соединение с БД
    conn.autocommit = True  # включаем автокоммит запросов в БД
    cur = conn.cursor()  # создаем курсор

    cur.execute(f"DROP DATABASE IF EXISTS {database_name}")  # удаляем базу данных если она существует
    cur.execute(f"CREATE DATABASE {database_name}")  # создаем новую базу данных

    conn.close()  # закрываем соединение

    # создаем таблицы в базе данных
    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:  # таблица с работодателями
        cur.execute("""
            CREATE TABLE employers (
                employer_id INT PRIMARY KEY,
                employer_name VARCHAR(255) NOT NULL,
                number_vacancies INTEGER
            )
        """)

    with conn.cursor() as cur:  # таблица с вакансиями
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id INT PRIMARY KEY,
                vacancy_name VARCHAR NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                employer_id INT REFERENCES employers(employer_id),
                vacancy_url TEXT
            )
        """)

    conn.commit()
    conn.close()


def employers_table_filling(database_name: str, params: dict, employers_list):
    """
    Заполняет таблицу employers данными из списка работодателей
    """
    print(">>> Заполняем таблицу по работодателям")
    conn = psycopg2.connect(dbname=database_name, **params) # создаем соединение с БД

    # запускаем заполнение таблицы
    try:
        with conn:
            with conn.cursor() as cur:
                for employer in employers_list:
                    # передаем данные из списка в таблицу базы данных
                    cur.execute('INSERT INTO employers VALUES (%s, %s, %s)',
                                (employer['employer_id'],
                                 employer['employer_name'],
                                 employer['vacancies_count']))

                    cur.execute('SELECT * FROM employers')  # записываем данные в таблицу

    finally:
        conn.close()  # закрываем запись в БД


def vacancies_table_filling(database_name: str, params: dict, vacancies_list):
    """
    Заполняет таблицу employers данными из списка работодателей
    """
    print(">>> Заполняем таблицу по вакансиям")

    conn = psycopg2.connect(dbname=database_name, **params) # создаем соединение с БД

    # запускаем заполнение таблицы
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute('TRUNCATE ONLY vacancies RESTART IDENTITY')
                for vacancy in vacancies_list:
                    # передаем данные из списка в таблицу базы данных

                    cur.execute('INSERT INTO vacancies VALUES (%s, %s, %s, %s, %s, %s)',
                                (vacancy['vacancy_id'],
                                 vacancy['vacancy_name'],
                                 vacancy['salary_from'],
                                 vacancy['salary_to'],
                                 vacancy['employer_id'],
                                 vacancy['vacancy_url']
                                 ))

                    cur.execute('SELECT * FROM vacancies')  # записываем данные в таблицу

    finally:
        conn.close()  # закрываем запись в БД


def get_vacancies_and_create_database(db_name):
    """
    Соединяет вместе функции поиска вакансий и создания базы данных
    :return:
    """
    employers_list = get_employers_list(file_employers)  # создаем список работодателей с количеством вакансий

    vacancies_list = get_all_vacancies(employers_list)  # создание списка всех вакансий

    params_dict = get_params(file_config, "postgresql")  # получаем словарь с параметрами для создания БД

    create_database(db_name, params_dict)  # создаем базу данных

    employers_table_filling(db_name, params_dict, employers_list)  # заполняем таблицу работодателей

    vacancies_table_filling(db_name, params_dict, vacancies_list)


# a2 = get_employers_list(file_employers)  # создаем список работодателей с количеством вакансий
# a3 = get_all_vacancies(a2)  # создание списка всех вакансий

# c1 = get_params(file_config, "postgresql")  # получаем словарь с параметрами для создания БД
# print(c1)
# create_database('vacancies_hh', c1)  # создаем базу данных
# employers_table_filling('vacancies_hh', c1, a2)
# vacancies_table_filling('vacancies_hh', c1, a3)

# c2 = get_params(file_sql_queries, 'employers')  # получаем словарь с sql запросами
# print(c2)
# for q in c2:
#     print(c2[q])
