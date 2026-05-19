# Spotler - Wordle with Spotify Artists

A Wordle-like game using Spotify artists that the user actually listens to.

## Setup

### Backend Setup

1. Create a `.env` file in the `backend` directory:
   ```
   cp backend/.env.example backend/.env
   ```

2. Register an app on [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Get your Client ID and Client Secret
   - Set Redirect URI to `http://127.0.0.1:8000/auth/callback`

3. Update `.env` with your credentials:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/callback
   FRONTEND_URL=http://localhost:5173
   ```

4. Install Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

5. Run the backend:
   ```bash
   python main.py
   ```
   The API will be available at `http://127.0.0.1:8000`

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://127.0.0.1:5173`

## How to Play

1. Click "Login with Spotify" and authorize the app
2. The game will fetch your top 50 artists
3. A random artist from your library is selected
4. You have 6 attempts to guess the artist name
5. Letters turn green if correct and in the right position
6. Letters turn yellow if in the word but wrong position
7. Letters turn gray if not in the word

## Tech Stack

- **Frontend**: Svelte, TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLite3
- **Auth**: Spotify OAuth 2.0
