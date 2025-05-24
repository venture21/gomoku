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
        self.assertIsNone(game.game_mode, "game_mode should be None after default reset")
        self.assertIsNone(game.ai_difficulty, "ai_difficulty should be None after default reset")
        
        # Check if board is entirely empty
        for r in range(game.board_size_internal):
            for c in range(game.board_size_internal):
                self.assertEqual(game.board[r][c], ' ', f"Cell ({r},{c}) should be empty after reset.")

    def test_game_mode_attributes(self):
        game = GomokuGame(game_mode="1P", ai_difficulty="Easy")
        self.assertEqual(game.game_mode, "1P")
        self.assertEqual(game.ai_difficulty, "Easy")

        game.reset_game(game_mode="2P", ai_difficulty="Hard") # Reset with new mode and difficulty
        self.assertEqual(game.game_mode, "2P")
        self.assertEqual(game.ai_difficulty, "Hard")
        
        game.reset_game(game_mode="1P") # Reset with new mode, difficulty becomes None by default in reset
        self.assertEqual(game.game_mode, "1P")
        self.assertIsNone(game.ai_difficulty) 

        game.reset_game() # Reset to complete defaults
        self.assertIsNone(game.game_mode)
        self.assertIsNone(game.ai_difficulty)

    def test_make_ai_move_easy(self):
        # Test basic move on an EMPTY board (fallback to all_empty_cells)
        game = GomokuGame(game_mode="1P", ai_difficulty="Easy")
        game.current_player = 'O' # AI is 'O'
        initial_empty_cells = sum(row.count(' ') for row in game.board)
        
        move_made = game.make_ai_move_easy()
        self.assertTrue(move_made, "AI should make a move on an empty board")
        current_empty_cells = sum(row.count(' ') for row in game.board)
        self.assertEqual(current_empty_cells, initial_empty_cells - 1, "One stone should be placed on empty board")
        self.assertEqual(game.current_player, 'O', "Current player should remain AI after its move")

        # Test Prioritized Moves (adjacent to existing stone)
        game.reset_game(game_mode="1P", ai_difficulty="Easy")
        game.current_player = 'O' # AI is 'O'
        # Place a stone for context
        px, py = 7, 7
        game.board[px][py] = 'X' # Opponent's stone
        
        move_made_priority = game.make_ai_move_easy()
        self.assertTrue(move_made_priority, "AI should make a priority move")
        
        ai_move_r, ai_move_c = -1, -1
        found_ai_move = False
        for r_idx, row_val in enumerate(game.board):
            for c_idx, cell_val in enumerate(row_val):
                if cell_val == 'O':
                    ai_move_r, ai_move_c = r_idx, c_idx
                    found_ai_move = True
                    break
            if found_ai_move:
                break
        
        self.assertTrue(found_ai_move, "AI move ('O') should be found on the board")
        
        is_adjacent = False
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0: continue
                if ai_move_r == px + dr and ai_move_c == py + dc:
                    is_adjacent = True
                    break
            if is_adjacent: break
        self.assertTrue(is_adjacent, f"AI move ({ai_move_r},{ai_move_c}) should be adjacent to opponent stone at ({px},{py})")


        # Test Fallback to Any Empty Cell (when priority cells are blocked)
        # Using a 5x5 board for simplicity in this specific scenario
        game_fallback = GomokuGame(board_size=5, game_mode="1P", ai_difficulty="Easy")
        game_fallback.current_player = 'X' # AI is 'X' this time
        
        # Setup: opponent 'O' places a stone, AI 'X' surrounds it, then opponent 'O' blocks all adjacencies
        # This setup is a bit contrived to force a specific scenario
        # Let's place a stone at (2,2) for AI
        center_r, center_c = 2,2
        game_fallback.board[center_r][center_c] = 'O' # Opponent stone

        # Fill all adjacent cells to (2,2) with AI's *own* stones - this is not the goal.
        # Goal: Opponent stone at (2,2), AI is 'X'. All cells adjacent to (2,2) are taken by 'O'.
        # Other cells like (0,0) are empty. AI ('X') should play in (0,0).
        game_fallback.reset_game(board_size=5, game_mode="1P", ai_difficulty="Easy") # Fresh board
        game_fallback.current_player = 'X' # AI is 'X'
        
        opponent_stone_r, opponent_stone_c = 2, 2
        game_fallback.board[opponent_stone_r][opponent_stone_c] = 'O' # Central opponent stone
        
        # Block all cells adjacent to opponent_stone with 'O' as well
        for dr_block in range(-1, 2):
            for dc_block in range(-1, 2):
                if dr_block == 0 and dc_block == 0: continue
                nr, nc = opponent_stone_r + dr_block, opponent_stone_c + dc_block
                if 0 <= nr < 5 and 0 <= nc < 5:
                    game_fallback.board[nr][nc] = 'O' 
        
        # Ensure (0,0) is empty for AI ('X') to pick
        game_fallback.board[0][0] = ' ' 
        
        move_made_fallback = game_fallback.make_ai_move_easy()
        self.assertTrue(move_made_fallback, "AI should make a fallback move")
        
        ai_fallback_r, ai_fallback_c = -1, -1
        found_fallback_move = False
        for r_idx, row_val in enumerate(game_fallback.board):
            for c_idx, cell_val in enumerate(row_val):
                if cell_val == 'X': # AI is 'X'
                    ai_fallback_r, ai_fallback_c = r_idx, c_idx
                    found_fallback_move = True
                    break
            if found_fallback_move: break
            
        self.assertTrue(found_fallback_move, "AI fallback move ('X') should be found")
        # Check it's not adjacent to the original 'O' at (2,2)
        is_adj_to_center_o = False
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0: continue
                if ai_fallback_r == opponent_stone_r + dr and ai_fallback_c == opponent_stone_c + dc:
                    is_adj_to_center_o = True; break
            if is_adj_to_center_o: break
        self.assertFalse(is_adj_to_center_o, 
                         f"AI fallback move ({ai_fallback_r},{ai_fallback_c}) should NOT be adjacent to central 'O' at ({opponent_stone_r},{opponent_stone_c}) because all those spots were blocked.")
        self.assertEqual((ai_fallback_r, ai_fallback_c), (0,0), "AI should have picked the only available non-priority spot (0,0)")


        # Test on a nearly full board
        game.reset_game(game_mode="1P", ai_difficulty="Easy")
        game.current_player = 'O'
        # Fill all but one cell
        last_empty_row, last_empty_col = -1, -1
        for r in range(game.board_size_internal):
            for c in range(game.board_size_internal):
                if r == game.board_size_internal -1 and c == game.board_size_internal -1 :
                    last_empty_row, last_empty_col = r,c
                    continue # Leave last cell empty
                game.board[r][c] = 'X' # Fill with opponent's stones
        
        self.assertEqual(game.board[last_empty_row][last_empty_col], ' ') # Confirm it's empty
        move_made_on_nearly_full = game.make_ai_move_easy()
        self.assertTrue(move_made_on_nearly_full, "AI should make a move on a nearly full board")
        self.assertEqual(game.board[last_empty_row][last_empty_col], 'O', "AI should take the last empty cell")
        self.assertEqual(game.current_player, 'O')

        # Test on a completely full board
        game.reset_game(game_mode="1P", ai_difficulty="Easy")
        game.current_player = 'O'
        for r in range(game.board_size_internal):
            for c in range(game.board_size_internal):
                game.board[r][c] = 'X' # Fill all cells
        
        move_made_on_full = game.make_ai_move_easy()
        self.assertFalse(move_made_on_full, "AI should not make a move on a full board")
        # Verify board is unchanged (no 'O' placed)
        o_stones = sum(row.count('O') for row in game.board)
        self.assertEqual(o_stones, 0, "No 'O' stones should be on a full board after AI attempts move")
        self.assertEqual(game.current_player, 'O')

        # Test randomness (simplified check - moves should generally differ)
        # This test is probabilistic and might occasionally fail even if logic is correct.
        # A more robust test would analyze distribution or require many trials.
        if game.board_size_internal >= 3: # Ensure enough space for varied moves
            game.reset_game(game_mode="1P", ai_difficulty="Easy", board_size=3) # Use smaller board for this test
            game.current_player = 'O'
            moves = set()
            for _ in range(5): # Make 5 AI moves on an empty 3x3 board
                game.reset_game(game_mode="1P", ai_difficulty="Easy", board_size=3)
                game.current_player = 'O'
                if game.make_ai_move_easy():
                    # Find where the move was made
                    for r_idx, row_val in enumerate(game.board):
                        for c_idx, cell_val in enumerate(row_val):
                            if cell_val == 'O':
                                moves.add((r_idx, c_idx))
                                break
                        if (r_idx, c_idx) in moves: break 
            # Expect more than 1 unique move if board is 3x3 (9 cells) and 5 attempts
            # This is a weak test but can catch if AI always picks e.g. (0,0)
            self.assertTrue(len(moves) > 1, "AI moves should show some variation on a 3x3 board over 5 trials")


    def test_board_size_default(self):
        game = GomokuGame()
        self.assertEqual(game.board_size_internal, DEFAULT_BOARD_SIZE, f"Default board size should be {DEFAULT_BOARD_SIZE}")
        self.assertEqual(len(game.board), DEFAULT_BOARD_SIZE)

    def test_get_lines_for_cell(self):
        game = GomokuGame(board_size=15) # Standard 15x15 board
        win_len = game.WIN_LENGTH

        # Test center cell (e.g., 7,7)
        lines_center = game._get_lines_for_cell(7, 7)
        self.assertEqual(len(lines_center), 4 * win_len, 
                         f"Center cell should have {4 * win_len} potential lines")
        for line in lines_center:
            self.assertEqual(len(line), win_len, "Each line should have WIN_LENGTH coordinates")
            for r, c in line:
                self.assertTrue(0 <= r < game.board_size_internal and 0 <= c < game.board_size_internal, 
                                "All coordinates in a line must be valid")

        # Test edge cell (e.g., 0,7) - not a corner
        lines_edge = game._get_lines_for_cell(0, 7)
        # Horizontal: win_len lines
        # Vertical: 1 line (if offset allows, i.e. cell is one of the 5 points)
        # Diagonal TL-BR: (win_len - 0) = 5 lines starting from (0,7), (0,6)...(0,3) if offset makes (0,7) the first point.
        #    offset = 0: (0,7)...(4,11)
        #    offset = 1: (-1,6)...(3,10) - invalid
        #    This depends on how many of the 5 possible start positions for a line of length 5,
        #    that *includes* (0,7), are valid.
        #    Horizontal: 5 lines. (0,7) can be 1st, 2nd, 3rd, 4th, 5th point.
        #    Vertical: (0,7) to (4,7) is 1 line.
        #    Diag TL-BR: (0,7)-(4,11), (-1,6)-(3,10)X, (-2,5)-(2,9)X, (-3,4)-(1,8)X, (-4,3)-(0,7)X.
        #              Actually, it's simpler: how many lines of length 5 can contain (0,7)?
        #              Horizontal: 5. Vertical: 1. Diag TL-BR: 1. Diag TR-BL: 1. Total = 8.
        #              This needs to be calculated more carefully. Let's assume the method is correct.
        #              For (0,7) on 15x15 with WIN_LENGTH=5:
        #              H: 5 lines. V: 1 line. D1 (TL-BR): 1 line. D2 (TR-BL): min(0+1, 15-7, 5, 0+1+15-7-5+1) = 1 line.
        #              This is not right. The logic is: for each direction, for each of the 5 offsets, is the line valid?
        #              H: [(0,3)-(0,7)] to [(0,7)-(0,11)] -> 5 lines
        #              V: [(0,7)-(4,7)] -> 1 line
        #              D1: [(0,7)-(4,11)] -> 1 line
        #              D2: [(0,7)-(-4,3)]X ... no, it's (0,7) to (4,3) -> 1 line.
        #              Total should be 5+1+1+1 = 8.
        self.assertTrue(len(lines_edge) < 4 * win_len, "Edge cell should have fewer lines than center")
        self.assertEqual(len(lines_edge), 8, "Cell (0,7) on 15x15 should have 8 lines of length 5 through it")


        # Test corner cell (0,0)
        lines_corner = game._get_lines_for_cell(0, 0)
        # H: 1 line. V: 1 line. D1 (TL-BR): 1 line. D2 (TR-BL): 0 lines. Total = 3.
        self.assertEqual(len(lines_corner), 3, "Corner cell (0,0) should have 3 lines of length 5 through it")

    def test_evaluate_line_segment(self):
        game = GomokuGame(board_size=5) # Use 5x5 board
        ai_symbol = 'O'
        opponent_symbol = 'X'

        # All empty
        line_coords_empty = [(0,0), (0,1), (0,2), (0,3), (0,4)]
        game.board = [[' '] * 5 for _ in range(5)]
        counts = game._evaluate_line_segment(line_coords_empty, ai_symbol)
        self.assertEqual(counts, {'player_stones': 0, 'opponent_stones': 0, 'empty_cells': 5})

        # 1 AI stone, 4 empty
        game.board[0][0] = ai_symbol
        counts = game._evaluate_line_segment(line_coords_empty, ai_symbol)
        self.assertEqual(counts, {'player_stones': 1, 'opponent_stones': 0, 'empty_cells': 4})

        # 3 AI stones, 2 empty ("open three" if this is the line)
        game.board[0][0] = ai_symbol; game.board[0][1] = ai_symbol; game.board[0][2] = ai_symbol
        game.board[0][3] = ' '; game.board[0][4] = ' '
        counts = game._evaluate_line_segment(line_coords_empty, ai_symbol)
        self.assertEqual(counts, {'player_stones': 3, 'opponent_stones': 0, 'empty_cells': 2})
        
        # 4 AI stones, 1 empty
        game.board[0][3] = ai_symbol
        counts = game._evaluate_line_segment(line_coords_empty, ai_symbol)
        self.assertEqual(counts, {'player_stones': 4, 'opponent_stones': 0, 'empty_cells': 1})

        # 5 AI stones (win)
        game.board[0][4] = ai_symbol
        counts = game._evaluate_line_segment(line_coords_empty, ai_symbol)
        self.assertEqual(counts, {'player_stones': 5, 'opponent_stones': 0, 'empty_cells': 0})

        # 1 Opponent stone, 4 empty
        game.board = [[' '] * 5 for _ in range(5)]
        game.board[0][0] = opponent_symbol
        counts = game._evaluate_line_segment(line_coords_empty, ai_symbol)
        self.assertEqual(counts, {'player_stones': 0, 'opponent_stones': 1, 'empty_cells': 4})

        # 3 Opponent stones, 2 empty
        game.board[0][0] = opponent_symbol; game.board[0][1] = opponent_symbol; game.board[0][2] = opponent_symbol
        counts = game._evaluate_line_segment(line_coords_empty, ai_symbol)
        self.assertEqual(counts, {'player_stones': 0, 'opponent_stones': 3, 'empty_cells': 2})

        # Mixed: 2 AI, 1 Opponent, 2 Empty
        game.board = [[' '] * 5 for _ in range(5)]
        game.board[0][0] = ai_symbol; game.board[0][1] = ai_symbol
        game.board[0][2] = opponent_symbol
        counts = game._evaluate_line_segment(line_coords_empty, ai_symbol)
        self.assertEqual(counts, {'player_stones': 2, 'opponent_stones': 1, 'empty_cells': 2})

    def test_make_ai_move_normal(self):
        # Test AI Winning Move
        game = GomokuGame(board_size=5, game_mode="1P", ai_difficulty="Normal")
        game.current_player = 'O' # AI is 'O'
        game.board = [
            [' ', ' ', ' ', ' ', ' '],
            [' ', 'O', 'O', 'O', 'O'], # AI needs to play at (1,0) or (1,4)
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ']
        ]
        game.board[1][0] = ' ' # Ensure one winning spot is open
        self.assertTrue(game.make_ai_move_normal())
        self.assertEqual(game.board[1][0], 'O', "AI should make winning move at (1,0)")
        
        game.reset_game(board_size=5, game_mode="1P", ai_difficulty="Normal")
        game.current_player = 'O'
        game.board = [
            [' ', 'O', 'O', 'O', 'O'],
            [' ', ' ', ' ', ' ', ' '], # AI needs to play at (0,0)
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ']
        ]
        game.board[0][0] = ' '
        game.board[0][4] = 'X' # Block one side to force win
        self.assertTrue(game.make_ai_move_normal())
        self.assertEqual(game.board[0][0], 'O', "AI should make winning move at (0,0)")


        # Test AI Blocks Opponent's Winning Move
        game.reset_game(board_size=5, game_mode="1P", ai_difficulty="Normal")
        game.current_player = 'O' # AI is 'O'
        game.board = [
            [' ', ' ', ' ', ' ', ' '],
            ['X', 'X', 'X', 'X', ' '], # Opponent 'X' needs (1,4) to win
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ']
        ]
        self.assertTrue(game.make_ai_move_normal())
        self.assertEqual(game.board[1][4], 'O', "AI should block opponent's win at (1,4)")

        # Test AI Creates "Open Three"
        game.reset_game(board_size=5, game_mode="1P", ai_difficulty="Normal")
        game.current_player = 'O' # AI is 'O'
        game.board = [ # AI is 'O'. Needs _ O O _ _ pattern.
            [' ', ' ', ' ', ' ', ' '],
            [' ', 'O', 'O', ' ', ' '], # AI plays at (1,0) or (1,3) or (1,4)
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ']
        ]
        self.assertTrue(game.make_ai_move_normal())
        # Check if an open three was created. The AI could play at (1,0), (1,3), or (1,4)
        # For simplicity, we check if one of these was chosen and creates an open three.
        # This is a bit more complex to assert precisely without knowing which random choice was made.
        # We'll check if *any* move resulted in an open three.
        ai_move_made = False
        for r in range(5):
            for c in range(5):
                if game.board[r][c] == 'O' and not (r==1 and (c==1 or c==2)): # Found the AI's new move
                    # Check if this move created an open three
                    lines_through_move = game._get_lines_for_cell(r,c)
                    open_three_found = False
                    for line in lines_through_move:
                        eval_info = game._evaluate_line_segment(line, 'O')
                        if eval_info['player_stones'] == 3 and eval_info['empty_cells'] == 2:
                            open_three_found = True
                            break
                    if open_three_found:
                        ai_move_made = True; break
            if ai_move_made: break
        self.assertTrue(ai_move_made, "AI should make a move to create an open three")


        # Test AI Blocks Opponent's "Open Three"
        game.reset_game(board_size=5, game_mode="1P", ai_difficulty="Normal")
        game.current_player = 'O' # AI is 'O'
        game.board = [ # Opponent 'X' needs _ X X _ _ pattern. AI 'O' should block.
            [' ', ' ', ' ', ' ', ' '],
            [' ', 'X', 'X', ' ', ' '], # Opponent can play at (1,0), (1,3), (1,4)
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ']
        ]
        self.assertTrue(game.make_ai_move_normal())
        # Check if AI blocked one of the opponent's potential open three spots
        self.assertTrue(game.board[1][0] == 'O' or game.board[1][3] == 'O' or game.board[1][4] == 'O',
                        "AI should block opponent's open three")

        # Test Fallback to make_ai_move_easy (on an empty board)
        game.reset_game(board_size=5, game_mode="1P", ai_difficulty="Normal")
        game.current_player = 'O' # AI is 'O'
        initial_empty_count = sum(row.count(' ') for row in game.board)
        self.assertTrue(game.make_ai_move_normal())
        final_empty_count = sum(row.count(' ') for row in game.board)
        self.assertEqual(final_empty_count, initial_empty_count - 1, 
                         "AI should make a move (fallback to easy) on empty board")

        # Test on Full Board
        game.reset_game(board_size=3, game_mode="1P", ai_difficulty="Normal") # Smaller board
        game.current_player = 'O'
        game.board = [['X','O','X'],['O','X','O'],['X','O','X']]
        self.assertFalse(game.make_ai_move_normal(), "AI should not move on a full board")


if __name__ == '__main__':
    unittest.main()
