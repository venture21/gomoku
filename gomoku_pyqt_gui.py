import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGridLayout, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from gomoku import GomokuGame # Assuming gomoku.py is in the same directory or accessible

class GomokuPyQtGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.game = GomokuGame()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Gomoku - PyQt5")

        # Status Label
        self.status_label = QLabel("Welcome to Gomoku!")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(14)
        self.status_label.setFont(status_font)

        # New Game Button
        self.new_game_button = QPushButton("New Game")
        self.new_game_button.clicked.connect(self._new_game)

        # Board Buttons and Layout
        self.board_buttons = []
        board_layout = QGridLayout()
        board_layout.setSpacing(5) # Adjust spacing as needed

        button_font = QFont()
        button_font.setPointSize(16) # Font for X/O on buttons
        button_font.setBold(True)

        for r in range(self.game.board_size_internal):
            row_buttons = []
            for c in range(self.game.board_size_internal):
                button = QPushButton('')
                button.setFixedSize(40, 40)
                button.setFont(button_font)
                button.clicked.connect(lambda checked, row=r, col=c: self._handle_cell_click(row, col))
                board_layout.addWidget(button, r, c)
                row_buttons.append(button)
            self.board_buttons.append(row_buttons)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.status_label)
        main_layout.addLayout(board_layout) # Add the grid layout to the main VBox layout
        main_layout.addWidget(self.new_game_button)

        self.setLayout(main_layout)
        
        self._update_status_display() # Initial status update

    def _update_status_display(self, message=None):
        """Updates the status label display."""
        if message:
            self.status_label.setText(message)
        else:
            if not self.game.game_over: # Check if game is over
                self.status_label.setText(f"Player {self.game.current_player}'s turn")
            # If game is over, the message should be set by win/draw logic,
            # or a specific "Game Over" message if desired.

    def _handle_cell_click(self, row, col):
        """Handles a click on a board cell."""
        if self.game.board[row][col] == ' ' and not self.game.game_over:
            player_symbol = self.game.current_player
            
            if self.game.make_move(row, col): # make_move returns True if successful
                self.board_buttons[row][col].setText(player_symbol)
                self.board_buttons[row][col].setEnabled(False)

                if self.game.check_win():
                    self.game.game_over = True
                    self._update_status_display(f"Player {player_symbol} wins!")
                    self._disable_board()
                    QMessageBox.information(self, "Game Over", f"Player {player_symbol} wins!")
                elif self.game.check_draw():
                    self.game.game_over = True
                    self._update_status_display("It's a draw!")
                    self._disable_board()
                    QMessageBox.information(self, "Game Over", "It's a draw!")
                else:
                    self.game.switch_player()
                    self._update_status_display()

    def _new_game(self):
        """Starts a new game."""
        self.game.reset_game() # Resets game logic (board, current_player, game_over)
        for r in range(self.game.board_size_internal):
            for c in range(self.game.board_size_internal):
                self.board_buttons[r][c].setText('')
                self.board_buttons[r][c].setEnabled(True)
        self._update_status_display() # Update to "Player X's turn"

    def _disable_board(self):
        """Disables all buttons on the board."""
        for r in range(self.game.board_size_internal):
            for c in range(self.game.board_size_internal):
                self.board_buttons[r][c].setEnabled(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GomokuPyQtGUI()
    window.show()
    sys.exit(app.exec_())
