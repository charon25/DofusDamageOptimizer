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
            # try:
                manager.execute_command(command)
            # except Exception as e:
            #     print(f"Error while executing command {command}: {e}")

        print()

if __name__ == '__main__':
    manager = Manager(manager_print)

    try:
        command_loop(manager)
    except KeyboardInterrupt:
        print('\nExiting...')
        manager.save()

