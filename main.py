from manager import Manager

def manager_print(code, message):
    print(f"{'[ERROR] ' if code == 1 else ''}{message}")

def command_loop(manager: Manager):

    while True:
        command = input('>>> ').strip().lower()

        if command == 'q':
            manager.save()
            break

        if command:
            manager.execute_command(command)

        print()

if __name__ == '__main__':
    manager = Manager(manager_print)

    try:
        command_loop(manager)
    except KeyboardInterrupt:
        manager.save()
        print('\nExiting...')

