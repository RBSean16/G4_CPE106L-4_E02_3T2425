from oxo_logic import Game
import argparse as ap

menu = ["Start new game",
        "Resume saved game",
        "Display help",
        "Quit"]

def get_menu_choice(a_menu):
    """Display a numbered menu and loop until user selects a valid number."""
    if not a_menu:
        raise ValueError('No menu content')

    while True:
        for index, item in enumerate(a_menu, start=1):
            print(index, "\t", item)
        try:
            choice = int(input("\nChoose a menu option: "))
            if 1 <= choice <= len(a_menu):
                return choice
            else:
                print("Choose a number between 1 and", len(a_menu))
        except ValueError:
            print("Choose the number of a menu option")


def start_game():
    """Start a new game and return a Game instance."""
    return Game()


def resume_game():
    """Restore a saved game and return a Game instance."""
    game = Game()
    game.restore_game()
    return game


def display_help():
    print('''
    Start new game:  starts a new game of tic-tac-toe
    Resume saved game: restores the last saved game and commences play
    Display help: shows this page
    Quit: quits the application
    ''')


def quit_game():
    print("Goodbye...")
    raise SystemExit


def execute_choice(choice):
    """Execute the selected menu option."""
    dispatch = [start_game, resume_game, display_help, quit_game]
    game = dispatch[choice - 1]()
    
    if isinstance(game, Game):
        play_game(game)


def print_game(game):
    """Display the current game board."""
    display = f"""
      1 | 2 | 3      {game.board[0]} | {game.board[1]} | {game.board[2]}
     ----------     -----------
      4 | 5 | 6      {game.board[3]} | {game.board[4]} | {game.board[5]}
      ---------     -----------
      7 | 8 | 9      {game.board[6]} | {game.board[7]} | {game.board[8]}
    """
    print(display)


def play_game(game):
    """Handle the game loop."""
    result = ""
    
    while not result:
        print_game(game)
        choice = input("Cell[1-9 or q to quit]: ")
        
        if choice.lower()[0] == 'q':
            save = input("Save game before quitting?[y/n] ")
            if save.lower()[0] == 'y':
                game.save_game()
            quit_game()
        else:
            try:
                cell = int(choice) - 1
                if not (0 <= cell <= 8):  # Validate range
                    raise ValueError
            except ValueError:
                print("Choose a number between 1 and 9 or 'q' to quit ")
                continue

            try:
                result = game.user_move(cell)
            except ValueError:
                print("Choose an empty cell")
                continue
            
            if not result:
                result = game.computer_move()
            
            if result:
                print_game(game)
                if result == 'D':
                    print("It's a draw!")
                else:
                    print(f"Winner is {result}\n")


def main():
    """Main function to handle command-line arguments."""
    parser = ap.ArgumentParser(description="Play a game of Tic-Tac-Toe")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-n", "--new", action='store_true', help="Start new game")
    group.add_argument("-r", "--res", "--restore", action='store_true', help="Restore old game")
    args = parser.parse_args()

    if args.new:
        execute_choice(1)
    elif args.res:
        execute_choice(2)
    else:
        while True:
            choice = get_menu_choice(menu)
            execute_choice(choice)


if __name__ == "__main__":
    main()
