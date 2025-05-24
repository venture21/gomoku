document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('gomoku-board');
    const ctx = canvas.getContext('2d');
    const gameStatusElement = document.getElementById('game-status');
    const newGameButton = document.getElementById('new-game-button'); // Will be used in a later step

    const PADDING = 20; // Padding around the board
    let CELL_SIZE;      // To be calculated
    let STONE_RADIUS;   // To be calculated
    let BOARD_ORIGIN_X; // Top-left X of the grid
    let BOARD_ORIGIN_Y; // Top-left Y of the grid
    let boardData = [];   // To store the game board state
    let boardSize = 15; // Default, will be updated from backend

    async function fetchGameStateAndDraw() {
        try {
            const response = await fetch('/api/game_state');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const gameState = await response.json();

            boardData = gameState.board;
            boardSize = gameState.boardSize; // Ensure backend sends this

            // Set fixed canvas size (can also be done in HTML or CSS)
            // Ensure this matches or is compatible with CSS if also styled there
            // Canvas size is set before drawing to ensure calculations are correct.
            // If canvas.width/height are set in HTML, this might be redundant
            // but useful if we want JS to control the rendering dimensions precisely.
            // For this task, let's assume the HTML/CSS provides a base, and JS adapts.
            // The problem description implies a fixed size of 450x450 for now.
            canvas.width = 450; 
            canvas.height = 450;

            drawBoard(gameState);
            updateStatus(gameState);
        } catch (error) {
            console.error("Failed to fetch game state:", error);
            gameStatusElement.textContent = "Error loading game state.";
        }
    }

    function drawBoard(gameState) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Calculate dimensions
        const availableWidth = canvas.width - 2 * PADDING;
        const availableHeight = canvas.height - 2 * PADDING;
        
        // Grid should be square, use the smaller dimension if canvas is not square
        const drawingAreaSize = Math.min(availableWidth, availableHeight);
        
        if (boardSize <= 1) return; // Avoid division by zero or nonsensical drawing

        CELL_SIZE = drawingAreaSize / (boardSize - 1); // Size of the gap between lines
        STONE_RADIUS = CELL_SIZE * 0.4; // Radius of the stone

        BOARD_ORIGIN_X = PADDING + (availableWidth - drawingAreaSize) / 2;
        BOARD_ORIGIN_Y = PADDING + (availableHeight - drawingAreaSize) / 2;
        
        const gridPixelSize = (boardSize - 1) * CELL_SIZE;

        // Draw board background (wood color)
        ctx.fillStyle = 'rgb(222, 184, 135)'; // Wood color
        ctx.fillRect(BOARD_ORIGIN_X, BOARD_ORIGIN_Y, gridPixelSize, gridPixelSize);

        // Draw grid lines
        ctx.strokeStyle = '#000'; // Black color for lines
        ctx.lineWidth = 1;
        for (let i = 0; i < boardSize; i++) {
            // Horizontal lines
            ctx.beginPath();
            ctx.moveTo(BOARD_ORIGIN_X, BOARD_ORIGIN_Y + i * CELL_SIZE);
            ctx.lineTo(BOARD_ORIGIN_X + gridPixelSize, BOARD_ORIGIN_Y + i * CELL_SIZE);
            ctx.stroke();

            // Vertical lines
            ctx.beginPath();
            ctx.moveTo(BOARD_ORIGIN_X + i * CELL_SIZE, BOARD_ORIGIN_Y);
            ctx.lineTo(BOARD_ORIGIN_X + i * CELL_SIZE, BOARD_ORIGIN_Y + gridPixelSize);
            ctx.stroke();
        }

        // Draw stones
        if (gameState && gameState.board) {
            for (let r = 0; r < boardSize; r++) {
                for (let c = 0; c < boardSize; c++) {
                    const player = gameState.board[r][c];
                    if (player !== ' ') {
                        const stoneX = BOARD_ORIGIN_X + c * CELL_SIZE;
                        const stoneY = BOARD_ORIGIN_Y + r * CELL_SIZE;
                        
                        ctx.beginPath();
                        ctx.arc(stoneX, stoneY, STONE_RADIUS, 0, 2 * Math.PI);
                        ctx.fillStyle = (player === 'X') ? '#000' : '#FFF'; // X=Black, O=White
                        ctx.fill();
                        ctx.strokeStyle = '#555'; // Border for stones
                        ctx.stroke();
                    }
                }
            }
        }
    }

    function updateStatus(gameState) {
        if (gameState.gameOver) {
            // The backend's /api/make_move response includes a "message" field for win/draw.
            // The /api/game_state might not, so we rely on the message from make_move.
            // If fetching initial state and it's already game over, we construct a generic message.
            if (gameState.message) { 
                 gameStatusElement.textContent = gameState.message;
            } else { 
                 // This state might occur if /api/game_state is called and game is over
                 // without a preceding make_move that set a specific win/draw message.
                 // For now, a generic "Game Over" is fine. A more robust solution
                 // might involve having the backend determine the winner for game_state.
                 gameStatusElement.textContent = "Game Over."; 
            }
        } else {
            const playerDisplayName = (gameState.currentPlayer === 'X') ? "Black" : "White";
            gameStatusElement.textContent = `Player ${playerDisplayName}'s turn`;
        }
    }

    // Initial setup
    // The canvas size is set in HTML/CSS or can be dynamically adjusted here.
    // For this task, we used fixed size in HTML (450x450).
    // If canvas.width and canvas.height were not set in HTML, we would need to set them here.
    // e.g., canvas.width = 450; canvas.height = 450;

    canvas.addEventListener('click', async (event) => {
        // Fetch current game state to check if game is over before processing click
        const currentStateResponse = await fetch('/api/game_state');
        const currentState = await currentStateResponse.json();
        if (currentState.gameOver) {
            // Optionally, provide feedback e.g. alert("Game is over. Please start a new game.");
            return; 
        }

        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        // Calculate column and row based on click position
        // (Ensure BOARD_ORIGIN_X, BOARD_ORIGIN_Y, CELL_SIZE are up-to-date, e.g. set in drawBoard)
        if (CELL_SIZE === undefined || CELL_SIZE <= 0) { // Check if CELL_SIZE is valid
            console.error("CELL_SIZE not initialized or invalid, cannot process click.");
            return;
        }
        const clickedCol = Math.round((x - BOARD_ORIGIN_X) / CELL_SIZE);
        const clickedRow = Math.round((y - BOARD_ORIGIN_Y) / CELL_SIZE);

        // Check if click is within valid grid cell range
        if (clickedRow >= 0 && clickedRow < boardSize && clickedCol >= 0 && clickedCol < boardSize) {
            try {
                const response = await fetch('/api/make_move', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ row: clickedRow, col: clickedCol }),
                });
                if (!response.ok) {
                    // Try to get error message from backend if available
                    const errorData = await response.json().catch(() => null);
                    const errorMessage = errorData?.message || `HTTP error! status: ${response.status}`;
                    throw new Error(errorMessage);
                }
                
                const result = await response.json();
                // The make_move API now returns the game state and a message.
                // So, we can directly use its response to update.
                boardData = result.board; // Update local board data
                drawBoard(result);        // Redraw using the full state from response
                updateStatus(result);     // Update status using the full state from response
                
                if (result.message && result.message !== "Move successful." && result.message !== "It's a draw!" && !result.message.includes("wins")) {
                     // Display backend messages e.g. "Cell already taken" via an alert for more direct feedback
                     // if not a win/draw message which is handled by updateStatus
                    // alert(result.message); // Potentially annoying, use gameStatusElement instead or a more subtle notification
                }


            } catch (error) {
                console.error("Failed to make move:", error);
                gameStatusElement.textContent = error.message || "Failed to make move.";
                // Optionally, re-fetch game state to ensure UI consistency if error was transient
                // await fetchGameStateAndDraw(); 
            }
        }
    });

    newGameButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/new_game', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            // new_game API returns the fresh game state
            const gameState = await response.json();
            
            boardData = gameState.board; // Update local board data
            drawBoard(gameState);        // Redraw
            updateStatus(gameState);     // Update status
            
        } catch (error) {
            console.error("Failed to start new game:", error);
            gameStatusElement.textContent = "Failed to start new game.";
        }
    });

    fetchGameStateAndDraw(); // Initial fetch and draw
}); // End of DOMContentLoaded
