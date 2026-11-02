VALID_TYPES = {'int', 'str', 'bool'}

def create_table(metadata, table_name, columns):
    """
    Создает новую таблицу в базе данных.
    
    Функция проверяет существование таблицы, валидность имени,
    добавляет столбец ID при необходимости и сохраняет метаданные.
    
    Args:
        metadata (dict): текущие метаданные базы данных
        table_name (str): имя создаваемой таблицы
        columns (list): список кортежей (имя_столбца, тип_данных)
        
    Returns:
        dict: обновленные метаданные с новой таблицей
        
    Raises:
        ValueError: при различных ошибках валидации
    """
    if 'tables' not in metadata:
        metadata['tables'] = {}
    
    # Правильная проверка существования
    if table_name in metadata['tables']:
        raise ValueError(f"Таблица {table_name} уже существует")
        
    # Проверяем корректность имени таблицы
    if not table_name.isidentifier():
        raise ValueError("Некорректное имя таблицы")

    if len(table_name) > 50:
        raise ValueError("Имя таблицы не может превышать 50 символов")

    if not table_name:
        raise ValueError("Имя таблицы не может быть пустым")
    
    # Проверяем наличие ID среди существующих столбцов
    column_names = [col[0] for col in columns]
    
    # Добавляем ID только если его нет
    if 'ID' not in column_names:
        columns.insert(0, ('ID', 'int'))
    else:
        # Проверяем тип существующего ID
        id_index = column_names.index('ID')
        id_type = columns[id_index][1]
        if id_type != 'int':
            raise ValueError("Столбец ID должен иметь тип int")
    
    # Проверяем уникальность имён столбцов
    column_names = [col[0] for col in columns]
    if len(column_names) != len(set(column_names)):
        raise ValueError("Имена столбцов должны быть уникальными")
    
    # Проверяем корректность имён столбцов
    for col_name in column_names:
        if not col_name.isidentifier():
            raise ValueError(f"Некорректное имя столбца: {col_name}")
    
    # Проверяем типы данных
    for col_name, col_type in columns:
        if col_type not in VALID_TYPES:
            raise ValueError(f"Некорректное значение: {col_type}. Допустимые типы: int, str, bool")
    
    # Создаем запись в метаданных
    metadata['tables'][table_name] = {
        'columns': {col_name: col_type for col_name, col_type in columns}
    }
    return metadata


def drop_table(metadata, table_name):
    """
    Удаляет таблицу из базы данных.
    
    Функция проверяет существование таблицы и удаляет её
    из метаданных, если она существует.
    
    Args:
        metadata (dict): текущие метаданные базы данных
        table_name (str): имя удаляемой таблицы
        
    Returns:
        dict: обновленные метаданные без удаленной таблицы
        
    Raises:
        ValueError: если таблица не существует
    """
    if not table_name.isidentifier():
        raise ValueError("Некорректное имя таблицы")
    
    if table_name not in metadata.get('tables', {}):
        raise ValueError(f"Таблица \"{table_name}\" не существует")
    
    if 'tables' not in metadata:
        raise ValueError("Нет таблиц для удаления")
    
    del metadata['tables'][table_name]
    
    if not metadata['tables']:
        metadata.pop('tables', None)
    
    return metadata