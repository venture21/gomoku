BOARD_SIZE = 15

def create_board():
    """Creates an empty game board."""
    return [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def display_board(board):
    """Displays the game board in a user-friendly format."""
    # Print column numbers
    print("   " + " ".join([f"{i:2}" for i in range(BOARD_SIZE)]))
    # Print board with row numbers
    for i, row in enumerate(board):
        print(f"{i:2} |" + "|".join([f"{cell:2}" for cell in row]) + "|")

def get_player_move(player, board):
    """Gets the player's move, validates it, and returns the 0-indexed row and col."""
    while True:
        try:
            move_str = input(f"Player {player}, enter your move (row col, e.g., 1 1): ")
            row_str, col_str = move_str.split()
            row_1_indexed = int(row_str)
            col_1_indexed = int(col_str)

            if not (1 <= row_1_indexed <= BOARD_SIZE and 1 <= col_1_indexed <= BOARD_SIZE):
                print(f"Invalid input. Row and column must be between 1 and {BOARD_SIZE}.")
                continue

            row_0_indexed = row_1_indexed - 1
            col_0_indexed = col_1_indexed - 1

            if board[row_0_indexed][col_0_indexed] != ' ':
                print("Invalid move. Cell is already taken. Try again.")
                continue

            return row_0_indexed, col_0_indexed
        except ValueError:
            print("Invalid input. Please enter two integers separated by a space (e.g., '3 4').")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def make_move(board, row, col, player):
    """Updates the board at the given row and col with the player's mark."""
    board[row][col] = player

def check_win(board, player):
    """Checks if the given player has won (five in a row)."""
    # Check horizontal win
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE - 4):
            if all(board[r][c+i] == player for i in range(5)):
                return True

    # Check vertical win
    for c in range(BOARD_SIZE):
        for r in range(BOARD_SIZE - 4):
            if all(board[r+i][c] == player for i in range(5)):
                return True

    # Check diagonal (top-left to bottom-right)
    for r in range(BOARD_SIZE - 4):
        for c in range(BOARD_SIZE - 4):
            if all(board[r+i][c+i] == player for i in range(5)):
                return True

    # Check diagonal (top-right to bottom-left)
    for r in range(BOARD_SIZE - 4):
        for c in range(4, BOARD_SIZE): # Start from column 4
            if all(board[r+i][c-i] == player for i in range(5)):
                return True

    return False

def check_draw(board):
    """Checks if the game is a draw (board is full)."""
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == ' ':
                return False  # Found an empty cell, not a draw
    return True  # No empty cells found, it's a draw

def play_game():
    """Main function to play the Gomoku game."""
    board = create_board()
    current_player = 'X'
    print("Welcome to Gomoku!")

    while True:
        print("\n") # Add some spacing
        display_board(board)
        
        print(f"Player {current_player}'s turn.")
        row, col = get_player_move(current_player, board)
        make_move(board, row, col, current_player)

        if check_win(board, current_player):
            print("\n")
            display_board(board)
            print(f"Congratulations! Player {current_player} wins!")
            break
        
        if check_draw(board):
            print("\n")
            display_board(board)
            print("It's a draw!")
            break

        # Switch player
        if current_player == 'X':
            current_player = 'O'
        else:
            current_player = 'X'

if __name__ == '__main__':
    play_game()