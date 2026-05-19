import { describe, it, expect, vi } from 'vitest'
import { getLoginUrl, getArtists, startNewGame } from '../api'
import { api } from '../api'

vi.mock('axios', () => {
  return {
    default: {
      create: vi.fn(() => ({
        get: vi.fn(),
        post: vi.fn(),
      })),
    }
  }
})

describe('API functions', () => {
  it('getLoginUrl returns auth_url from response', async () => {
    const mockUrl = 'http://auth.url'
    vi.mocked(api.get).mockResolvedValueOnce({ data: { auth_url: mockUrl } })
    
    const url = await getLoginUrl()
    
    expect(url).toBe(mockUrl)
    expect(api.get).toHaveBeenCalledWith('/auth/login')
  })

  it('getArtists calls /artists with user_id', async () => {
    const mockArtists = [{ id: '1', name: 'Artist' }]
    vi.mocked(api.get).mockResolvedValueOnce({ data: { artists: mockArtists } })
    
    const artists = await getArtists('user-123')
    
    expect(artists).toEqual(mockArtists)
    expect(api.get).toHaveBeenCalledWith('/artists', { params: { user_id: 'user-123' } })
  })

  it('startNewGame calls /game/new with user_id', async () => {
    const mockGame = { game_id: 'game-123', target_length: 5 }
    vi.mocked(api.post).mockResolvedValueOnce({ data: mockGame })
    
    const game = await startNewGame('user-123')
    
    expect(game).toEqual(mockGame)
    expect(api.post).toHaveBeenCalledWith('/game/new', null, { params: { user_id: 'user-123' } })
  })
})
