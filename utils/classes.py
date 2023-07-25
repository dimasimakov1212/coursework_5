

class DBManager:
    """
    Позволяет подключаться к БД Postgres
    и реализует методы методы для получения данных из БД
    """

    def __init__(self, params):
        self.params = params

    def __repr__(self):
        return f"{self.__class__.__name__}\n" \
               f"{self.params}"

