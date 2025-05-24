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
        "boardSize": game_instance.board_size_internal
    }

@app.get("/api/game_state")
async def api_get_game_state():
    """Returns the current state of the game."""
    return get_game_state_dict(game)

@app.post("/api/make_move")
async def api_make_move(move: MoveRequest):
    """Handles a player's move. Expects a JSON body with 'row' and 'col'."""
    message = ""
    move_success = False

    if game.game_over:
        message = "Game is already over."
    else:
        # GomokuGame.make_move handles validation (bounds, cell taken)
        # and uses game.current_player
        move_success = game.make_move(move.row, move.col) 
        
        if move_success:
            if game.check_win(): # check_win uses game.current_player (who just made the move)
                game.game_over = True
                message = f"Player {game.current_player} wins!"
            elif game.check_draw():
                game.game_over = True
                message = "It's a draw!"
            else:
                game.switch_player()
                message = "Move successful."
        else:
            # make_move returned False, indicating an invalid move
            message = "Invalid move. Cell might be taken or out of bounds."

    response_state = get_game_state_dict(game)
    response_state["message"] = message
    response_state["moveSuccess"] = move_success
    return response_state

@app.post("/api/new_game")
async def api_new_game():
    """Resets the game to its initial state."""
    game.reset_game()
    return get_game_state_dict(game)

# To run this app (from the terminal, assuming uvicorn is installed):
# uvicorn gomoku_web_app:app --reload
