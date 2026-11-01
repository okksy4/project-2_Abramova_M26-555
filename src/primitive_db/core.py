VALID_TYPES = {'int', 'str', 'bool'}

def create_table(metadata, table_name, columns):
    # Проверяем существование таблицы
    if table_name in metadata['tables']:
        raise ValueError(f"Таблица {table_name} уже существует")
    
    # Добавляем ID в начало
    columns.insert(0, ('ID', 'int'))
    
    # Проверяем типы данных
    for col_name, col_type in columns:
        if col_type not in VALID_TYPES:
            raise ValueError(f"Недопустимый тип данных: {col_type}")
    
    # Создаем запись в метаданных
    metadata['tables'][table_name] = {
        'columns': [col[0] for col in columns],
        'types': [col[1] for col in columns]
    }
    return metadata

def drop_table(metadata, table_name):
    if table_name not in metadata['tables']:
        raise ValueError(f"Таблица {table_name} не существует")
    
    del metadata['tables'][table_name]
    return metadata
