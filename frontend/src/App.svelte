<script lang="ts">
  import { onMount } from 'svelte'
  import Login from './components/Login.svelte'
  import Game from './components/Game.svelte'
  import './app.css'

  let userId: string | null = null
  let isAuthenticated = false

  onMount(() => {
    const params = new URLSearchParams(window.location.search)
    const paramUserId = params.get('user_id')
    
    if (paramUserId) {
      userId = paramUserId
      isAuthenticated = true
      localStorage.setItem('spotler_user_id', paramUserId)
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname)
    } else {
      const stored = localStorage.getItem('spotler_user_id')
      if (stored) {
        userId = stored
        isAuthenticated = true
      }
    }
  })

  function handleLogin(event: CustomEvent<string>) {
    userId = event.detail
    isAuthenticated = true
    localStorage.setItem('spotler_user_id', userId)
  }

  function handleLogout() {
    userId = null
    isAuthenticated = false
    localStorage.removeItem('spotler_user_id')
  }
</script>

<main class="w-full h-screen flex items-center justify-center bg-white">
  {#if isAuthenticated && userId}
    <Game {userId} on:logout={handleLogout} />
  {:else}
    <Login on:login={handleLogin} />
  {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
  }
</style>
