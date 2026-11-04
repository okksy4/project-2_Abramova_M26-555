import json
import os

DATA_DIR = "data"


def load_metadata(filepath):
    """Загружает метаданные из JSON-файла.

    Если файла нет или он повреждён — возвращает пустую структуру.
    """
    if not os.path.exists(filepath):
        return {"tables": {}}
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("Некорректные метаданные")
        if "tables" not in data:
            data["tables"] = {}
        return data
    except (json.JSONDecodeError, ValueError, IOError) as e:
        print(f"Ошибка при загрузке метаданных: {e}")
        return {"tables": {}}


def save_metadata(filepath: str, data: dict) -> None:
    """
    Сохраняет метаданные в JSON-файл.

    Args:
        filepath (str): путь к файлу для сохранения
        data (dict): словарь с метаданными для сохранения
    """
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    """Загружает данные таблицы из data/<table_name>.json."""
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError("Некорректные данные таблицы")
    return data


def save_table_data(table_name: str, data: list) -> None:
    """Сохраняет данные таблицы в data/<table_name>.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
