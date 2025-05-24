import unittest
from gomoku import GomokuGame, DEFAULT_BOARD_SIZE

class TestGomoku(unittest.TestCase):
    def test_create_board(self):
        game = GomokuGame()
        self.assertEqual(len(game.board), game.board_size_internal, f"Board should have {game.board_size_internal} rows")
        for row in game.board:
            self.assertEqual(len(row), game.board_size_internal, f"Row should have {game.board_size_internal} columns")
            for cell in row:
                self.assertEqual(cell, ' ', f"Cell should be empty (' '), but got '{cell}'")

        # Test with a different board size
        custom_size = 10
        game_custom = GomokuGame(board_size=custom_size)
        self.assertEqual(len(game_custom.board), custom_size, f"Board should have {custom_size} rows")
        self.assertEqual(game_custom.board_size_internal, custom_size, "Internal board size should be custom_size")
        for row in game_custom.board:
            self.assertEqual(len(row), custom_size, f"Row should have {custom_size} columns")


    def test_make_move(self):
        game = GomokuGame()
        
        # Test Player X's move
        game.current_player = 'X'
        self.assertTrue(game.make_move(0, 0), "make_move should return True for a valid move")
        self.assertEqual(game.board[0][0], 'X', "Cell (0,0) should contain 'X'")

        # Test Player O's move
        game.current_player = 'O'
        last_idx = game.board_size_internal - 1
        self.assertTrue(game.make_move(last_idx, last_idx), "make_move should return True for a valid move")
        self.assertEqual(game.board[last_idx][last_idx], 'O', f"Cell ({last_idx},{last_idx}) should contain 'O'")

        # Test invalid move (cell taken)
        game.current_player = 'X'
        self.assertFalse(game.make_move(0, 0), "make_move should return False for a taken cell")
        self.assertEqual(game.board[0][0], 'X', "Cell (0,0) should still contain 'X'")

        # Test invalid move (out of bounds)
        self.assertFalse(game.make_move(-1, 0), "make_move should return False for out-of-bounds row")
        self.assertFalse(game.make_move(0, game.board_size_internal), "make_move should return False for out-of-bounds col")


    def test_check_win_horizontal(self):
        game = GomokuGame()
        game.current_player = 'X'
        for i in range(5):
            game.board[0][i] = 'X' # X wins horizontally at row 0
        self.assertTrue(game.check_win(), "Player X should win with 5 horizontal marks")
        
        game_o_incomplete = GomokuGame()
        game_o_incomplete.current_player = 'O'
        for i in range(4):
            game_o_incomplete.board[1][i] = 'O' # O has 4 horizontal marks
        self.assertFalse(game_o_incomplete.check_win(), "Player O should not win with 4 horizontal marks")

    def test_check_win_vertical(self):
        game = GomokuGame()
        game.current_player = 'X'
        for i in range(5):
            game.board[i][0] = 'X' # X wins vertically at col 0
        self.assertTrue(game.check_win(), "Player X should win with 5 vertical marks")

    def test_check_win_diagonal_tl_br(self): # Top-Left to Bottom-Right
        game = GomokuGame()
        game.current_player = 'X'
        for i in range(5):
            game.board[i][i] = 'X' # X wins diagonally (TL-BR)
        self.assertTrue(game.check_win(), "Player X should win with 5 diagonal TL-BR marks")

    def test_check_win_diagonal_tr_bl(self): # Top-Right to Bottom-Left
        game = GomokuGame()
        game.current_player = 'X'
        for i in range(5):
            game.board[i][4-i] = 'X' # X wins diagonally (TR-BL) e.g. (0,4), (1,3)...(4,0)
        self.assertTrue(game.check_win(), "Player X should win with 5 diagonal TR-BL marks")

    def test_check_win_no_win(self):
        game = GomokuGame()
        
        game.board[0][0] = 'X'
        game.board[0][1] = 'O'
        game.board[0][2] = 'X'
        game.board[1][0] = 'O'
        game.board[1][1] = 'X'
        
        game.current_player = 'X'
        self.assertFalse(game.check_win(), "Should be no win for X")
        
        game.current_player = 'O'
        self.assertFalse(game.check_win(), "Should be no win for O")

    def test_check_draw(self):
        # Empty board
        game_empty = GomokuGame()
        self.assertFalse(game_empty.check_draw(), "Empty board should not be a draw")

        # Partially filled board
        game_partial = GomokuGame()
        game_partial.board[0][0] = 'X'
        game_partial.board[0][1] = 'O'
        self.assertFalse(game_partial.check_draw(), "Partially filled board should not be a draw")

        # Full board
        game_full = GomokuGame()
        for r in range(game_full.board_size_internal):
            for c in range(game_full.board_size_internal):
                if (r + c) % 2 == 0:
                    game_full.board[r][c] = 'X'
                else:
                    game_full.board[r][c] = 'O'
        
        # First, ensure no accidental winner for a robust draw test (optional, depends on pattern)
        # For this specific alternating pattern on a 15x15 board, a winner is unlikely, but possible
        # game_full.current_player = 'X'
        # if game_full.check_win(): print("Warning: Full board test pattern created a win for X")
        # game_full.current_player = 'O'
        # if game_full.check_win(): print("Warning: Full board test pattern created a win for O")

        self.assertTrue(game_full.check_draw(), "Full board should be a draw")
        
        # Test draw on a smaller board for easier verification
        game_small_full = GomokuGame(board_size=3)
        game_small_full.board = [
            ['X', 'O', 'X'],
            ['O', 'X', 'O'],
            ['O', 'X', 'O'] # No winner here
        ]
        game_small_full.current_player = 'X' # Assume X made the last move
        self.assertFalse(game_small_full.check_win(), "Small full board should not have X as winner for this pattern")
        game_small_full.current_player = 'O'
        self.assertFalse(game_small_full.check_win(), "Small full board should not have O as winner for this pattern")
        self.assertTrue(game_small_full.check_draw(), "Small full board should be a draw")


    def test_check_win_edge_cases(self):
        game = GomokuGame()
        board_size = game.board_size_internal

        # Horizontal win at the bottom edge
        game.reset_game() # Ensure clean board
        game.current_player = 'X'
        for i in range(5):
            game.board[board_size - 1][i] = 'X'
        self.assertTrue(game.check_win(), "X should win horizontally at bottom edge")

        # Vertical win at the right edge
        game.reset_game()
        game.current_player = 'O'
        for i in range(5):
            game.board[i][board_size - 1] = 'O'
        self.assertTrue(game.check_win(), "O should win vertically at right edge")
        
        # Diagonal TL-BR win ending at bottom-right edge
        game.reset_game()
        game.current_player = 'X'
        for i in range(5):
            game.board[(board_size - 5) + i][(board_size - 5) + i] = 'X'
        self.assertTrue(game.check_win(), "X should win TL-BR diagonal at BR edge")

        # Diagonal TR-BL win ending at bottom-left edge (e.g. for 15x15, starting at (10,4) -> (14,0))
        game.reset_game()
        game.current_player = 'O'
        for i in range(5):
            # E.g., for 15x15, (10,4), (11,3), (12,2), (13,1), (14,0)
            # For a generic board_size, this means starting row = board_size - 5, starting col = 4
            if board_size >= 5: # Ensure this test is valid for the board size
                 game.board[(board_size - 5) + i][4 - i] = 'O'
        if board_size >=5: # Only assert if the board was large enough for the pattern
            self.assertTrue(game.check_win(), "O should win TR-BL diagonal at BL edge")
        else:
            self.assertFalse(game.check_win(), "O should not win TR-BL on a board too small for this pattern")


    def test_switch_player(self):
        game = GomokuGame()
        self.assertEqual(game.current_player, 'X', "Initial player should be X")
        game.switch_player()
        self.assertEqual(game.current_player, 'O', "Player should be O after one switch")
        game.switch_player()
        self.assertEqual(game.current_player, 'X', "Player should be X after two switches")

    def test_reset_game(self):
        game = GomokuGame()
        
        # Make some moves
        game.current_player = 'X'
        game.make_move(0,0)
        game.current_player = 'O'
        game.make_move(0,1)
        game.game_over = True # Simulate game end
        
        game.reset_game()
        
        self.assertEqual(game.board[0][0], ' ', "Cell (0,0) should be empty after reset")
        self.assertEqual(game.board[0][1], ' ', "Cell (0,1) should be empty after reset")
        self.assertEqual(game.current_player, 'X', "Current player should be 'X' after reset")
        self.assertFalse(game.game_over, "game_over should be False after reset")
        
        # Check if board is entirely empty
        for r in range(game.board_size_internal):
            for c in range(game.board_size_internal):
                self.assertEqual(game.board[r][c], ' ', f"Cell ({r},{c}) should be empty after reset.")

    def test_board_size_default(self):
        game = GomokuGame()
        self.assertEqual(game.board_size_internal, DEFAULT_BOARD_SIZE, f"Default board size should be {DEFAULT_BOARD_SIZE}")
        self.assertEqual(len(game.board), DEFAULT_BOARD_SIZE)

if __name__ == '__main__':
    unittest.main()
