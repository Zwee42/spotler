import { describe, it, expect, vi } from 'vitest'
import { render, fireEvent } from '@testing-library/svelte'
import Login from '../components/Login.svelte'
import * as api from '../api'

// Mock the API calls
vi.mock('../api', () => ({
  getLoginUrl: vi.fn(),
}))

describe('Login Component', () => {
  it('renders the title correctly', () => {
    const { getByText } = render(Login)
    expect(getByText('SPOTLER')).toBeInTheDocument()
    expect(getByText('Guess the artist in 6 tries')).toBeInTheDocument()
  })

  it('handles login button click', async () => {
    const mockUrl = 'http://localhost:8000/auth/login'
    vi.mocked(api.getLoginUrl).mockResolvedValue(mockUrl)
    
    // Partially mock window.location
    const originalLocation = window.location
    // @ts-expect-error Mocking window.location for test
    delete window.location
    // @ts-expect-error Mocking window.location for test
    window.location = { ...originalLocation, href: '' }

    const { getByText } = render(Login)
    const loginButton = getByText('Login with Spotify')
    
    await fireEvent.click(loginButton)
    
    // Wait for the async click handler
    await new Promise(resolve => setTimeout(resolve, 0))
    
    expect(api.getLoginUrl).toHaveBeenCalled()
    expect(window.location.href).toBe(mockUrl)

    // Restore window.location
    window.location = originalLocation
  })
})
