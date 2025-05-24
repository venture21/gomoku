import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGridLayout, QMessageBox, QSizePolicy
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush, QPen
from PyQt5.QtCore import Qt, QSize, QPointF
from gomoku import GomokuGame # Assuming gomoku.py is in the same directory or accessible

class BoardWidget(QWidget):
    def __init__(self, parent_gui, parent=None): # Changed game_instance to parent_gui
        super().__init__(parent)
        self.parent_gui = parent_gui
        self.game = self.parent_gui.game # Access game from parent_gui
        self.padding = 20  # Pixels
        self.cell_size = None # Calculated in paintEvent or mousePressEvent
        self.stone_radius = None # Calculated in paintEvent
        self.board_origin_x = 0 # Top-left X of the grid, calculated in paintEvent/mousePressEvent
        self.board_origin_y = 0 # Top-left Y of the grid, calculated in paintEvent/mousePressEvent
        self.setMinimumSize(self.minimumSizeHint())


    def sizeHint(self):
        # Accommodate a 15x15 board with padding. (14 spaces * ~30px) + 2*padding
        return QSize(450, 450)

    def minimumSizeHint(self):
        # Slightly smaller than sizeHint, but still reasonable for a board
        return QSize(350, 350)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        widget_width = self.width()
        widget_height = self.height()

        # Define the square drawing area for the board logic (grid + stones)
        # This area will be centered within the widget.
        drawing_area_size = min(widget_width, widget_height) - 2 * self.padding
        
        if drawing_area_size <= 0 or self.game.board_size_internal <= 1:
            return # Not enough space or invalid board size

        # Calculate cell_size based on the number of intervals (board_size - 1)
        self.cell_size = drawing_area_size / (self.game.board_size_internal - 1)
        self.stone_radius = self.cell_size * 0.40 # Proportion for stone size

        # The actual size of the grid of lines
        grid_size = (self.game.board_size_internal - 1) * self.cell_size

        # Calculate top-left offset to center the grid
        # Store these as instance variables for mousePressEvent
        self.board_origin_x = (widget_width - grid_size) / 2
        self.board_origin_y = (widget_height - grid_size) / 2

        # --- Draw Rectangular Background ---
        # This rectangle covers the area of the grid.
        painter.fillRect(int(self.board_origin_x), int(self.board_origin_y), 
                         int(grid_size), int(grid_size), QColor(222, 184, 135))

        # --- Draw Grid Lines ---
        painter.save()
        painter.translate(self.board_origin_x, self.board_origin_y) # Translate to top-left of the grid
        
        pen = QPen(Qt.black)
        pen.setWidth(1) # Adjust line thickness if needed
        painter.setPen(pen)

        for i in range(self.game.board_size_internal):
            # Horizontal line
            painter.drawLine(QPointF(0, i * self.cell_size), 
                             QPointF(grid_size, i * self.cell_size))
            # Vertical line
            painter.drawLine(QPointF(i * self.cell_size, 0),
                             QPointF(i * self.cell_size, grid_size))
        
        # --- Draw Stones ---
        for r in range(self.game.board_size_internal):
            for c in range(self.game.board_size_internal):
                player = self.game.board[r][c]
                if player != ' ':
                    stone_center_x = c * self.cell_size
                    stone_center_y = r * self.cell_size
                    
                    if player == 'X':
                        painter.setBrush(QBrush(Qt.black))
                    elif player == 'O':
                        painter.setBrush(QBrush(Qt.white))
                    
                    # Draw stone with a thin border
                    painter.setPen(QPen(Qt.darkGray, 0.5)) # Thin border for stones
                    painter.drawEllipse(QPointF(stone_center_x, stone_center_y), 
                                        self.stone_radius, self.stone_radius)
        painter.restore()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.game.game_over:
            click_x = event.pos().x()
            click_y = event.pos().y()

            # Recalculate geometry for click handling, ensuring it's up-to-date
            widget_width = self.width()
            widget_height = self.height()
            
            current_drawing_area_size = min(widget_width, widget_height) - 2 * self.padding
            if current_drawing_area_size <= 0 or self.game.board_size_internal <= 1:
                return

            current_cell_size = current_drawing_area_size / (self.game.board_size_internal - 1)
            if current_cell_size <= 0: # Avoid division by zero if cell_size is somehow zero
                return

            grid_size = (self.game.board_size_internal - 1) * current_cell_size
            current_board_origin_x = (widget_width - grid_size) / 2
            current_board_origin_y = (widget_height - grid_size) / 2

            relative_x = click_x - current_board_origin_x
            relative_y = click_y - current_board_origin_y

            # Determine clicked cell by finding the nearest intersection point
            col = round(relative_x / current_cell_size)
            row = round(relative_y / current_cell_size)

            # Validate if the click is within the board boundaries
            if 0 <= row < self.game.board_size_internal and \
               0 <= col < self.game.board_size_internal:
                # Check if click is reasonably close to an intersection
                # This adds a tolerance: click must be within stone_radius of an intersection
                # This makes clicking more intuitive than just rounding.
                dist_x = relative_x - col * current_cell_size
                dist_y = relative_y - row * current_cell_size
                # Using stone_radius as a click tolerance region around the intersection
                # (could also use cell_size / 2 for a larger clickable area per cell)
                click_tolerance = self.stone_radius if self.stone_radius else current_cell_size * 0.4 
                if abs(dist_x) < click_tolerance and abs(dist_y) < click_tolerance:
                    self.parent_gui._handle_cell_click(row, col)
        else:
            super().mousePressEvent(event)


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

        # Custom Board Widget
        self.board_widget = BoardWidget(self) # Pass self (GomokuPyQtGUI instance)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.board_widget) # Add the custom board widget
        main_layout.addWidget(self.new_game_button)

        self.setLayout(main_layout)
        
        self._update_status_display() # Initial status update

    def _update_status_display(self, message=None):
        """Updates the status label display."""
        if message:
            self.status_label.setText(message)
        else:
            if not self.game.game_over: # Check if game is over
                current_player_symbol = self.game.current_player
                display_name = "Black" if current_player_symbol == 'X' else "White"
                self.status_label.setText(f"Player {display_name}'s turn")
            # If game is over, the message should be set by win/draw logic,
            # or a specific "Game Over" message if desired.

    def _handle_cell_click(self, row, col):
        """Handles a click on a board cell."""
        if self.game.board[row][col] == ' ' and not self.game.game_over:
            player_symbol = self.game.current_player # Symbol of player making the move
            
            if self.game.make_move(row, col): # make_move returns True if successful
                # UI update for the clicked cell will be handled by BoardWidget's paintEvent
                self.board_widget.update() # Trigger repaint of BoardWidget

                if self.game.check_win():
                    self.game.game_over = True
                    # Note: check_win() uses self.game.current_player, which is the player who just made the move.
                    winner_display_name = "Black" if player_symbol == 'X' else "White"
                    self._update_status_display(f"Player {winner_display_name} wins!")
                    # Board interactivity is handled by BoardWidget based on game.game_over
                    QMessageBox.information(self, "Game Over", f"Player {winner_display_name} wins!")
                elif self.game.check_draw():
                    self.game.game_over = True
                    self._update_status_display("It's a draw!")
                    # Board interactivity is handled by BoardWidget based on game.game_over
                    QMessageBox.information(self, "Game Over", "It's a draw!")
                else:
                    self.game.switch_player()
                    self._update_status_display()
            # else: move was invalid, BoardWidget should not have emitted signal or handled it.

    def _new_game(self):
        """Starts a new game."""
        self.game.reset_game() # Resets game logic (board, current_player, game_over)
        self.board_widget.update() # Repaint the board widget to show empty state
        self._update_status_display() # Update to "Player X's turn"

    # _disable_board method is removed as BoardWidget will handle its own interactivity
    # based on self.game.game_over state.

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GomokuPyQtGUI()
    window.show()
    sys.exit(app.exec_())
