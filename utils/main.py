import os
from utils.functions import get_params
from utils.classes import DBManager

# файл с параметрами для создания базы данных
file_config = os.path.abspath('./database.ini')

database_name = 'vacancies_hh'


def start_menu():
    """
    Запускает основное меню
    :return:
    """
    print('------------------------------')
    print('Выберите необходимое действие:')
    main_menu()


def main_menu():
    """
    Основное меню для работы с программой
    :return:
    """
    print('1 - Запуск получения информации о вакансиях и создание базы данных\n'
          '    (в случае, если база данных уже существует, этот пункт можно пропустить)')
    print('2 - Получение списка всех компаний и количества вакансий у каждой компании')
    print('3 - Получение списка всех вакансий с указанием названия компании, \n'
          '    названия вакансии и зарплаты и ссылки на вакансию')
    print('4 - Получение средней зарплаты по вакансиям')
    print('5 - Получение списка всех вакансий, у которых зарплата выше средней по всем вакансиям')
    print('6 - Получение списка всех вакансий, в названии которых содержатся ключевые слова, например “python”')

    print('0 - выход из программы')

    user_choice = input('>>> ')

    if user_choice == '1':
        get_vacancies_and_db_create()  # парсинг вакансий и создание БД

    if user_choice == '2':
        get_employers_list_and_vacancies_count()  # вывод списка компаний

    if user_choice == '3':
        get_all_vacancies_list()  # вывод списка вакансий

    if user_choice == '4':
        get_average_salary()  # вывод средней зарплаты

    if user_choice == '5':
        get_vacancies_list_with_high_salary()  # вывод вакансий с зарплатой выше средней

    if user_choice == '6':
        get_vacancies_list_by_key_word()  # вывод списка вакансий по ключевому слову

    if user_choice == '0':
        exit()

    else:
        print('\nВы ввели некорректное значение')
        start_menu()


def get_vacancies_and_db_create():
    """
    Запускает поиск вакансий и создание базы данных
    :return:
    """
    print('\nЗапускаю поиск вакансий')
    start_menu()


def get_employers_list_and_vacancies_count():
    """
    Получение списка всех компаний и количества вакансий у каждой компании
    :return:
    """
    print('\n--- Вывод списка всех компаний ---')

    params = get_params(file_config, "postgresql")  # получаем параметры подключения к БД
    employers = DBManager(params, database_name)  # инициализируем экземпляр класса
    employers.get_employers_list_and_vacancies_number()  # запускаем метод класса

    start_menu()


def get_all_vacancies_list():
    """
    Получение списка всех вакансий с указанием названия компании,
    названия вакансии и зарплаты и ссылки на вакансию
    :return:
    """
    print('\n--- Вывод списка всех вакансий ---')

    params = get_params(file_config, "postgresql")  # получаем параметры подключения к БД
    vacancies = DBManager(params, database_name)  # инициализируем экземпляр класса
    vacancies.get_vacancies_list()  # запускаем метод класса

    start_menu()


def get_average_salary():
    """
    Получение средней зарплаты по вакансиям
    :return:
    """
    print('\n--- Вывод средней зарплаты по вакансиям ---')
    start_menu()


def get_vacancies_list_with_high_salary():
    """
    Получение списка всех вакансий, у которых зарплата выше средней по всем вакансиям
    :return:
    """
    print('\n--- Вывод списка всех вакансий, у которых зарплата выше средней ---')
    start_menu()


def get_vacancies_list_by_key_word():
    """
    Получение списка всех вакансий по ключевому слову
    :return:
    """
    print('\n--- Вывод списка всех вакансий, в названии которых содержатся ключевые слова ---')
    start_menu()


if __name__ == '__main__':
    print('Программа позволяет загружать данные о вакансиях работодателей с сайта HeadHanter,\n'
          'создавать на основе этих данных базу данных и получать необходимые данные из нее')

    start_menu()
