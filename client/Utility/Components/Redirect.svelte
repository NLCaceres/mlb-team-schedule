<script lang="ts">
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-navigator';

  export let to;

  onMount(() => { navigate(to, { replace: true }); } );
</script>