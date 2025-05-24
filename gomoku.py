import random # Added for AI
DEFAULT_BOARD_SIZE = 15

class GomokuGame:
    def __init__(self, board_size=None, game_mode=None, ai_difficulty=None):
        """Initializes the Gomoku game."""
        self.board_size_internal = board_size if board_size is not None else DEFAULT_BOARD_SIZE
        self.board = self._create_board()
        self.current_player = 'X'
        self.game_over = False
        self.game_mode = game_mode
        self.ai_difficulty = ai_difficulty
        self.WIN_LENGTH = 5 # Length needed to win

    def _create_board(self):
        """Creates an empty game board based on internal board size."""
        return [[' ' for _ in range(self.board_size_internal)] for _ in range(self.board_size_internal)]

    def make_move(self, row, col):
        """
        Updates the board at the given row and col with the current player's mark.
        Returns True if the move was successful, False otherwise.
        """
        if 0 <= row < self.board_size_internal and \
           0 <= col < self.board_size_internal and \
           self.board[row][col] == ' ':
            self.board[row][col] = self.current_player
            return True
        return False

    def check_win(self):
        """Checks if the current player has won (five in a row)."""
        player = self.current_player
        # Check horizontal win
        for r in range(self.board_size_internal):
            for c in range(self.board_size_internal - 4):
                if all(self.board[r][c+i] == player for i in range(5)):
                    return True

        # Check vertical win
        for c in range(self.board_size_internal):
            for r in range(self.board_size_internal - 4):
                if all(self.board[r+i][c] == player for i in range(5)):
                    return True

        # Check diagonal (top-left to bottom-right)
        for r in range(self.board_size_internal - 4):
            for c in range(self.board_size_internal - 4):
                if all(self.board[r+i][c+i] == player for i in range(5)):
                    return True

        # Check diagonal (top-right to bottom-left)
        for r in range(self.board_size_internal - 4):
            for c in range(4, self.board_size_internal): 
                if all(self.board[r+i][c-i] == player for i in range(5)):
                    return True
        return False

    def check_draw(self):
        """Checks if the game is a draw (board is full)."""
        for r in range(self.board_size_internal):
            for c in range(self.board_size_internal):
                if self.board[r][c] == ' ':
                    return False  # Found an empty cell, not a draw
        return True  # No empty cells found, it's a draw

    def switch_player(self):
        """Switches the current player."""
        if self.current_player == 'X':
            self.current_player = 'O'
        else:
            self.current_player = 'X'

    def reset_game(self, game_mode=None, ai_difficulty=None):
        """Resets the game to its initial state."""
        self.board = self._create_board()
        self.current_player = 'X'
        self.game_over = False
        self.game_mode = game_mode
        self.ai_difficulty = ai_difficulty

    def make_ai_move_easy(self):
        """Makes a move for the AI, preferring cells adjacent to existing stones."""
        if self.game_over:
            return False

        priority_empty_cells = []
        all_empty_cells = []

        for r in range(self.board_size_internal):
            for c in range(self.board_size_internal):
                if self.board[r][c] == ' ':
                    all_empty_cells.append((r, c))
                    is_priority = False
                    # Check neighbors
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            if dr == 0 and dc == 0:
                                continue # Skip the cell itself
                            
                            nr, nc = r + dr, c + dc
                            
                            # Check bounds
                            if 0 <= nr < self.board_size_internal and \
                               0 <= nc < self.board_size_internal:
                                if self.board[nr][nc] != ' ': # Neighbor has a stone
                                    priority_empty_cells.append((r, c))
                                    is_priority = True
                                    break # Found a stone, (r,c) is priority
                        if is_priority:
                            break # Move to next empty cell
        
        chosen_move = None
        if priority_empty_cells:
            chosen_move = random.choice(priority_empty_cells)
        elif all_empty_cells:
            chosen_move = random.choice(all_empty_cells)
        else:
            return False # No moves possible

        if chosen_move:
            row, col = chosen_move
            return self.make_move(row, col)
        return False # Should not be reached if all_empty_cells logic is correct

    def _get_opponent_symbol(self, player_symbol):
        """Returns the opponent's symbol."""
        return 'O' if player_symbol == 'X' else 'X'

    def _is_valid_coord(self, r, c):
        """Checks if coordinates are within board bounds."""
        return 0 <= r < self.board_size_internal and 0 <= c < self.board_size_internal

    def _get_lines_for_cell(self, r, c):
        """
        Generates all potential winning lines of WIN_LENGTH that pass through cell (r,c).
        """
        lines = []
        directions = [
            (0, 1),  # Horizontal
            (1, 0),  # Vertical
            (1, 1),  # Diagonal TL-BR
            (1, -1)  # Diagonal TR-BL / BL-TR
        ]

        for dr, dc in directions:
            for offset in range(self.WIN_LENGTH):
                line = []
                all_valid = True
                for i in range(self.WIN_LENGTH):
                    cur_r, cur_c = r + (i - offset) * dr, c + (i - offset) * dc
                    if not self._is_valid_coord(cur_r, cur_c):
                        all_valid = False
                        break
                    line.append((cur_r, cur_c))
                
                if all_valid:
                    lines.append(line)
        return lines

    def _evaluate_line_segment(self, line_coords, player_symbol):
        """
        Evaluates a single line segment for the given player.
        Returns a dictionary with counts of player stones, opponent stones, and empty cells.
        """
        counts = {
            'player_stones': 0,
            'opponent_stones': 0,
            'empty_cells': 0
        }
        opponent_symbol = self._get_opponent_symbol(player_symbol)

        for r_coord, c_coord in line_coords:
            cell_content = self.board[r_coord][c_coord]
            if cell_content == player_symbol:
                counts['player_stones'] += 1
            elif cell_content == opponent_symbol:
                counts['opponent_stones'] += 1
            else: # Empty cell
                counts['empty_cells'] += 1
        
        return counts

    def make_ai_move_normal(self):
        """Makes a move for the AI using a prioritized strategy."""
        if self.game_over:
            return False

        ai_symbol = self.current_player
        opponent_symbol = self._get_opponent_symbol(ai_symbol)

        empty_cells = []
        for r_idx in range(self.board_size_internal):
            for c_idx in range(self.board_size_internal):
                if self.board[r_idx][c_idx] == ' ':
                    empty_cells.append((r_idx, c_idx))
        
        if not empty_cells:
            return False # No moves possible

        # Priority 1: Check for AI Winning Move
        shuffled_empty_cells_for_win_check = random.sample(empty_cells, len(empty_cells))
        for r, c in shuffled_empty_cells_for_win_check:
            self.board[r][c] = ai_symbol # Temporarily place AI stone
            lines = self._get_lines_for_cell(r, c)
            for line_coords in lines:
                eval_info = self._evaluate_line_segment(line_coords, ai_symbol)
                if eval_info['player_stones'] == self.WIN_LENGTH:
                    self.board[r][c] = ' ' # Revert temporary placement
                    return self.make_move(r, c) # Make the winning move
            self.board[r][c] = ' ' # Revert if not a winning move

        # Priority 2: Block Opponent's Winning Move
        shuffled_empty_cells_for_block_check = random.sample(empty_cells, len(empty_cells))
        for r, c in shuffled_empty_cells_for_block_check:
            self.board[r][c] = opponent_symbol # Temporarily place opponent's stone
            lines = self._get_lines_for_cell(r, c)
            for line_coords in lines:
                # Evaluate from opponent's perspective
                eval_info = self._evaluate_line_segment(line_coords, opponent_symbol)
                if eval_info['player_stones'] == self.WIN_LENGTH:
                    self.board[r][c] = ' ' # Revert temporary placement
                    return self.make_move(r, c) # AI plays here to block
            self.board[r][c] = ' ' # Revert

        # Priority 3: Create an "Open Three" for AI
        ai_open_three_moves = []
        for r, c in empty_cells: # Iterate in natural order, then pick randomly
            self.board[r][c] = ai_symbol # Temporarily place AI stone
            lines = self._get_lines_for_cell(r, c)
            for line_coords in lines:
                eval_info = self._evaluate_line_segment(line_coords, ai_symbol)
                if eval_info['player_stones'] == 3 and eval_info['empty_cells'] == 2:
                    ai_open_three_moves.append((r,c))
                    break # Found an open three for this (r,c)
            self.board[r][c] = ' ' # Revert
        
        if ai_open_three_moves:
            chosen_move = random.choice(ai_open_three_moves)
            return self.make_move(chosen_move[0], chosen_move[1])

        # Priority 4: Block Opponent's "Open Three"
        opponent_open_three_blocking_moves = []
        for r, c in empty_cells: # Iterate in natural order, then pick randomly
            self.board[r][c] = opponent_symbol # Temporarily place opponent's stone
            lines = self._get_lines_for_cell(r, c)
            for line_coords in lines:
                # Evaluate from opponent's perspective
                eval_info = self._evaluate_line_segment(line_coords, opponent_symbol)
                if eval_info['player_stones'] == 3 and eval_info['empty_cells'] == 2:
                    opponent_open_three_blocking_moves.append((r,c)) # AI plays here to block
                    break # Found a blocking opportunity for this (r,c)
            self.board[r][c] = ' ' # Revert

        if opponent_open_three_blocking_moves:
            chosen_move = random.choice(opponent_open_three_blocking_moves)
            return self.make_move(chosen_move[0], chosen_move[1])
            
        # Priority 5: Fallback to "Easy" AI logic
        return self.make_ai_move_easy()

# Functions below are for terminal interaction and will remain separate.
# These functions can use the DEFAULT_BOARD_SIZE or take the size from the game instance.

def create_board(): # This function is kept for potential direct use, though play_game uses GomokuGame.
    """Creates an empty game board using DEFAULT_BOARD_SIZE."""
    return [[' ' for _ in range(DEFAULT_BOARD_SIZE)] for _ in range(DEFAULT_BOARD_SIZE)]

def display_board(board_display, board_size_display=DEFAULT_BOARD_SIZE):
    """Displays the game board in a user-friendly format."""
    # Print column numbers
    print("   " + " ".join([f"{i:2}" for i in range(board_size_display)]))
    # Print board with row numbers
    for i, row in enumerate(board_display):
        print(f"{i:2} |" + "|".join([f"{cell:2}" for cell in row]) + "|")

def get_player_move(player, board_display, board_size_display=DEFAULT_BOARD_SIZE):
    """Gets the player's move, validates it, and returns the 0-indexed row and col."""
    while True:
        try:
            move_str = input(f"Player {player}, enter your move (row col, e.g., 1 1): ")
            row_str, col_str = move_str.split()
            row_1_indexed = int(row_str)
            col_1_indexed = int(col_str)

            if not (1 <= row_1_indexed <= board_size_display and 1 <= col_1_indexed <= board_size_display):
                print(f"Invalid input. Row and column must be between 1 and {board_size_display}.")
                continue

            row_0_indexed = row_1_indexed - 1
            col_0_indexed = col_1_indexed - 1

            if board_display[row_0_indexed][col_0_indexed] != ' ':
                print("Invalid move. Cell is already taken. Try again.")
                continue

            return row_0_indexed, col_0_indexed
        except ValueError:
            print("Invalid input. Please enter two integers separated by a space (e.g., '3 4').")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# Obsolete global functions (make_move, check_win, check_draw) are removed
# as their logic is now within the GomokuGame class.

def play_game():
    """Main function to play the Gomoku game in the terminal."""
    # game instance uses DEFAULT_BOARD_SIZE by default if not specified
    game = GomokuGame()
    print("Welcome to Gomoku!")

    while True:
        print("\n") 
        # Pass game.board and game.board_size_internal to display_board
        display_board(game.board, game.board_size_internal) 
        
        print(f"Player {game.current_player}'s turn.")
        # Pass game.current_player, game.board and game.board_size_internal to get_player_move
        row, col = get_player_move(game.current_player, game.board, game.board_size_internal) 
        
        if game.make_move(row, col): # make_move now uses self.current_player and self.board
            if game.check_win(): # check_win now uses self.current_player and self.board
                print("\n")
                display_board(game.board, game.board_size_internal)
                print(f"Congratulations! Player {game.current_player} wins!")
                break
            
            if game.check_draw(): # check_draw now uses self.board
                print("\n")
                display_board(game.board, game.board_size_internal)
                print("It's a draw!")
                break

            game.switch_player()
        # else: The make_move method now returns False if move is invalid.
        # get_player_move should prevent invalid moves from being attempted by make_move.

# if __name__ == '__main__':
#    play_game()