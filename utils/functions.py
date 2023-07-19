import json
import os
import requests
import time

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


def get_number_vacancies_by_employer(employer_id):
    """
    Формирует запрос на API сайта HeadHunter для получения количества вакансий
    по работодателю
    :param employer_id:
    :return: num_vacancies: количество вакансий работодателя
    """
    num_vacancies = 0  # задаем количество вакансий работодателя
    url_api = f'https://api.hh.ru/vacancies'  # адрес запроса вакансий через API

    params = {'employer_id': employer_id}

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 "
                      "Safari/537.36",
    }

    req = requests.get(url_api, params=params, headers=headers)  # Посылаем запрос к API

    if req.status_code == 200:  # проверяем на корректность ответа

        data_in = req.content.decode()  # Декодируем ответ API, чтобы Кириллица отображалась корректно
        req.close()

        data_out = json.loads(data_in)  # преобразуем полученные данные из формата json

        num_vacancies = data_out['found']  # получаем количество вакансий работодателя
        name_employer = data_out['items'][0]['employer']['name']  # получаем наименование работодателя

        # проверяем количество вакансий на случай превышения лимита
        if num_vacancies > 2000:
            print(f'Количество вакансий работодателя {name_employer} превышает лимит\n'
                  f'Будут выведены последние 2000 вакансий ')
            num_vacancies = 2000

    if req.status_code != 200:
        print("В настоящий момент сайт недоступен. Попробуйте позже.")

    return num_vacancies


def get_number_pages_for_search(num_vacancies):
    """
    Определяет количество страниц, необходимых для поиска вакансий
    :param num_vacancies: количество вакансий работодателя
    :return: num_pages
    """
    num_pages = round((num_vacancies + 50) / 100)

    return num_pages


def get_vacancies_hh_by_employer(employer_id, num_pages):
    """
    Формирует запрос на API сайта HeadHunter для получения выборки вакансий
    по работодателю
    :return: список вакансий по запросу
    """

    per_page_num = 100  # задаем кол-во вакансий на 1 странице
    page_num = num_pages  # задаем количество страниц
    vacancies_count = 0  # задаем счетчик вакансий
    url_api = f'https://api.hh.ru/vacancies'  # адрес запроса вакансий через API
    vacancies_list = []  # список, в который будут сохраняться вакансии по запросу

    # перебираем страницы с вакансиями
    for page in range(0, page_num):

        # формируем справочник для параметров GET-запроса
        params = {
            'employer_id': employer_id,
            'page': page,  # Индекс страницы поиска на HH
            'per_page': per_page_num  # Кол-во вакансий на 1 странице
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

            # полученные вакансии складываем в словарь и добавляем его в список
            for vacancy in data_out['items']:
            #
            #     # запускаем метод формирования словаря
            #     vacancy_dict = HeadHunterApi.get_vacancy_dict(vacancy)
            #
            #     vacancies_list.append(vacancy_dict)  # полученный словарь добавляем в список
                vacancies_count += 1  # увеличиваем счетчик вакансий

        if req.status_code != 200:
            print("В настоящий момент сайт недоступен. Попробуйте позже.")

        if vacancies_count == data_out['found']:  # проверка на наличие вакансий на странице
            break

        time.sleep(0.2)  # временная задержка во избежание блокировки большого количества запросов

    print(vacancies_count)

    return data_out


def get_vacancies_by_employer(employer_id, page_num):
    """
    Формирует запрос на API сайта HeadHunter для получения выборки вакансий
    по работодателю
    employer_id - id работодателя
    page_num - номер страницы поиска
    :return: список вакансий по запросу
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


# b = get_number_vacancies_by_employer(3127)
# print(b)
# c = get_number_pages_for_search(b)
# print(c)

a = get_vacancies_by_employer(2605703, 0)
print(a['found'])
print(a)
