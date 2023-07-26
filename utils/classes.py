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

    def get_companies_and_vacancies_count(self):
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

    def get_all_vacancies(self):
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

    def get_avg_salary(self):
        """
        Получение средней зарплаты по вакансиям
        :return:
        """

        sql_dict = get_params(self.file_sql_queries, 'salary_avg')  # получаем список sql запросов

        conn = psycopg2.connect(dbname=self.db_name, **self.params)  # создаем соединение с БД

        # запускаем выполнение sql запросов из словаря

        with conn.cursor() as cur:
            for query in sql_dict:
                cur.execute(sql_dict[query])  # передаем запрос в базу данных
                results = cur.fetchall()  # получаем данные по запросу
                for item in results:
                    print(f'Вакансия - {item[0]}, средняя зарплата - {item[1]}, ссылка на вакансию - {item[2]}')

        conn.close()  # закрываем соединение с БД

    def get_vacancies_with_higher_salary(self):
        """
        Получение списка всех вакансий, у которых зарплата выше средней по всем вакансиям
        :return:
        """

        sql_dict = get_params(self.file_sql_queries, 'salary_higher')  # получаем список sql запросов

        conn = psycopg2.connect(dbname=self.db_name, **self.params)  # создаем соединение с БД

        # запускаем выполнение sql запросов из словаря

        with conn.cursor() as cur:
            for query in sql_dict:
                cur.execute(sql_dict[query])  # передаем запрос в базу данных
                results = cur.fetchall()  # получаем данные по запросу
                for item in results:
                    print(f'Вакансия - {item[0]}, зарплата - {item[1]}-{item[2]},'
                          f' ссылка на вакансию - {item[3]}')

        conn.close()  # закрываем соединение с БД

    def get_vacancies_with_keyword(self, keyword):
        """
        Получение списка всех вакансий, в названии которых содержатся ключевые слова
        :return:
        """

        sql_dict = get_params(self.file_sql_queries, 'keyword')  # получаем список sql запросов

        conn = psycopg2.connect(dbname=self.db_name, **self.params)  # создаем соединение с БД

        # запускаем выполнение sql запросов из словаря

        with conn.cursor() as cur:
            for query in sql_dict:
                sql_query = sql_dict[query].replace('keyword', f"'%{keyword}%'")
                cur.execute(sql_query)  # передаем запрос в базу данных
                results = cur.fetchall()  # получаем данные по запросу

                if len(results) == 0:
                    print('По указанному ключевому слову нет результатов')
                for item in results:
                    print(f'Вакансия - {item[0]}, зарплата - {item[1]}-{item[2]},'
                          f' ссылка на вакансию - {item[3]}')

        conn.close()  # закрываем соединение с БД
