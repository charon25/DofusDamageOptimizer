from manager import Manager
from stuff_manager import StuffManager


def manager_print(code, message):
    print(f"{'[ERROR] ' if code == 1 else ''}{message}")

def command_loop(manager: Manager, stuff_manager: StuffManager):
    mode = 'stuff' # TODO change 'base'

    while True:
        if mode == 'base':
            try:
                command = input('>>> ').strip().lower()
            except KeyboardInterrupt: # If user uses Ctrl C, prompt for another one
                print()
                continue

            if command == 'q':
                manager.save(save_cache=True)
                break
            elif command == 'stuff':
                manager.save(False)
                mode = 'stuff'
                continue

            if command:
                try:
                    manager.execute_command(command)
                except Exception as e:
                    print(f"Error while executing command {command}: {e}")

        elif mode == 'stuff':
            try:
                command = input('[stuff] >>> ').strip().lower()
            except KeyboardInterrupt: # If user uses Ctrl C, prompt for another one
                print()
                continue

            if command == 'q':
                manager.save(save_cache=True)
                break
            elif command == 'exit':
                mode = 'base'
                continue

            if command:
                try:
                    stuff_manager.execute_command(command)
                except Exception as e:
                    print(f"Error while executing stuff command {command}: {e}")

        print()

if __name__ == '__main__':
    manager = Manager(manager_print)
    stuff_manager = StuffManager(manager_print, manager)

    try:
        command_loop(manager, stuff_manager)
    except (KeyboardInterrupt, EOFError):
        print('\nExiting...')
        manager.save(save_cache=True)

