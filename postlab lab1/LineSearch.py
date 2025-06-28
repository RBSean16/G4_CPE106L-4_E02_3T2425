def navigate_file_lines():
    filename = input("Enter the filename: ")

    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return

    total_lines = len(lines)
    print(f"The file '{filename}' has {total_lines} lines.")

    while True:
        try:
            line_number = int(input(f"Enter a line number (1 to {total_lines}, or 0 to quit): "))
            if line_number == 0:
                print("Exiting the program.")
                break
            elif 1 <= line_number <= total_lines:
                print(f"Line {line_number}: {lines[line_number - 1].strip()}")
            else:
                print(f"Invalid line number. Please enter a number between 1 and {total_lines}, or 0 to quit.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

# Run the program
navigate_file_lines()