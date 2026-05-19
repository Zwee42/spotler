from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import secrets
from config import FRONTEND_URL
from database import init_db
from spotify_service import (
    generate_state, get_auth_url, exchange_code_for_token,
    get_current_user_info, get_user_top_artists, save_user_to_db,
    save_artists_to_db, get_user_artists, user_exists
)
from game_service import start_new_game, make_guess, get_game_state

app = FastAPI()

# Initialize database
init_db()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store states for CSRF protection
auth_states = {}


class GuessRequest(BaseModel):
    guess: str


@app.get("/")
def read_root():
    return {"message": "Spotler API - Wordle with Spotify Artists"}


@app.get("/auth/login")
def login():
    """Initiate Spotify OAuth flow"""
    state = generate_state()
    auth_states[state] = True
    auth_url = get_auth_url(state)
    return {"auth_url": auth_url}


@app.get("/auth/callback")
def auth_callback(code: str, state: str):
    """Handle Spotify OAuth callback"""
    if state not in auth_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    del auth_states[state]
    
    try:
        token_info = exchange_code_for_token(code)
        user_info = get_current_user_info(token_info['access_token'])
        user_id = save_user_to_db(user_info, token_info)
        
        # Fetch and save user's top artists
        artists = get_user_top_artists(token_info['access_token'])
        save_artists_to_db(user_id, artists)
        
        # Redirect to frontend with user_id
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?user_id={user_id}",
            status_code=302
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/artists")
def get_artists(user_id: str = Query(...)):
    """Get user's artists"""
    if not user_exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    artists = get_user_artists(user_id)
    return {"artists": artists}


@app.post("/game/new")
def new_game(user_id: str = Query(...)):
    """Start a new game"""
    if not user_exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        game_data = start_new_game(user_id)
        return {
            "game_id": game_data["game_id"],
            "message": "Game started"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/game/{game_id}")
def get_game(game_id: str):
    """Get game state"""
    try:
        game_state = get_game_state(game_id)
        return game_state
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/game/{game_id}/guess")
def post_guess(game_id: str, request: GuessRequest):
    """Make a guess"""
    try:
        result = make_guess(game_id, request.guess)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
