import uuid
from datetime import datetime
from typing import Optional
from database import get_db_connection
import sqlite3


def start_new_game(user_id: str) -> dict:
    """Start a new game for the user"""
    from spotify_service import get_random_artist
    
    artist = get_random_artist(user_id)
    if not artist:
        raise ValueError("No artists found for user")
    
    game_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO games (id, user_id, artist_id, artist_name, guesses, status)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        game_id,
        user_id,
        artist['id'],
        artist['name'],
        "",
        "active"
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "game_id": game_id,
        "artist_name": artist['name']
    }


def make_guess(game_id: str, guess: str) -> dict:
    """Process a guess for the game"""
    from config import MAX_GUESSES
    from spotify_service import sanitize_name
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM games WHERE id = ?", (game_id,))
    game = cursor.fetchone()
    
    if not game:
        conn.close()
        raise ValueError("Game not found")
    
    if game['status'] != 'active':
        conn.close()
        raise ValueError("Game is not active")
    
    artist_name = game['artist_name']
    print(f"Processing guess '{guess}' for game {game_id} (target: '{artist_name}')")
    # Use sanitized forms for comparison and feedback
    target_sanitized = sanitize_name(artist_name)
    guess_sanitized = sanitize_name(guess)
    
    # Parse existing guesses
    guesses = []
    if game['guesses']:
        guesses = game['guesses'].split(',')
    
    if guess_sanitized in guesses:
        conn.close()
        return {
            "success": False,
            "message": "You already guessed that",
            "game_over": False
        }
    
    guesses.append(guess_sanitized)
    
    # Check if correct (sanitized)
    is_correct = guess_sanitized == target_sanitized
    
    # Check game over
    is_game_over = len(guesses) >= MAX_GUESSES or is_correct
    
    # Update game
    new_status = 'won' if is_correct else ('lost' if len(guesses) >= MAX_GUESSES else 'active')
    
    cursor.execute("""
    UPDATE games SET guesses = ?, status = ?, completed_at = ?
    WHERE id = ?
    """, (
        ','.join(guesses),
        new_status,
        datetime.now() if is_game_over else None,
        game_id
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "success": is_correct,
        "is_correct": is_correct,
        "game_over": is_game_over,
        "correct_answer": artist_name if is_game_over else None,
        "guesses_remaining": MAX_GUESSES - len(guesses),
        "status": new_status,
        "guess_feedback": get_guess_feedback(guess_sanitized, target_sanitized)
    }


def get_guess_feedback(guess: str, target: str) -> list:
    """
    Get feedback for each letter in the guess
    Returns list of dicts with letter and status (correct, present, absent)
    """
    feedback = [{"letter": char, "status": "absent"} for char in guess]
    
    target_counts = {}
    for char in target:
        target_counts[char] = target_counts.get(char, 0) + 1
        
    # First pass: find correct letters (green)
    for i in range(min(len(guess), len(target))):
        if guess[i] == target[i]:
            feedback[i]["status"] = "correct"
            target_counts[guess[i]] -= 1
            
    # Second pass: find present letters (yellow)
    for i in range(len(guess)):
        if feedback[i]["status"] != "correct":
            char = guess[i]
            if target_counts.get(char, 0) > 0:
                feedback[i]["status"] = "present"
                target_counts[char] -= 1
                
    return feedback


def get_game_state(game_id: str) -> dict:
    """Get the current state of a game"""
    from config import MAX_GUESSES
    from spotify_service import sanitize_name
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM games WHERE id = ?", (game_id,))
    game = cursor.fetchone()
    conn.close()
    
    if not game:
        raise ValueError("Game not found")
    
    guesses = []
    if game['guesses']:
        guesses = game['guesses'].split(',')

    # Compute sanitized target and per-guess feedback so frontend can render
    target = game['artist_name']
    target_sanitized = sanitize_name(target)
    feedbacks = []
    for g in guesses:
        gs = sanitize_name(g)
        feedbacks.append(get_guess_feedback(gs, target_sanitized))

    return {
        "game_id": game_id,
        "status": game['status'],
        "guesses": guesses,
        "guesses_count": len(guesses),
        "guesses_remaining": MAX_GUESSES - len(guesses),
        "correct_answer": game['artist_name'] if game['status'] != 'active' else None,
        "feedbacks": feedbacks,
        "target_length": len(target_sanitized),
        "max_guesses": MAX_GUESSES
    }
