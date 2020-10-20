import sqlite3
from functools import reduce

"""В этом файле содержится подключение к базе данных sqlite3 и объекты моделей,
связывающие таблицы в БД с объектами в коде (простой вариант ORM). 
Все модели наследуются от базового класса AbstractModel."""

DATABASE = 'tasks_and_settings.db'
CONNECTION = sqlite3.connect(DATABASE)
CURSOR = CONNECTION.cursor()
CURSOR.execute('''CREATE TABLE IF NOT EXISTS Settings (
                id INTEGER PRIMARY KEY,
                short_desc TEXT NOT NULL,
                lc_colors TEXT NOT NULL,
                tf_color TEXT NOT NULL,
                fill_colors TEXT NOT NULL
                )''')

CURSOR.execute('''CREATE TABLE IF NOT EXISTS Tasks (
                id INTEGER PRIMARY KEY,
                problem_situation TEXT,
                target_func_lim TEXT NOT NULL,
                target_func_coefs TEXT NOT NULL,
                linear_constraints TEXT NOT NULL,
                settings_id INTEGER,
                FOREIGN KEY (settings_id)
                    REFERENCES Settings (id)
                        ON DELETE CASCADE 
                        ON UPDATE NO ACTION
                )''')


class AbstractModel:
    TABLE = None
    VERBOSE_ATTRS = {}

    def __init__(self):
        self.ATTRS = [] if not self.TABLE else [
                d[0] for d in
                CURSOR.execute('SELECT * FROM ' + self.TABLE).description
            ]

    def get_title(self):
        return [self.VERBOSE_ATTRS.get(a, a) for a in self.ATTRS]

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
                CURSOR.execute(f'''INSERT INTO {self.model.TABLE}
                                ({", ".join("?" * len(keys))}) 
                                VALUES ({", ".join("?" * len(values))})''',
                               (*keys, *values))
                CONNECTION.commit()
                self.saved = True
                self.id = CURSOR.lastrowid

        def update(self):
            """Обновляет сохранённый объект в базе данных.
            Если объект не сохранён, ничего не происходит."""
            if self.saved:
                CURSOR.execute(f'''UPDATE {self.model.TABLE}
                    SET {", ".join(["?=?"] * len(self.__dict__))}
                    WHERE id=?''', (
                    *reduce(
                        lambda res, x: res + x, self.__dict__.items()), self.id),)
                CONNECTION.commit()

        def delete(self):
            """Удаляет объект из базы данных, если он есть в ней.
            Если объект не сохранён в базе данных, ничего не происходит."""
            if self.saved:
                CURSOR.execute(f'''DELETE FROM {self.model.TABLE} WHERE id=?''', (self.id, ))
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
                for x in CURSOR.execute('SELECT * FROM ' + self.TABLE).fetchall()]

    def __get_filter_cursor(self, **kwargs):
        return CURSOR.execute(f'''SELECT * FROM {self.TABLE}
            WHERE {" AND ".join(["?=?" * len(kwargs)])}''', (
            *reduce(lambda res, x: res + x, kwargs.items()),
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


class SettingsModel(AbstractModel):
    TABLE = 'Settings'


class TaskModel(AbstractModel):
    TABLE = 'Tasks'
    LIM_INF = 'inf'
    LIM_ZERO = '0'
    VERBOSE_ATTRS = {
        'problem_situation': 'Условие задачи',
        'target_func_lim': 'Целевая функция стремиться к',
        'linear_constraints': 'Линейные ограничения',
        'settings_id': 'Настройки',
        'target_func_coefs': 'Коэффициенты целевой функции'
    }
