import json
from typing import Dict, Any

def load_metadata(filepath: str) -> Dict[str, Any]:
    """
    Загружает метаданные из JSON-файла.
    
    Если файл не найден, возвращает пустой словарь.
    
    Args:
        filepath: путь к файлу с метаданными
        
    Returns:
        словарь с метаданными или пустой словарь
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON. Возвращается пустой словарь.")
        return {}

def save_metadata(filepath: str, data: Dict[str, Any]) -> None:
    """
    Сохраняет метаданные в JSON-файл.
    
    Args:
        filepath: путь к файлу для сохранения
        data: словарь с метаданными
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Ошибка при записи файла: {e}")