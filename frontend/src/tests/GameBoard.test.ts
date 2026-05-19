import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/svelte'
import GameBoard from '../components/GameBoard.svelte'

describe('GameBoard Component', () => {
  it('renders correct number of tiles based on target length and max guesses', () => {
    const mockGameState = {
      game_id: '123',
      status: 'active' as const,
      guesses: ['abc', 'def'],
      guesses_count: 2,
      guesses_remaining: 4,
      correct_answer: null,
      max_guesses: 6,
      target_length: 5,
      feedbacks: [
        [
          { letter: 'a', status: 'absent' },
          { letter: 'b', status: 'present' },
          { letter: 'c', status: 'correct' },
          { letter: 'x', status: 'absent' },
          { letter: 'y', status: 'absent' },
        ],
        [
          { letter: 'd', status: 'absent' },
          { letter: 'e', status: 'absent' },
          { letter: 'f', status: 'absent' },
          { letter: 'g', status: 'absent' },
          { letter: 'h', status: 'absent' },
        ]
      ]
    }

    const { container } = render(GameBoard, {
      props: { gameState: mockGameState }
    })

    // 6 rows * 5 letters = 30 tiles
    // Empty tiles use div with w-10 class. Rendered feedback tiles also have w-10.
    const allTiles = container.querySelectorAll('.w-10')
    expect(allTiles.length).toBe(30)

    // First row verification
    const correctTile = container.querySelector('.bg-green-600')
    expect(correctTile).toBeInTheDocument()
    expect(correctTile?.textContent).toContain('C')
    
    // Check present tile
    const presentTile = container.querySelector('.bg-yellow-500')
    expect(presentTile).toBeInTheDocument()
    expect(presentTile?.textContent).toContain('B')
  })
})
