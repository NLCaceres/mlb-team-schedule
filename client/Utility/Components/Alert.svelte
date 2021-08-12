<script lang="ts">
  import { fade } from 'svelte/transition';
  import { createEventDispatcher } from 'svelte';
	const dispatch = createEventDispatcher();
  import CloseIcon from "./CloseIcon.svelte";

  export let alertID;
  export let alertClasses = '';

  //* CSS Props
  export let fading = false;
  export let invisible: boolean | null = null;
</script>

{#if !invisible}
  <div transition:fade id="{alertID}" class="alert {alertClasses} align-middle {(fading) ? 'alert-dismissable fade show' : ''}" role="alert">
      <slot>Alert!</slot>
      {#if fading || invisible !== null}
        <button type="button" class="close-btn text-white border-0" aria-label="Close" on:click="{e => dispatch('openAlert', false)}"> 
          <CloseIcon />
        </button>
      {/if}
  </div>
{/if}

<style lang="less">
  @import "../Less/variables";
  div.alert {
    position: fixed;
    color: white;
    left: 0;
    right: 0;
    bottom: 30%;
    margin-left: auto;
    margin-right: auto;
    @media @max575 {
      width: 75%;
    }
    width: 40%;
    @media @min1440 {
      width: 20%;
    }
  }
  button.close-btn {
    position: absolute;
    right: 0;
    top: 0;
    background-color: transparent;
  }
</style>