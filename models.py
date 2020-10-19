import sqlite3
from functools import reduce

"""В этом файле содержится подключение к базе данных sqlite3 и объекты моделей,
связывающие таблицы в БД с объектами в коде (простой вариант ORM). 
Все модели наследуются от базового класса AbstractModel."""

DATABASE = 'tasks_and_settings.db'
CONNECTION = sqlite3.connect(DATABASE)
CURSOR = CONNECTION.cursor()
# TODO: схема БД и её заполнение задачами-примерами и настройками по умолчанию


class AbstractModel:
    TABLE = None

    def __init__(self):
        self.ATTRS = [] if not self.TABLE else [
                d[0] for d in
                CURSOR.execute('SELECT * FROM ?', (self.TABLE,)).description
            ]

    class __ModelObject:
        def __init__(self, model, saved=False, **kwargs):
            """Инициализирует объект модели 'model' с заданными аттрибутами.
            Если хотя бы одного аттрибута нет в списке аттрибутов модели - поднимает исключение."""
            for key, value in kwargs.items():
                if key in model.ATTRS:
                    self.__dict__[key] = value
                else:
                    raise AttributeError(f'"{type(model).__name__}" has no attribute "{key}"')
            self.model = model
            self.saved = saved

        def __setattr__(self, key, value):
            """Присваивает значение 'value' аттрибуту 'key',
            если 'key' есть в списке аттрибутов модели,
            иначе - поднимает исключение."""
            if key in self.model.ATTRS:
                self.__dict__[key] = value
            else:
                raise AttributeError(f'"{type(self.model).__name__}" has no attribute "{key}"')

        def save(self):
            """Сохраняет объект в базе данных и помечает его как сохранённый.
            Если объект уже сохранён, то ничего не происходит."""
            if not self.saved:
                keys = self.__dict__.keys()
                values = self.__dict__.values()
                CURSOR.execute(f'''INSERT INTO ? ({", ".join("?" * len(keys))}) 
                                VALUES ({", ".join("?" * len(values))})''',
                               (self.model.TABLE, *keys, *values))
                CONNECTION.commit()
                self.saved = True
                self.id = CURSOR.lastrowid

        def delete(self):
            """Удаляет объект из базы данных, если он есть в ней.
            Если объект не сохранён в базе данных, ничего не происходит."""
            if self.saved:
                CURSOR.execute('''DELETE FROM ? WHERE id=?''', (self.model.TABLE, self.id))
                CONNECTION.commit()
                self.saved = False
                del self.id

    def new(self, **kwargs):
        """Создаёт и возвращает объект модели с заданными аттрибутами."""
        obj = self.__ModelObject(self, **kwargs)
        return obj

    def all(self):
        """Возвращает список всех объектов модели."""
        return [self.__ModelObject(self, True, **dict(zip(self.ATTRS, x)))
                for x in CURSOR.execute('SELECT * FROM ?', (self.TABLE,)).fetchall()]

    def __get_filter_cursor(self, **kwargs):
        return CURSOR.execute(f'''SELECT * FROM ?
            WHERE {" AND ".join(["?=?" * len(kwargs)])}''', (
            self.TABLE, *reduce(lambda res, x: res + x, kwargs.items())
        ))

    def __row_to_obj(self, row):
        return self.__ModelObject(self, True, **dict(zip(self.ATTRS, row)))

    def get(self, **kwargs):
        """Возвращает один объект по заданным ограничениям типа 'аттрибут=значение'.
        Если объектов, удовлетворяющих ограничениям, несколько, то возвращает первый.
        Если объект не найден, возвращает None"""
        result = self.__get_filter_cursor(**kwargs).fetchone()
        return result if not result else self.__row_to_obj(result)

    def filter(self, **kwargs):
        """Возвращает список объектов по заданным ограничениям типа 'аттрибут=значение'.
        Список объектов может быть пустым."""
        result = self.__get_filter_cursor(**kwargs).fetchall()
        return [self.__row_to_obj(row) for row in result]

    def __del__(self):
        CONNECTION.close()


class SettingsModel(AbstractModel):
    TABLE = 'Settings'


class TaskModel(AbstractModel):
    TABLE = 'Tasks'
