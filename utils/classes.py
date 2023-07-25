import psycopg2
import os
from functions import get_params


class DBManager:
    """
    Позволяет подключаться к БД Postgres
    и реализует методы методы для получения данных из БД
    """

    def __init__(self, params, db_name):
        self.params = params  # параметры подключения к БД
        self.db_name = db_name  # имя базы данных
        self.file_sql_queries = os.path.abspath('./src/queries.sql')  # файл с sql запросами

    def __repr__(self):
        return f"{self.__class__.__name__}\n" \
               f"{self.params}\n" \
               f"{self.db_name}"

    def get_employers_list_and_vacancies_number(self):
        """
        Получение списка всех компаний и количества вакансий у каждой компании
        :return:
        """

        sql_dict = get_params(self.file_sql_queries, 'employers')  # получаем список sql запросов

        conn = psycopg2.connect(dbname=self.db_name, **self.params)  # создаем соединение с БД

        # запускаем выполнение sql запросов из словаря

        with conn.cursor() as cur:
            for query in sql_dict:
                cur.execute(sql_dict[query])  # передаем запрос в базу данных
                results = cur.fetchall()  # получаем данные по запросу
                for item in results:
                    print(f'Компания - {item[0]}, количество вакансий - {item[1]}')

        conn.close()  # закрываем соединение с БД

    def get_vacancies_list(self):
        """
        Получение списка всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию
        :return:
        """

        sql_dict = get_params(self.file_sql_queries, 'vacancies')  # получаем список sql запросов

        conn = psycopg2.connect(dbname=self.db_name, **self.params)  # создаем соединение с БД

        # запускаем выполнение sql запросов из словаря

        with conn.cursor() as cur:
            for query in sql_dict:
                cur.execute(sql_dict[query])  # передаем запрос в базу данных
                results = cur.fetchall()  # получаем данные по запросу
                for item in results:
                    print(f'Компания - {item[0]}, вакансия - {item[1]}, зарплата - {item[2]}-{item[3]},'
                          f' ссылка на вакансию - {item[4]}')

        conn.close()  # закрываем соединение с БД
