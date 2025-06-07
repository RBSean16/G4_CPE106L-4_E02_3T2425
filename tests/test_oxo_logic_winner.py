import unittest
import oxo_logic

class TestOxoWinner(unittest.TestCase):
    def test_x_wins_row(self):
        game = ['X', 'X', 'X', ' ', ' ', ' ', ' ', ' ', ' ']
        self.assertTrue(oxo_logic._isWinningMove(game))

    def test_o_wins_column(self):
        game = ['O', ' ', ' ', 'O', ' ', ' ', 'O', ' ', ' ']
        self.assertTrue(oxo_logic._isWinningMove(game))

    def test_x_wins_diagonal(self):
        game = ['X', ' ', ' ', ' ', 'X', ' ', ' ', ' ', 'X']
        self.assertTrue(oxo_logic._isWinningMove(game))

    def test_no_winner(self):
        game = ['X', 'O', 'X', 'X', 'O', 'O', 'O', 'X', 'X']
        self.assertFalse(oxo_logic._isWinningMove(game))

    def test_user_move_detects_win(self):
        game = ['X', 'X', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
        result = oxo_logic.userMove(game, 2)
        self.assertEqual(result, 'X')

    def test_computer_move_detects_win(self):
        # Set up so computer can win by moving to cell 2
        game = ['O', 'O', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
        # Patch _generateMove to always pick 2
        oxo_logic._generateMove = lambda g: 2
        result = oxo_logic.computerMove(game)
        self.assertEqual(result, 'O')

if __name__ == '__main__':
    unittest.main()