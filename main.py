
def command_loop():
    while True:
        command = input('>>> ').strip().lower()
        
        if command == 'stats':
            pass
        elif command == 'spell':
            pass
        else:
            print(f"Unknown command : '{command}'")
        
        print()

if __name__ == '__main__':
    try:
        command_loop()
    except KeyboardInterrupt:
        print('\nExiting...')

