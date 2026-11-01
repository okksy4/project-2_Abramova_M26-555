
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