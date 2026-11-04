import re

def parse_value(raw):
    """Разбирает значение: строки — в кавычках, числа и bool — без."""
    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        return raw[1:-1]
    if re.fullmatch(r'-?\d+', raw):
        return int(raw)
    if raw in ('true', 'false'):
        return raw == 'true'
    raise ValueError(f"Значение '{raw}' не распознано: строки должны быть в кавычках")

def parse_condition(condition_str):
    """'age = 28' -> {'age': 28}; 'name = "Иван"' -> {'name': 'Иван'}."""
    if '=' not in condition_str:
        raise ValueError(f"В условии '{condition_str}' нет '='")
    field, raw = condition_str.split('=', 1)
    field, raw = field.strip(), raw.strip()
    if not field.isidentifier():
        raise ValueError(f'Некорректное имя столбца: {field}')
    return {field: parse_value(raw)}

def split_outside_quotes(s):
    """Разбивает строку по запятым, не трогая запятые внутри кавычек."""
    return re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', s)

def parse_set(set_str):
    """'name = "Иванов, Иван", age = 30' -> {'name': 'Иванов, Иван', 'age': 30}."""
    result = {}
    for part in split_outside_quotes(set_str):
        if '=' not in part:
            raise ValueError(f"В set-условии '{part.strip()}' нет '='")
        field, raw = part.split('=', 1)
        field, raw = field.strip(), raw.strip()
        if not field.isidentifier():
            raise ValueError(f'Некорректное имя столбца: {field}')
        if field == 'ID':
            raise ValueError("ID изменять нельзя")
        result[field] = parse_value(raw)
    return result

def parse_values(values_str):
    """'( "Sergei", 28, true )' -> ['Sergei', 28, True]."""
    values_str = values_str.strip()
    if not (values_str.startswith('(') and values_str.endswith(')')):
        raise ValueError("Значения должны быть указаны в круглых скобках: values (...)")
    inner = values_str[1:-1].strip()
    if not inner:
        raise ValueError("Не передано ни одного значения")
    return [parse_value(part.strip()) for part in split_outside_quotes(inner)]
