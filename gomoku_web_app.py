from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles # Added for static file serving
from pydantic import BaseModel # Added for request model
from gomoku import GomokuGame # Assuming gomoku.py is in the same directory

# Initialize FastAPI app
app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic model for make_move request
class MoveRequest(BaseModel):
    row: int
    col: int

# Pydantic model for new_game request
class NewGameRequest(BaseModel):
    game_mode: str | None = None # e.g., "1P", "2P"
    ai_difficulty: str | None = None # e.g., "Easy", "Medium", "Hard"

# Initialize Jinja2Templates for serving HTML
# (The "templates" directory must exist at the root for this to work)
templates = Jinja2Templates(directory="templates")

# Initialize the Gomoku game instance
# This will be a single global game instance for now
game = GomokuGame()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # This endpoint will serve the main game page.
    # The actual index.html will be created in a later step.
    # For now, this setup assumes an index.html will exist in the templates directory.
    return templates.TemplateResponse("index.html", {"request": request})

# Helper function to get the current game state
def get_game_state_dict(game_instance: GomokuGame):
    return {
        "board": game_instance.board,
        "currentPlayer": "Black" if game_instance.current_player == 'X' else "White",
        "gameOver": game_instance.game_over,
        "boardSize": game_instance.board_size_internal,
        "gameMode": game_instance.game_mode,          # New
        "aiDifficulty": game_instance.ai_difficulty  # New
    }

@app.get("/api/game_state")
async def api_get_game_state():
    """Returns the current state of the game."""
    return get_game_state_dict(game)

@app.post("/api/make_move")
async def api_make_move(move: MoveRequest):
    message = ""
    human_move_made_successfully = False
    ai_move_made_this_turn = False # To track if AI made a move this turn

    if game.game_over:
        message = "Game is already over."
    # Pre-emptive check, game.make_move also validates.
    elif not (0 <= move.row < game.board_size_internal and \
              0 <= move.col < game.board_size_internal and \
              game.board[move.row][move.col] == ' '):
        message = "Invalid move (out of bounds or cell taken)."
    else:
        # Human Player's Move
        # Assuming Human is 'X' in 1P mode. game.current_player should be 'X'.
        if game.game_mode == "1P" and game.current_player != 'X':
             message = "Not your turn (AI is thinking or error)."
        else:
            human_move_made_successfully = game.make_move(move.row, move.col)

            if human_move_made_successfully:
                if game.check_win():
                    game.game_over = True
                    message = f"Player {get_game_state_dict(game)['currentPlayer']} wins!"
                elif game.check_draw():
                    game.game_over = True
                    message = "It's a draw!"
                else:
                    # Potentially AI's turn
                    if game.game_mode == "1P":
                        game.switch_player() # Switch to AI ('O')

                        if game.ai_difficulty == "Easy" and not game.game_over:
                            ai_move_made = game.make_ai_move_easy()
                            ai_move_made_this_turn = True
                            
                            if ai_move_made:
                                if game.check_win(): # AI wins
                                    game.game_over = True
                                    # currentPlayer in state dict will be AI's display name
                                    message = f"Player {get_game_state_dict(game)['currentPlayer']} (AI) wins!"
                                elif game.check_draw(): # Draw after AI move
                                    game.game_over = True
                                    message = "It's a draw!"
                                # AI made a move, current_player is AI. Will be switched back if game not over.
                            else: # AI couldn't make a move
                                if not game.game_over : # Avoid overriding win/draw from human move
                                    message = "AI could not make a move (board might be full)."
                        
                        # Switch back to Human ('X') if game is not over
                        if not game.game_over:
                            game.switch_player() 
                    
                    else: # 2P mode or no mode set
                        game.switch_player()
                    
                    if not message: # If no win/draw message set by human or AI
                        message = "Move successful."
            else: # Human move failed (already caught by pre-checks, but as fallback)
                message = "Invalid move." # Should be more specific if possible
    
    response_state = get_game_state_dict(game)
    
    # Ensure message from win/draw takes precedence
    if "wins!" not in message.lower() and "draw!" not in message.lower():
        if not message and human_move_made_successfully:
            response_state["message"] = "Move successful."
        elif message: # Use message from logic above if it's set (e.g. AI specific messages)
             response_state["message"] = message
        elif not human_move_made_successfully and not game.game_over : # Default invalid if no other message
             response_state["message"] = "Invalid move."
    else: # Win/draw message is already set
        response_state["message"] = message


    response_state["moveSuccess"] = human_move_made_successfully
    return response_state

@app.post("/api/new_game")
async def api_new_game(settings: NewGameRequest):
    """Resets the game to its initial state with new settings."""
    game.reset_game(game_mode=settings.game_mode, ai_difficulty=settings.ai_difficulty)
    return get_game_state_dict(game)

# To run this app (from the terminal, assuming uvicorn is installed):
# uvicorn gomoku_web_app:app --reload
