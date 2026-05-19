<script lang="ts">
  import { getLoginUrl } from '../api'

  let loading = false
  let error = ''

  async function handleSpotifyLogin() {
    try {
      loading = true
      error = ''
      const authUrl = await getLoginUrl()
      window.location.href = authUrl
    } catch (_err) {
      error = 'Failed to initiate login'
      loading = false
    }
  }
</script>

<div class="flex flex-col items-center justify-center w-full h-screen bg-white">
  <div class="flex flex-col items-center gap-8">
    <!-- Logo/Title -->
    <div class="flex flex-col items-center gap-2">
      <h1 class="text-6xl font-bold text-slate-900">SPOTLER</h1>
      <p class="text-lg text-slate-500">Guess the artist in 6 tries</p>
    </div>

    <!-- Spotify Logo hint -->
    <div class="w-32 h-32 flex items-center justify-center">
      <svg viewBox="0 0 63 63" class="w-24 h-24" fill="#1DB954">
        <circle cx="31.5" cy="31.5" r="31.5" />
        <path
          d="M46.4 20.5c-3.2-1.9-8.5-2.3-12.9-1.4 2.2 1.5 4.1 3.8 5.2 6.5 1.1-2.8 3-5.1 5.2-6.5-1.2-.2-2.4-.3-3.5-.3 2.1 1.3 4 3.2 5.4 5.4 1.3-2.1 3.3-4 5.8-5.4-2.3-.9-4.7-1.3-7.2-1.3z"
          fill="white"
        />
      </svg>
    </div>

    <!-- Login Button -->
    <button
      on:click={handleSpotifyLogin}
      disabled={loading}
      class="px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-lg"
    >
      {loading ? 'Redirecting...' : 'Login with Spotify'}
    </button>

    {#if error}
      <p class="text-red-600 text-sm">{error}</p>
    {/if}

    <!-- Info -->
    <div class="mt-8 text-center text-slate-600 text-sm max-w-md">
      <p>Connect your Spotify account to play.</p>
      <p class="mt-2">We'll use your top listened artists to create the game.</p>
    </div>
  </div>
</div>

<style>
  :global(body) {
    background-color: white;
  }
</style>
