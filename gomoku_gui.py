import tkinter as tk
from tkinter import font as tkfont # For font settings
from gomoku import GomokuGame

class GomokuGUI:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Gomoku")

        self.game = GomokuGame() # Uses DEFAULT_BOARD_SIZE from gomoku.py

        # Initialize board_buttons as a list of lists before _create_board_ui is called
        self.board_buttons = [[None for _ in range(self.game.board_size_internal)] 
                              for _ in range(self.game.board_size_internal)]

        # Status Label
        self.status_label_text = tk.StringVar()
        self.status_label = tk.Label(self.root, textvariable=self.status_label_text, font=('Arial', 14))
        self.status_label.pack(pady=10)

        # Board Frame - will be created and packed in _create_board_ui
        self.board_frame = tk.Frame(self.root)
        # This frame will be packed/gridded in _create_board_ui

        # New Game Button
        self.new_game_button = tk.Button(self.root, text="New Game", font=('Arial', 12), command=self._new_game)
        self.new_game_button.pack(pady=10)
        
        self._create_board_ui()
        self._update_status() # Initial status update

    def _create_board_ui(self):
        """Creates the UI for the game board."""
        self.board_frame.pack(pady=5) # Pack the frame that will contain the buttons

        button_font = tkfont.Font(family='Arial', size=20, weight='bold')
        
        for r in range(self.game.board_size_internal):
            for c in range(self.game.board_size_internal):
                button = tk.Button(
                    self.board_frame,
                    text=' ',
                    font=button_font,
                    width=2,  # Adjusted for better visual balance with font
                    height=1,
                    command=lambda row=r, col=c: self._handle_cell_click(row, col)
                )
                button.grid(row=r, column=c, sticky="nsew") # Use sticky for responsiveness
                self.board_buttons[r][c] = button
        
        # Configure row/column weights for the board_frame so buttons expand if window is resized
        for i in range(self.game.board_size_internal):
            self.board_frame.grid_rowconfigure(i, weight=1)
            self.board_frame.grid_columnconfigure(i, weight=1)

    def _handle_cell_click(self, row, col):
        """Handles a click on a board cell."""
        if self.game.board[row][col] == ' ' and not self.game.game_over:
            player_symbol = self.game.current_player
            
            if self.game.make_move(row, col): # make_move returns True if successful
                self.board_buttons[row][col].config(text=player_symbol, state='disabled', disabledforeground= "black" if player_symbol == "X" else "blue") # Example colors

                if self.game.check_win():
                    self.game.game_over = True
                    self._update_status(f"Player {player_symbol} wins!")
                    self._disable_board()
                elif self.game.check_draw():
                    self.game.game_over = True
                    self._update_status("It's a draw!")
                    self._disable_board()
                else:
                    self.game.switch_player()
                    self._update_status()
            # else: make_move returned False, which shouldn't happen if logic is correct
            # because we checked if cell is empty and game is not over.

    def _update_status(self, message=None):
        """Updates the status label."""
        if message:
            self.status_label_text.set(message)
        else:
            if not self.game.game_over:
                self.status_label_text.set(f"Player {self.game.current_player}'s turn")
            # If game is over and no specific message, status is already set by win/draw logic

    def _new_game(self):
        """Starts a new game."""
        self.game.reset_game() # Resets game logic (board, current_player, game_over)
        for r in range(self.game.board_size_internal):
            for c in range(self.game.board_size_internal):
                self.board_buttons[r][c].config(text=' ', state='normal')
        self._update_status() # Update to "Player X's turn"

    def _disable_board(self, exclude_clicked=False, clicked_row=None, clicked_col=None):
        """Disables all buttons on the board, optionally excluding the last clicked one."""
        for r in range(self.game.board_size_internal):
            for c in range(self.game.board_size_internal):
                if exclude_clicked and r == clicked_row and c == clicked_col:
                    continue
                self.board_buttons[r][c].config(state='disabled')

if __name__ == '__main__':
    root = tk.Tk()
    gui = GomokuGUI(root)
    root.mainloop()
