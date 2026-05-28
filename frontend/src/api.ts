import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function getLoginUrl() {
  const response = await api.get('/auth/login')
  return response.data.auth_url
}

export async function getArtists(userId: string) {
  const response = await api.get('/artists', { params: { user_id: userId } })
  return response.data.artists
}

export async function startNewGame(userId: string) {
  const response = await api.post('/game/new', null, { params: { user_id: userId } })
  return response.data
}

export async function getGameState(gameId: string) {
  const response = await api.get(`/game/${gameId}`)
  return response.data
}

export async function makeGuess(gameId: string, guess: string) {
  const response = await api.post(`/game/${gameId}/guess`, { guess })
  return response.data
}
