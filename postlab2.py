def read_file(filename):
    """Reads a file and returns its lines as a list."""
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        return lines
    except FileNotFoundError:
        print("Error: File not found.")
        return []

def navigate_lines(lines):
    """Allows user to navigate through the lines in the file."""
    while True:
        num_lines = len(lines)
        if num_lines == 0:
            print("No lines to display. Exiting.")
            break

        print(f"\nThe file has {num_lines} lines.")
        choice = input(f"Enter a line number (1-{num_lines}, or 0 to quit): ")

        if not choice.isdigit():
            print("Invalid input. Please enter a number.")
            continue

        choice = int(choice)

        if choice == 0:
            print("Exiting program.")
            break
        elif 1 <= choice <= num_lines:
            print(f"Line {choice}: {lines[choice - 1].strip()}")
        else:
            print("Invalid line number. Please enter a valid number.")

# Main program
filename = input("Enter the filename: ")
lines = read_file(filename)
navigate_lines(lines)
