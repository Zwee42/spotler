<script lang="ts">
  export let letterStatuses: Record<string, 'correct' | 'present' | 'absent'> = {};
  export let onKeyPress: (key: string) => void = () => {};

  const rows = [
    ['1','2','3','4','5','6','7','8','9','0'],
    ['q','w','e','r','t','y','u','i','o','p'],
    ['a','s','d','f','g','h','j','k','l'],
    ['z','x','c','v','b','n','m']
  ];

  function getKeyClass(key: string, statuses: Record<string, 'correct' | 'present' | 'absent'>) {
    const status = statuses[key];
    const baseClass = "h-10 sm:h-12 flex-1 flex mx-0.5 justify-center items-center uppercase font-bold rounded transition-colors text-sm sm:text-base cursor-pointer hover:bg-slate-300";
    
    if (status === 'correct') {
      return `${baseClass} bg-green-500 text-white`;
    }
    if (status === 'present') {
      return `${baseClass} bg-yellow-500 text-white`;
    }
    if (status === 'absent') {
      return `${baseClass} bg-slate-400 text-white hover:bg-slate-500`;
    }
    return `${baseClass} bg-slate-200 text-slate-800`;
  }
</script>

<div class="w-full max-w-lg mt-6 mb-4 flex flex-col items-center select-none px-2">
  {#each rows as row}
    <div class="flex w-full mb-1 sm:mb-2 justify-center">
      {#each row as key}
        <div class={getKeyClass(key, letterStatuses)} on:click={() => onKeyPress(key)} on:keydown={(e) => e.key === 'Enter' && onKeyPress(key)} role="button" tabindex="0">
          {key}
        </div>
      {/each}
    </div>
  {/each}
  <div class="flex w-full mb-1 sm:mb-2 justify-center">
    <div
      class="h-10 sm:h-12 w-3/4 flex mx-0.5 justify-center items-center uppercase font-bold rounded transition-colors text-sm sm:text-base cursor-pointer bg-slate-200 hover:bg-slate-300 text-slate-800"
      on:click={() => onKeyPress(' ')}
      on:keydown={(e) => e.key === 'Enter' && onKeyPress(' ')}
      role="button"
      tabindex="0"
    >
      SPACE
    </div>
  </div>
</div>
