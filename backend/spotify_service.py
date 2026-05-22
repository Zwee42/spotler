import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spotipy.cache_handler
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, FRONTEND_URL
from database import get_db_connection
import uuid

def generate_state():
    """Generate a random state for OAuth"""
    return secrets.token_urlsafe(32)

def get_spotify_oauth():
    """Create and return SpotifyOAuth instance"""
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="user-top-read user-read-private user-read-email",
        cache_handler=spotipy.cache_handler.MemoryCacheHandler()
    )

def get_auth_url(state: str):
    """Get Spotify authorization URL"""
    oauth = get_spotify_oauth()
    return oauth.get_authorize_url(state=state)

def exchange_code_for_token(code: str):
    """Exchange authorization code for access token"""
    oauth = get_spotify_oauth()
    token_info = oauth.get_access_token(code)
    return token_info

def get_current_user_info(access_token: str):
    """Get current user info from Spotify"""
    sp = spotipy.Spotify(auth=access_token)
    return sp.current_user()

def get_user_top_artists(access_token: str, limit: int = 50):
    """Get user's top artists from Spotify api limit max 50"""
    sp = spotipy.Spotify(auth=access_token)
    results = sp.current_user_top_artists(limit=limit, time_range='medium_term')
    return results['items']

def save_user_to_db(spotify_data: dict, token_info: dict) -> str:
    """Save or update user in database, returns user_id"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    spotify_id = spotify_data['id']
    user_id = str(uuid.uuid4())
    
    expires_at = None
    if 'expires_in' in token_info:
        expires_at = int((datetime.now() + timedelta(seconds=token_info['expires_in'])).timestamp())
    
    try:
        cursor.execute("""
        INSERT INTO users (id, spotify_id, display_name, email, access_token, refresh_token, token_expires_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            spotify_id,
            spotify_data.get('display_name', ''),
            spotify_data.get('email', ''),
            token_info['access_token'],
            token_info.get('refresh_token'),
            expires_at
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        # User already exists, update tokens
        cursor.execute("""
        UPDATE users SET access_token = ?, refresh_token = ?, token_expires_at = ?
        WHERE spotify_id = ?
        """, (
            token_info['access_token'],
            token_info.get('refresh_token'),
            expires_at,
            spotify_id
        ))
        conn.commit()
        # Get existing user_id
        cursor.execute("SELECT id FROM users WHERE spotify_id = ?", (spotify_id,))
        user_id = cursor.fetchone()['id']
    
    conn.close()
    return user_id

def save_artists_to_db(user_id: str, artists: list):
    """Save user's artists to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for artist in artists:
        artist_id = artist['id']
        image_url = None
        if artist.get('images'):
            image_url = artist['images'][0]['url']
        
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO artists (id, user_id, spotify_id, name, popularity, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                f"{user_id}_{artist_id}",
                user_id,
                artist['id'],
                artist['name'],
                artist.get('popularity', 0),
                image_url
            ))
        except Exception as e:
            print(f"Error saving artist {artist['name']}: {e}")
    
    conn.commit()
    conn.close()

def get_user_artists(user_id: str, limit: int = None) -> list:
    """Get user's artists from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if limit:
        cursor.execute("""
        SELECT * FROM artists WHERE user_id = ?
        ORDER BY popularity DESC
        LIMIT ?
        """, (user_id, limit))
    else:
        cursor.execute("""
        SELECT * FROM artists WHERE user_id = ?
        ORDER BY popularity DESC
        """, (user_id,))
    
    artists = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return artists

def get_random_artist(user_id: str):
    """Get a random artist from user's collection"""
    import random
    artists = get_user_artists(user_id)
    if not artists:
        return None
    return random.choice(artists)


def sanitize_name(name: str) -> str:
    """Return a sanitized version of the artist name: lowercase letters, numbers and spaces only."""
    import re
    if not name:
        return ""
    # Keep only a-z letters, 0-9 numbers and spaces
    s = name.lower()
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return s


def get_random_artist_by_length(user_id: str, desired_length: int):
    """Get a random artist whose sanitized name length equals desired_length."""
    import random
    if desired_length is None or desired_length <= 0:
        return get_random_artist(user_id)

    artists = get_user_artists(user_id)
    filtered = []
    for a in artists:
        s = sanitize_name(a.get('name', ''))
        if len(s) == desired_length:
            # include sanitized name for convenience
            a['_sanitized_name'] = s
            filtered.append(a)

    if not filtered:
        return None

    return random.choice(filtered)

def user_exists(user_id: str) -> bool:
    """Check if user exists in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists
