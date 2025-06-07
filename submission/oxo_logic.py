import os
import random
import oxo_data

class Game:
    def __init__(self):
        """Initialize a new game board."""
        self.board = [" "] * 9

    def save_game(self):
        """Save the current game state."""
        oxo_data.saveGame(self.board)
    
    def restore_game(self):
        """Restore a previously saved game."""
        try:
            game = oxo_data.restoreGame()
            if len(game) == 9:
                self.board = game
            else:
                self.board = [" "] * 9
        except IOError:
            self.board = [" "] * 9

    def _generate_move(self):
        """Generate a random available move. Return -1 if no moves available."""
        options = [i for i in range(len(self.board)) if self.board[i] == " "]
        return random.choice(options) if options else -1

    def _is_winning_move(self):
        """Check if the current board contains a winning combination."""
        wins = ((0,1,2), (3,4,5), (6,7,8),
                (0,3,6), (1,4,7), (2,5,8),
                (0,4,8), (2,4,6))

        for a, b, c in wins:
            chars = self.board[a] + self.board[b] + self.board[c]
            if chars == 'XXX' or chars == 'OOO':
                return True
        return False

    def user_move(self, cell):
        """Process the user's move. Raise ValueError if the cell is occupied."""
        if self.board[cell] != ' ':
            raise ValueError('Invalid cell')
        self.board[cell] = 'X'
        
        return 'X' if self._is_winning_move() else ""

    def computer_move(self):
        """Process the computer's move."""
        cell = self._generate_move()
        if cell == -1:
            return 'D'  # Game draw
        
        self.board[cell] = 'O'
        return 'O' if self._is_winning_move() else ""

    def display_board(self):
        """Print the game board in a readable format."""
        print(f"""
          {self.board[0]} | {self.board[1]} | {self.board[2]} 
         ---------
          {self.board[3]} | {self.board[4]} | {self.board[5]} 
         ---------
          {self.board[6]} | {self.board[7]} | {self.board[8]} 
        """)

# Test function for debugging
def test():
    game = Game()
    result = ""

    while not result:
        game.display_board()
        try:
            result = game.user_move(game._generate_move())
        except ValueError:
            print("Oops, that shouldn't happen")

        if not result:
            result = game.computer_move()
        
        if result:
            if result == 'D':
                print("It's a draw!")
            else:
                print(f"Winner is: {result}")
        game.display_board()

if __name__ == "__main__":
    test()
