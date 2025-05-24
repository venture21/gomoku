import unittest
from gomoku import create_board, make_move, check_win, check_draw, BOARD_SIZE

class TestGomoku(unittest.TestCase):
    def test_create_board(self):
        board = create_board()
        self.assertEqual(len(board), BOARD_SIZE, "Board should have BOARD_SIZE rows")
        for row in board:
            self.assertEqual(len(row), BOARD_SIZE, f"Row should have BOARD_SIZE columns: {row}")
            for cell in row:
                self.assertEqual(cell, ' ', f"Cell should be empty (' '), but got '{cell}'")

    def test_make_move(self):
        board = create_board()
        make_move(board, 0, 0, 'X')
        self.assertEqual(board[0][0], 'X', "Cell (0,0) should contain 'X' after make_move")
        make_move(board, BOARD_SIZE -1, BOARD_SIZE -1, 'O')
        self.assertEqual(board[BOARD_SIZE -1][BOARD_SIZE -1], 'O', "Cell (last,last) should contain 'O'")

    def test_check_win_horizontal(self):
        board = create_board()
        for i in range(5):
            make_move(board, 0, i, 'X') # X wins horizontally at row 0
        self.assertTrue(check_win(board, 'X'), "Player X should win with 5 horizontal marks")
        
        board_o_incomplete = create_board()
        for i in range(4):
            make_move(board_o_incomplete, 1, i, 'O') # O has 4 horizontal marks
        self.assertFalse(check_win(board_o_incomplete, 'O'), "Player O should not win with 4 horizontal marks")

    def test_check_win_vertical(self):
        board = create_board()
        for i in range(5):
            make_move(board, i, 0, 'X') # X wins vertically at col 0
        self.assertTrue(check_win(board, 'X'), "Player X should win with 5 vertical marks")

    def test_check_win_diagonal_tl_br(self): # Top-Left to Bottom-Right
        board = create_board()
        for i in range(5):
            make_move(board, i, i, 'X') # X wins diagonally (TL-BR)
        self.assertTrue(check_win(board, 'X'), "Player X should win with 5 diagonal TL-BR marks")

    def test_check_win_diagonal_tr_bl(self): # Top-Right to Bottom-Left
        board = create_board()
        for i in range(5):
            make_move(board, i, 4-i, 'X') # X wins diagonally (TR-BL) e.g. (0,4), (1,3)...(4,0)
        self.assertTrue(check_win(board, 'X'), "Player X should win with 5 diagonal TR-BL marks")

    def test_check_win_no_win(self):
        board = create_board()
        make_move(board, 0, 0, 'X')
        make_move(board, 0, 1, 'O')
        make_move(board, 0, 2, 'X')
        make_move(board, 1, 0, 'O')
        make_move(board, 1, 1, 'X')
        self.assertFalse(check_win(board, 'X'), "Should be no win for X")
        self.assertFalse(check_win(board, 'O'), "Should be no win for O")

    def test_check_draw(self):
        # Empty board
        board_empty = create_board()
        self.assertFalse(check_draw(board_empty), "Empty board should not be a draw")

        # Partially filled board
        board_partial = create_board()
        make_move(board_partial, 0, 0, 'X')
        make_move(board_partial, 0, 1, 'O')
        self.assertFalse(check_draw(board_partial), "Partially filled board should not be a draw")

        # Full board (no winner - this specific pattern might create a winner on 15x15,
        # but for check_draw, the primary goal is to test if it correctly identifies a full board.
        # A robust test for a "true draw game state" would also assert no winner.)
        board_full = create_board()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                # A simple pattern to fill the board
                if (r + c) % 2 == 0:
                    make_move(board_full, r, c, 'X')
                else:
                    make_move(board_full, r, c, 'O')
        
        # Assuming this pattern doesn't create a 5-in-a-row for 'X' or 'O'
        # which is likely for a 15x15 board with simple alternation.
        # If it does, check_draw should still be true if board is full.
        is_full = True
        for r_idx in range(BOARD_SIZE):
            for c_idx in range(BOARD_SIZE):
                if board_full[r_idx][c_idx] == ' ':
                    is_full = False
                    break
            if not is_full:
                break
        self.assertTrue(is_full, "Board must be full for this part of the draw test")
        # If the board is full, check_draw should be true, regardless of a winner.
        # The game logic in play_game() checks win before draw.
        self.assertTrue(check_draw(board_full), "Full board should be a draw")


    def test_check_win_edge_cases(self):
        # Horizontal win at the bottom edge
        board_h_edge = create_board()
        for i in range(5):
            make_move(board_h_edge, BOARD_SIZE - 1, i, 'X')
        self.assertTrue(check_win(board_h_edge, 'X'), "X should win horizontally at bottom edge")

        # Vertical win at the right edge
        board_v_edge = create_board()
        for i in range(5):
            make_move(board_v_edge, i, BOARD_SIZE - 1, 'O')
        self.assertTrue(check_win(board_v_edge, 'O'), "O should win vertically at right edge")
        
        # Diagonal TL-BR win ending at bottom-right edge
        board_d1_edge = create_board()
        for i in range(5):
            make_move(board_d1_edge, (BOARD_SIZE - 5) + i, (BOARD_SIZE - 5) + i, 'X')
        self.assertTrue(check_win(board_d1_edge, 'X'), "X should win TL-BR diagonal at BR edge")

        # Diagonal TR-BL win ending at bottom-left edge (e.g. for 15x15, starting at (10,4) -> (14,0))
        board_d2_edge = create_board()
        for i in range(5):
            make_move(board_d2_edge, (BOARD_SIZE - 5) + i, 4 - i, 'O')
        self.assertTrue(check_win(board_d2_edge, 'O'), "O should win TR-BL diagonal at BL edge")


if __name__ == '__main__':
    unittest.main()
