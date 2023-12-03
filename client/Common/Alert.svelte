<script lang="ts">
  import CloseIcon from "./CloseIcon.svelte";
  import { fade } from "svelte/transition";
  import { createEventDispatcher } from "svelte";
  const dispatch = createEventDispatcher<{ openAlert: boolean }>();

  export let alertID = "";
  export let alertClasses = "";

  //* CSS Props
  export let fading = false; //* If fade transition needed, set to true, and following will fade in and out over 400 milliseconds
  const duration = (fading) ? 400 : 0; // eslint-disable-line @typescript-eslint/no-unnecessary-condition
  export let invisible: boolean | null = null;
//TODO: Not sure `fading` needs to control the button visibility anymore + `invisible` might not need `null` either
  // Instead, an `autoFade` property could indicate an alert that hides itself, `fading` could toggle the transition on/off regardless
  // AND `invisible` could control if the view is in the DOM or not.
  // If `autoFade` was on, then a button might not be needed. A backup prop like `closeable` could force-provide a button if desired though!
</script>

{#if !invisible}
  <div transition:fade={{ delay: 0, duration }} id={alertID} class="alert {alertClasses} align-middle" role="alert">
    <slot>Alert!</slot>
    {#if fading || invisible !== null}
      <button type="button" class="close-btn text-white border-0" aria-label="Close" on:click={() => dispatch("openAlert", false)}>
        <CloseIcon />
      </button>
    {/if}
  </div>
{/if}

<style lang="less">
  @import "../CSS/variables";
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
    &:focus-visible {
      box-shadow: -2px 2px 0 0.1rem #ffffff90;
    }
  }
</style>