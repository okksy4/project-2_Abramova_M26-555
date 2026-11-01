import shlex
from .core import create_table, drop_table
from .utils import load_metadata, save_metadata

def welcome():
    print("project")
    print("Первая попытка запустить проект!")
    print("***")
    while True:
        cmd = input("<command> exit - выйти из программы\n<command> help - справочная информация\nВведите команду: ")
        if cmd == "exit":
            break
        elif cmd == "help":
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            print("Неизвестная команда. Введите 'help' для справки.")

def print_help():
    """Prints the help message for the current mode."""
   
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
    metadata = load_metadata(METADATA_FILE)
    
    while True:
        try:
            print("\nВведите команду:")
            user_input = input(">>> ")
            args = shlex.split(user_input)
            
            if not args:
                continue
                
            command = args[0]
            
            if command == 'exit':
                break
                
            elif command == 'help':
                print_help()
                
            elif command == 'create_table':
                if len(args) < 3:
                    print("Недостаточно аргументов")
                    continue
                    
                table_name = args[1]
                columns = [tuple(arg.split(':')) for arg in args[2:]]
                
                try:
                    metadata = create_table(metadata, table_name, columns)
                    save_metadata(METADATA_FILE, metadata)
                    print(f"Таблица {table_name} успешно создана")
                except ValueError as e:
                    print(f"Ошибка: {e}")
                    
            elif command == 'drop_table':
                if len(args) != 2:
                    print("Неверный формат команды")
                    continue
                    
                table_name = args[1]
                try:
                    metadata = drop_table(metadata, table_name)
                    save_metadata(METADATA_FILE, metadata)
                    print(f"Таблица {table_name} успешно удалена")
                except ValueError as e:
                    print(f"Ошибка: {e}")
                    
            elif command == 'list_tables':
                tables = metadata.get('tables', {}).keys()
                print("Список таблиц:")
                for table in tables:
                    print(f"- {table}")
                    
            else:
                print("Неизвестная команда. Введите 'help' для справки")
                
        except Exception as e:
            print(f"Произошла ошибка: {e}")