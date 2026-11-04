import shlex

from prettytable import PrettyTable

from .core import (
    check_value_type,
    create_table,
    delete,
    drop_table,
    insert,
    select,
    update,
)
from .parser import parse_condition, parse_set, parse_values
from .utils import load_metadata, load_table_data, save_metadata, save_table_data

METADATA_FILE = "db_meta.json"


def print_help():
    """Выводит справочную информацию по доступным командам."""
    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, ...) - создать запись"
    )
    print(
        "<command> select from <имя_таблицы> "
        "[where <столбец> = <значение>] - прочитать записи"
    )
    print(
        "<command> update <имя_таблицы> set <столбец> = <значение> "
        "where <столбец> = <значение> - обновить запись"
    )
    print(
        "<command> delete from <имя_таблицы> "
        "where <столбец> = <значение> - удалить запись"
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_table(column_names, rows):
    """Печатает записи в виде PrettyTable."""
    if not rows:
        print("Нет записей")
        return
    table = PrettyTable()
    table.field_names = column_names
    for row in rows:
        table.add_row([row[c] for c in column_names])
    print(table)


def check_table(metadata, table_name):
    """Проверяет существование таблицы."""
    if table_name not in metadata["tables"]:
        raise ValueError(f'Таблица "{table_name}" не существует')


def check_columns(columns, names, table_name):
    """Проверяет, что столбцы существуют в таблице."""
    for name in names:
        if name not in columns:
            raise ValueError(f'Столбец "{name}" не существует в таблице "{table_name}"')


def validate_where(where_clause, columns, table_name):
    """Проверяет столбец и тип значения условия where."""
    field, value = next(iter(where_clause.items()))
    check_columns(columns, [field], table_name)
    check_value_type(field, columns[field], value)


def run():
    """Загружает метаданные и обрабатывает команды пользователя."""
    metadata = load_metadata(METADATA_FILE)

    while True:
        try:
            line = input(">>>Введите команду: ").strip()
            if not line:
                continue

            # posix=False сохраняет кавычки значений ("Sergei" остается с кавычками)
            args = shlex.split(line, posix=False)
            command = args[0]

            if command == "exit":
                print("До свидания!")
                break

            elif command == "help":
                print_help()

            elif command == "create_table":
                if len(args) < 3:
                    raise ValueError("Недостаточно аргументов для команды create_table")
                table_name = args[1]
                columns = [tuple(arg.split(":")) for arg in args[2:]]
                new_metadata = create_table(metadata, table_name, columns)
                if new_metadata is None:
                    continue
                metadata = new_metadata
                save_metadata(METADATA_FILE, metadata)
                cols_str = ", ".join(
                    f"{name}:{col_type}"
                    for name, col_type in metadata["tables"][table_name][
                        "columns"
                    ].items()
                )
                print(
                    f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}'
                )

            elif command == "drop_table":
                if len(args) != 2:
                    raise ValueError("Неверный формат команды drop_table")
                new_metadata = drop_table(metadata, args[1])
                if new_metadata is None:
                    continue
                metadata = new_metadata
                save_metadata(METADATA_FILE, metadata)
                print(f'Таблица "{args[1]}" успешно удалена')

            elif command == "list_tables":
                tables = metadata.get("tables", {}).keys()
                if not tables:
                    print("Таблицы отсутствуют")
                else:
                    print("Список таблиц:")
                    for table in tables:
                        print(f'- "{table}"')

            elif command == "insert":
                if len(args) < 4 or args[1] != "into" or "values" not in args[3:]:
                    raise ValueError(
                        "Неверный формат: insert into <таблица> values (<значения>)"
                    )
                table_name = args[2]
                idx = args.index("values", 3)
                values = parse_values(" ".join(args[idx + 1 :]))
                result = insert(metadata, table_name, values)
                if result is None:
                    continue
                rows, new_id = result
                save_table_data(table_name, rows)
                print(
                    f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".'
                )

            elif command == "select":
                if len(args) < 3 or args[1] != "from":
                    raise ValueError(
                        "Неверный формат: select from <таблица> "
                        "[where <столбец> = <значение>]"
                    )
                table_name = args[2]
                check_table(metadata, table_name)
                columns = metadata["tables"][table_name]["columns"]

                where_clause = None
                if len(args) > 3:
                    if args[3] != "where":
                        raise ValueError(
                            "Неверный формат: select from <таблица> "
                            "[where <столбец> = <значение>]"
                        )
                    where_clause = parse_condition(" ".join(args[4:]))
                    validate_where(where_clause, columns, table_name)

                rows = select(load_table_data(table_name), where_clause, table_name)
                if rows is None:
                    continue
                print_table(list(columns), rows)

            elif command == "update":
                if len(args) < 4 or args[2] != "set" or "where" not in args:
                    raise ValueError(
                        "Неверный формат: update <таблица> set <столбец> "
                        "= <значение> where <столбец> = <значение>"
                    )
                table_name = args[1]
                check_table(metadata, table_name)
                columns = metadata["tables"][table_name]["columns"]

                idx_set = args.index("set")
                idx_where = args.index("where")
                set_clause = parse_set(" ".join(args[idx_set + 1 : idx_where]))
                for name, value in set_clause.items():
                    check_columns(columns, [name], table_name)
                    check_value_type(name, columns[name], value)

                where_clause = parse_condition(" ".join(args[idx_where + 1 :]))
                validate_where(where_clause, columns, table_name)

                rows, updated_ids = update(
                    load_table_data(table_name), set_clause, where_clause
                )
                save_table_data(table_name, rows)
                if len(updated_ids) == 1:
                    print(
                        f"Запись с ID={updated_ids[0]} в таблице "
                        f'"{table_name}" успешно обновлена.'
                    )
                else:
                    ids_str = ", ".join(map(str, updated_ids))
                    print(f"Обновлено записей: {len(updated_ids)} (ID: {ids_str}).")

            elif command == "delete":
                if len(args) < 3 or args[1] != "from":
                    raise ValueError(
                        "Неверный формат: delete from <таблица> "
                        "where <столбец> = <значение>"
                    )
                table_name = args[2]
                check_table(metadata, table_name)
                columns = metadata["tables"][table_name]["columns"]

                where_clause = None
                if len(args) > 3:
                    if args[3] != "where":
                        raise ValueError(
                            "Неверный формат: delete from <таблица> "
                            "where <столбец> = <значение>"
                        )
                    where_clause = parse_condition(" ".join(args[4:]))
                    validate_where(where_clause, columns, table_name)

                result = delete(load_table_data(table_name), where_clause)
                if result is None:
                    continue
                rows, deleted_ids = result
                save_table_data(table_name, rows)
                
                if rows is None:
                    continue
                save_table_data(table_name, rows)
                if len(deleted_ids) == 1:
                    print(
                        f"Запись с ID={deleted_ids[0]} успешно удалена "
                        f'из таблицы "{table_name}".'
                    )
                else:
                    ids_str = ", ".join(map(str, deleted_ids))
                    print(f"Удалено записей: {len(deleted_ids)} (ID: {ids_str}).")

            elif command == "info":
                if len(args) != 2:
                    raise ValueError("Неверный формат: info <таблица>")
                table_name = args[1]
                check_table(metadata, table_name)
                columns = metadata["tables"][table_name]["columns"]
                print(f"Таблица: {table_name}")
                print("Столбцы: " + ", ".join(f"{n}:{t}" for n, t in columns.items()))
                print(f"Количество записей: {len(load_table_data(table_name))}")

            else:
                print(f"Функции {command} нет. Попробуйте снова.")

        except (KeyboardInterrupt, EOFError):
            print()
            break
        except FileNotFoundError:
            print("Ошибка: файл базы данных не найден")
        except OSError:
            print("Ошибка: не удалось сохранить или прочитать файл")
        except ValueError as e:
            print(f"Ошибка: {e}")
