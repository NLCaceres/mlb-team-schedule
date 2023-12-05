<script lang="ts">
  import A11yDialog from "a11y-dialog";
  import { createEventDispatcher, onMount } from "svelte";
  const dispatch = createEventDispatcher<{ openModal: boolean }>();

  let dialogContainer: HTMLElement;
  let dialog: A11yDialog | undefined;

  export let modalID: string;
  export let modalTitle = "";

  export let visible = false; //? Let parent handle visibility, don't set it anywhere in this component
  $: if (dialog) { visible ? dialog.show() : dialog.hide(); } //? Just hide and show based on parent's value of `visible`

  //* Style CSS
  export let closeable = false;
  export let modalContentClasses = "";
  export let modalHeaderClasses = "";
  export let modalBodyClasses = "";

  onMount(() => {
    dialog = new A11yDialog(dialogContainer);

    dialog.on("show", () => { //? Since Svelte can't add classes to <body> via <svelte:body class:someClass={conditional} />
      document.documentElement.style.overflowY = "hidden"; //? SO just use vanilla JS to prevent scrolling while modal is open
    }).on("hide", () => { //* Handle closing whenever focus is lost
      document.documentElement.style.overflowY = "";
      dispatch("openModal", false); //? Let parent control the visibility
    });

    return () => { dialog?.destroy(); };
  });
</script>

<div bind:this={dialogContainer} id={modalID} aria-labelledby="{modalID}Label" aria-hidden={visible ? "false" : "true"} class="dialog-container">
  <!-- The overlay is a dark surface that floats above the normal page. The modal floats above the overlay, and is hidden when the overlay is clicked -->
  <div data-a11y-dialog-hide class="dialog-overlay" />
  <div role="document" class={`dialog-content modal-dialog ${modalContentClasses}`.trim()}>
    <div class={`modal-header ${modalHeaderClasses}`.trim()}>
      {#if modalTitle !== "" || $$slots.title}
        <slot name="title"> <!-- Span works well as a slot parent component here -->
          <h5 class="modal-title" id="{modalID}Label">{modalTitle}</h5>
        </slot>
      {/if}
      {#if closeable}
        <button class="btn-close" type="button" data-a11y-dialog-hide aria-label="Close dialog" on:click={() => dialog?.hide() } />
      {/if}
    </div>

    <div class={`modal-body ${modalBodyClasses}`.trim()}>
      <slot name="body" />
    </div>
  </div>
</div>

<style lang="less">
  @import "../CSS/variables";

  .dialog-container > .modal-dialog { //* Imitates `modal-lg` from Bootstrap since Svelte scoping overrides `modal-lg`
    @media @min576 {
      max-width: 100%;
    }
    @media @min700 {
      @media @max991 {
        margin-left: 1.25rem;
        margin-right: 1.25rem;
      }
    }
    @media @min992 {
      max-width: 800px;
    }
  }
  // Dialog Container AND overlay spread across the entire view
  .dialog-container, .dialog-overlay {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
  }

  .dialog-container {
    z-index: 2; // Dialog container + all descendants sit above all other elements
    display: flex; // Dialog container being flex makes centering easy
    justify-content: center;
  }

  .dialog-container[aria-hidden="true"] {
    display: none; // Dialog container + all descendants shouldn't be visible or focusable if hidden
  }

  .dialog-overlay {
    background-color: rgb(43 46 56 / 0.9); // Style the overlay with a dark slightly opaque background
  }

  .dialog-content {
    display: flex;
    flex-direction: column;
    width: 100%;
    margin: auto; // Vertical + horizontal centerings
    z-index: 2; // All dialog content should float above
    position: relative; // Ensures z-index works
    background-color: white;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 0.5rem;
  }
</style>