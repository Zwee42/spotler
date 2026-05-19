<script lang="ts">
  interface GameState {
    game_id: string
    status: 'active' | 'won' | 'lost'
    guesses: string[]
    guesses_count: number
    guesses_remaining: number
    correct_answer: string | null
    max_guesses?: number
    target_length?: number
    feedbacks?: Array<Array<{ letter: string; status: 'correct' | 'present' | 'absent' | string }>>
  }

  export let gameState: GameState

  function getLetterColor(status: string): string {
    switch (status) {
      case 'correct':
        return 'bg-green-600 text-white'
      case 'present':
        return 'bg-yellow-500 text-white'
      case 'absent':
        return 'bg-slate-300 text-slate-900'
      default:
        return 'bg-slate-200'
    }
  }
  // Frontend uses feedback provided by backend (gameState.feedbacks).
  // feedbacks is an array of rows; each row is array of {letter, status} with lowercase letters.
  function normalizeFeedbackRow(row: Array<{ letter: string; status: string }>) {
    return row.map((r) => ({ letter: (r.letter || '').toUpperCase(), status: r.status }))
  }
</script>

<div class="mb-8">
  <div class="text-center mb-4">
    <p class="text-slate-500 text-sm">Attempts remaining</p>
    <p class="text-3xl font-bold text-slate-900">{gameState.guesses_remaining}</p>
    <p>Target Length: {gameState.target_length}</p>
  </div>

  <!-- Guesses -->
  <div class="space-y-2">
    {#if gameState.feedbacks && gameState.target_length && gameState.max_guesses !== undefined}
      {#each gameState.feedbacks as row, rowIndex (rowIndex)}
        <div class="flex gap-1 justify-center">
          {#each Array(gameState.target_length) as _, colIndex (colIndex)}
            {#if colIndex < row.length}
              {@const letterInfo = normalizeFeedbackRow(row)[colIndex]}
                <div
                  class="w-10 h-10 flex items-center justify-center font-bold text-sm rounded {getLetterColor(
                    letterInfo.status
                  )}"
                >
                  {letterInfo.letter}
                </div>
            {:else}
              <div class="w-10 h-10 flex items-center justify-center border-2 border-slate-300 rounded"></div>
            {/if}
          {/each}
        </div>
      {/each}

      {#each Array(Math.max(0, gameState.max_guesses - gameState.feedbacks.length)) as _, placeholderRowIndex (placeholderRowIndex)}
        <div class="flex gap-1 justify-center">
          {#each Array(gameState.target_length) as _, placeholderColIndex (placeholderColIndex)}
            <div class="w-10 h-10 flex items-center justify-center border-2 border-slate-300 rounded"></div>
          {/each}
        </div>
      {/each}
    {/if}
  </div>
</div>

<style>
</style>
