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