import shlex
from .core import create_table, drop_table
from .utils import load_metadata, save_metadata

def print_help():
    """
    Выводит справочную информацию по доступным командам.
    
    Содержит список всех доступных команд и их краткое описание.
    """
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n") 

METADATA_FILE = 'db_meta.json'

def run():
    """
    Основная функция запуска приложения.
    
    Отвечает за:
    - загрузку метаданных
    - обработку пользовательского ввода
    - выполнение команд
    - сохранение изменений
    """
    metadata = load_metadata(METADATA_FILE)
    
    while True:
        try:
            command = input(">>>Введите команду: ")
            args = shlex.split(command)
            
            if not args:
                continue
                
            command = args[0]
            
            valid_commands = ['create_table', 'drop_table', 'list_tables', 'help', 'exit']
            if command not in valid_commands:
                print(f"Функции {command} нет. Попробуйте снова.")
                continue
                
            if command == 'create_table':
                if len(args) < 3:
                    print("Недостаточно аргументов для команды create_table")
                    continue
                    
                table_name = args[1]
                columns = [tuple(arg.split(':')) for arg in args[2:]]
                
                try:
                    metadata = create_table(metadata, table_name, columns)
                    save_metadata(METADATA_FILE, metadata)
    
                    columns_str = ', '.join([f"{name}:{type}" for name, type in columns])
                    print(f"Таблица \"{table_name}\" успешно создана со столбцами: {columns_str}")
                
                except ValueError as e:
                    if "Недопустимый тип данных" in str(e):
                        print(f"Некорректное значение: {e}")
                    else:
                        print(f"Ошибка: {e}")
                   
            elif command == 'drop_table':
                if len(args) != 2:
                    print("Неверный формат команды drop_table")
                    continue
                    
                table_name = args[1]
                try:
                    metadata = drop_table(metadata, table_name)
                    save_metadata(METADATA_FILE, metadata)
                    print(f"Таблица \"{table_name}\" успешно удалена")
                except ValueError as e:
                    print(f"Ошибка: {e}")
                    
            elif command == 'list_tables':
                tables = metadata.get('tables', {}).keys()
                if not tables:
                    print("Таблицы отсутствуют")
                else:
                    print("Список таблиц:")
                    for table in tables:
                        print(f"- \"{table}\"")

            elif command == 'help':
                print_help()
                
            elif command == 'exit':
                print("До свидания!")
                break
                
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")