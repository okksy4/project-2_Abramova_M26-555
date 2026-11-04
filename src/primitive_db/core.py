from .utils import load_table_data

VALID_TYPES = {'int', 'str', 'bool'}

def create_table(metadata, table_name, columns):
    """
    Создает новую таблицу в метаданных базы данных.

    Args:
        metadata (dict): метаданные базы данных (с ключом 'tables')
        table_name (str): имя создаваемой таблицы
        columns (list): список кортежей (имя_столбца, тип_данных)

    Returns:
        dict: обновленные метаданные с новой таблицей

    Raises:
        ValueError: при ошибках валидации имени, столбцов или типов
    """
    # валидация имени: пустое отсекается isidentifier, длина отдельно
    if not table_name.isidentifier():
        raise ValueError("Некорректное имя таблицы")
    if len(table_name) > 50:
        raise ValueError("Имя таблицы не может превышать 50 символов")

    if table_name in metadata['tables']:
        raise ValueError(f'Таблица "{table_name}" уже существует')

    # проверяем пользовательский ID и добавляем свой, если его нет
    column_names = [col[0] for col in columns]
    if 'ID' in column_names:
        id_index = column_names.index('ID')
        if columns[id_index][1] != 'int':
            raise ValueError("Столбец ID должен иметь тип int")
    else:
        columns = [('ID', 'int')] + list(columns)
        column_names = ['ID'] + column_names

    # уникальность и корректность имен столбцов
    if len(column_names) != len(set(column_names)):
        raise ValueError("Имена столбцов должны быть уникальными")
    for col_name in column_names:
        if not col_name.isidentifier():
            raise ValueError(f"Некорректное имя столбца: {col_name}")

    # корректность типов
    for _, col_type in columns:
        if col_type not in VALID_TYPES:
            raise ValueError(
                f"Некорректный тип: {col_type}. "
                f"Допустимые типы: {', '.join(sorted(VALID_TYPES))}"
            )

    metadata['tables'][table_name] = {
        'columns': {col_name: col_type for col_name, col_type in columns}
    }
    return metadata

def drop_table(metadata, table_name):
    """
    Удаляет таблицу из базы данных.

    Args:
        metadata (dict): текущие метаданные базы данных
        table_name (str): имя удаляемой таблицы

    Returns:
        dict: обновленные метаданные без удаленной таблицы

    Raises:
        ValueError: если таблица не существует
    """
    if table_name not in metadata['tables']:
        raise ValueError(f'Таблица "{table_name}" не существует')

    del metadata['tables'][table_name]
    return metadata

# GRUD
def check_value_type(col_name, col_type, value):
    """Проверяет, что значение соответствует типу столбца."""
    if col_type == 'bool' and not isinstance(value, bool):
        raise ValueError(f'Столбец {col_name} имеет тип bool')
    if col_type == 'int' and (isinstance(value, bool) or not isinstance(value, int)):
        raise ValueError(f'Столбец {col_name} имеет тип int')
    if col_type == 'str' and not isinstance(value, str):
        raise ValueError(f'Столбец {col_name} имеет тип str')
    return value

def _matches(row, where_clause):
    """Проверяет запись по условию-словарю {'поле': значение}."""
    field, value = next(iter(where_clause.items()))
    return row[field] == value

def insert(metadata, table_name, values):
    """
    Добавляет запись: значения сопоставляются со столбцами без ID,
    новый ID = max(ID) + 1. Возвращает (данные таблицы, новый ID).
    """
    if table_name not in metadata['tables']:
        raise ValueError(f'Таблица "{table_name}" не существует')

    columns = metadata['tables'][table_name]['columns']
    data_columns = [c for c in columns if c != 'ID']

    if len(values) != len(data_columns):
        raise ValueError(
            f"Ожидалось {len(data_columns)} значений ({', '.join(data_columns)}), "
            f"получено {len(values)}"
        )

    rows = load_table_data(table_name)
    new_id = max((row['ID'] for row in rows), default=0) + 1

    row = {'ID': new_id}
    for col_name, value in zip(data_columns, values):
        row[col_name] = check_value_type(col_name, columns[col_name], value)

    rows.append(row)
    return rows, new_id

def select(table_data, where_clause=None):
    """Возвращает записи, подходящие под условие (или все, если условия нет)."""
    if where_clause is None:
        return table_data
    return [row for row in table_data if _matches(row, where_clause)]

def update(table_data, set_clause, where_clause=None):
    """Обновляет поля set_clause в записях под условием. Возвращает (данные, ID изменённых)."""
    if 'ID' in set_clause:
        raise ValueError("ID изменять нельзя")
    updated_ids = []
    for row in table_data:
        if where_clause is None or _matches(row, where_clause):
            row.update(set_clause)
            updated_ids.append(row['ID'])
    return table_data, updated_ids

def delete(table_data, where_clause=None):
    """Удаляет записи под условием; без условия — все. Возвращает (данные, ID удалённых)."""
    kept, deleted_ids = [], []
    for row in table_data:
        if where_clause is None or _matches(row, where_clause):
            deleted_ids.append(row['ID'])
        else:
            kept.append(row)
    return kept, deleted_ids
