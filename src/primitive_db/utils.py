import os
import json
from typing import Dict, Any

def load_metadata(filepath: str) -> dict:
    """
    Загружает метаданные из JSON-файла.
    
    Args:
        filepath (str): путь к файлу с метаданными
        
    Returns:
        dict: загруженные метаданные или пустой словарь
        
    Raises:
        IOError: при ошибке чтения файла
    """
    if not os.path.exists(filepath):
        return {"tables": {}}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
            # Проверка целостности
            if not isinstance(data, dict):
                raise ValueError("Некорректные метаданные")
            
            if 'tables' not in data:
                data['tables'] = {}
                
            return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Ошибка при загрузке метаданных: {e}")
        return {"tables": {}}

def save_metadata(filepath: str, data: dict) -> None:
    """
    Сохраняет метаданные в JSON-файл.
    
    Args:
        filepath (str): путь к файлу для сохранения
        data (dict): словарь с метаданными для сохранения
        
    Raises:
        IOError: при ошибке записи файла
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Ошибка при записи файла: {e}")
        raise