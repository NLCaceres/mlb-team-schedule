<script lang="ts"> //todo May ultimately be replaceable with the new <dialog> elem, fixing the slot testing issue
export let modalID: string = "";
export let modalTitle: string = "";

//* Style CSS
export let closeable = false;
export let modalContentClasses = "";
export let modalHeaderClasses = "";
</script>

<div class="modal fade" id="{modalID}" tabindex="-1" aria-labelledby="{modalID}" aria-hidden="true" data-testid="modal">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content {modalContentClasses}">
      <div class="modal-header {modalHeaderClasses}">
        {#if modalTitle !== "" || $$slots.title}
          <slot name="title"> <!-- Span works well as a slot parent component here -->
            <h5 class="modal-title" id="{modalID}Label">{modalTitle}</h5>
          </slot>
        {/if}

        {#if closeable}
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        {/if}
      </div>
      <div class="modal-body">
        <slot name="body"></slot>
      </div>
    </div>
  </div>
</div>

<style lang="less">
  @import '../Less/variables';

  .modal-dialog { //* Imitates modal-lg from bootstrap (needed due to Svelte scoping overriding modal-lg)
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
</style>