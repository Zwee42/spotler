<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte'
  import { startNewGame, getGameState, makeGuess, getArtists } from '../api'
  import GameBoard from './GameBoard.svelte'
  import Keyboard from './Keyboard.svelte'

  const dispatch = createEventDispatcher<{ logout: void }>()

  export let userId: string

  interface FeedbackItem {
    letter: string
    status: 'correct' | 'present' | 'absent'
  }

  interface Artist {
    name: string
    popularity: number
    image_url: string
  }

  interface GameState {
    game_id: string
    status: 'active' | 'won' | 'lost'
    guesses: string[]
    guesses_count: number
    guesses_remaining: number
    correct_answer: string | null
    feedbacks: FeedbackItem[][]
    target_length: number
    max_guesses: number
  }

  let gameId: string | null = null
  let gameState: GameState | null = null
  let loading = false
  let error = ''
  let currentGuess = ''

  let artists: Artist[] = []
  let showArtists = false

  $: letterStatuses = computeLetterStatuses(gameState?.feedbacks)

  function computeLetterStatuses(feedbacks: FeedbackItem[][] | undefined) {
    const statuses: Record<string, 'correct' | 'present' | 'absent'> = {}
    if (!feedbacks) return statuses

    const hierarchy = { 'correct': 3, 'present': 2, 'absent': 1 }

    feedbacks.forEach(row => {
      row.forEach(item => {
        const curLevel = hierarchy[statuses[item.letter]] || 0
        const newLevel = hierarchy[item.status] || 0
        if (newLevel > curLevel) {
          statuses[item.letter] = item.status
        }
      })
    })

    return statuses
  }

  async function initializeGame() {
    try {
      loading = true
      error = ''
      const response = await startNewGame(userId)
      gameId = response.game_id
      const state = await getGameState(gameId as string)
      gameState = state
      loading = false
    } catch (_err: unknown) {
      error = 'Failed to start game'
      loading = false
    }
  }

  async function handleGuess() {
    if (!gameId || !currentGuess.trim()) return

    try {
      loading = true
      error = ''
      const result = await makeGuess(gameId, currentGuess.trim())

      if (result.success === false && result.message === 'You already guessed that') {
        error = 'You already guessed that'
        loading = false
        return
      }

      const state = await getGameState(gameId)
      gameState = state
      currentGuess = ''
    } catch (_err: unknown) {
      error = 'Failed to submit guess'
    }
    loading = false
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !loading) {
      handleGuess()
    }
  }

  function handleNewGame() {
    gameId = null
    gameState = null
    currentGuess = ''
    error = ''
    initializeGame()
  }

  function handleLogout() {
    dispatch('logout')
  }

  onMount(async () => {
    if (!gameState && userId) {
      initializeGame()
    }
    
    if (userId) {
      try {
        artists = await getArtists(userId)
      } catch (e) {
        console.error('Could not fetch artists:', e)
      }
    }
  })
</script>

<div class="w-full min-h-screen flex flex-col items-center py-10 bg-white p-4">
  <div class="w-full max-w-md">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-4xl font-bold text-slate-900">SPOTLER</h1>
      <button
        on:click={handleLogout}
        class="text-sm text-slate-500 hover:text-slate-900 underline"
      >
        Logout
      </button>
    </div>

    <!-- Artists Dropdown -->
    <div class="mb-4">
      <button
        on:click={() => showArtists = !showArtists}
        class="w-full text-left px-4 py-3 bg-slate-100 hover:bg-slate-200 text-slate-800 font-medium rounded flex justify-between items-center transition-colors"
      >
        <span>Possible Artists</span>
        <span class="bg-slate-900 text-white text-xs px-2 py-1 rounded-full">{artists.length}</span>
      </button>
      
      {#if showArtists}
        <div class="mt-2 max-h-48 overflow-y-auto bg-white border-2 border-slate-200 rounded shadow-lg">
          {#each artists as artist}
             <div class="px-4 py-2 border-b border-slate-100 last:border-0 hover:bg-slate-50 flex items-center gap-3">
               {#if artist.image_url}
                 <img src={artist.image_url} alt={artist.name} class="w-8 h-8 rounded-full object-cover" />
               {:else}
                 <div class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 text-xs">{artist.name.charAt(0)}</div>
               {/if}
               <span class="text-sm font-medium text-slate-800">{artist.name}</span>
             </div>
          {/each}
          {#if artists.length === 0}
             <div class="px-4 py-3 text-sm text-slate-500 text-center">No artists found</div>
          {/if}
        </div>
      {/if}
    </div>

    {#if gameState && gameState.status === 'active'}
      <GameBoard {gameState} />

      <!-- Input Section -->
      <div class="mt-8 flex gap-2">
        <div class="flex-1 relative flex items-center">
          <input
            type="text"
            bind:value={currentGuess}
            on:keydown={handleKeydown}
            placeholder="Enter artist name..."
            disabled={loading}
            class="w-full px-4 py-3 pr-12 border-2 border-slate-300 rounded focus:outline-none focus:border-slate-900 disabled:bg-slate-100 uppercase"
          />
          <span class="absolute right-4 text-slate-400 text-sm font-medium pointer-events-none">
            {currentGuess.length}
          </span>
        </div>
        <button
          on:click={handleGuess}
          disabled={loading || !currentGuess.trim()}
          class="px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? '...' : 'Guess'}
        </button>
      </div>

      <Keyboard
        {letterStatuses}
        onKeyPress={(key) => {
          if (!loading) currentGuess += key;
        }}
      />

      {#if error}
        <p class="mt-2 text-red-600 text-sm">{error}</p>
      {/if}
    {:else if gameState && gameState.status === 'won'}
      <div class="flex flex-col items-center gap-4">
        <div class="text-center">
          <p class="text-sm text-slate-500 mb-2">Guessed in</p>
          <p class="text-5xl font-bold text-green-600">{gameState.guesses_count}</p>
        </div>
        <p class="text-lg text-slate-900">
          The artist was <span class="font-bold">{gameState.correct_answer}</span>
        </p>
        <button
          on:click={handleNewGame}
          class="mt-4 px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded transition-colors"
        >
          Play Again
        </button>
      </div>
    {:else if gameState && gameState.status === 'lost'}
      <div class="flex flex-col items-center gap-4">
        <p class="text-xl text-slate-900 font-bold">Game Over</p>
        <p class="text-lg text-slate-900">
          The artist was <span class="font-bold">{gameState.correct_answer}</span>
        </p>
        <div class="text-sm text-slate-500">
          <p>Your guesses:</p>
          <p>{gameState.guesses.join(', ')}</p>
        </div>
        <button
          on:click={handleNewGame}
          class="mt-4 px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded transition-colors"
        >
          Try Again
        </button>
      </div>
    {/if}
  </div>
</div>

<style>
  :global(body) {
    background-color: white;
  }
</style>
