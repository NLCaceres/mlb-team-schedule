<script lang="ts">
import QuestionMark from "./QuestionMark.svelte";

let hovering = false;
$: hintVisibility = (hovering) ? "d-block" : "d-none";
const updateVisibility = (isHovered: boolean) => { hovering = isHovered }
export let placement: "top-placed" | "right-placed" = "right-placed";
</script>

<!--? Screen Readers usually append "Button" when reading a button. In the case of this default button slot, "Question Mark Icon BUTTON" gets read -->
<div class="app-tooltip-container {placement}" on:mouseenter={() => updateVisibility(true)}
  on:focus={() => updateVisibility(true)} on:mouseleave={() => updateVisibility(false)}>
    <button type="button" class="app-tooltip-button">
      <slot name="button-icon">
        <QuestionMark width={20} height={20} outlineColor="black" fillColor="black" />
      </slot>
    </button>
    <p class="{hintVisibility} app-tooltip-hint">
      <slot name="hint">
        <!--? Can use <svelte:fragment> to wrap elements and fill this slot -->
      </slot>
    </p>
</div>

<style lang="less">
@import "../CSS/variables";

.app-tooltip-container {
  display: inline-block;
  position: relative;
}

.app-tooltip-button {
  background-color: transparent;
  border-color: transparent;
  color: black;
}

// COULD use the `.app-tooltip-button::before` pseudoElement to render a hint BUT probably not very accessible since
// it seems unpredictable whether screen readers will actually find the text

.app-tooltip-container::after {
  content: "";
  position: absolute;
  // Render an arrow after the button and before the hint using ONE corner of a square elem to form a triangle to the center point
  // Only seems to work with ::before/::after pseudo tags though (normal elements make trapezoids)
  border: 12px solid #000;
  display: none;
}
// Render the arrow when the user hovers over any part of the container to match the visibility of the hint itself
.app-tooltip-container:hover::after {
  display: block;
}
.app-tooltip-container.right-placed::after {
  left: 100%;
  margin-left: -0.85rem;
  top: 53%;
  transform: translateY(-50%);
  border-color: transparent black transparent transparent;
}
.app-tooltip-container.top-placed::after {
  position: absolute;
  left: 15%;
  top: 0%;
  transform: translateY(-30%);
  border-color: black transparent transparent transparent;
}

.app-tooltip-hint {
  position: absolute;
  // Better to set max/min-width and let the text create the sizing
  max-width: 40vw;
  min-width: 150px;
  padding: 5px 2px;
  border-radius: 10px;
  background: #000000;
  // `white-space` and `overflow-wrap: break-word` can also be useful for getting the correct size and shape of text boxes
  // `text-wrap: balanced` may also be a game-changer in the future if it isn't too inefficient when finalized
  font-size: 0.80rem;
  color: #FFFFFF;
  text-align: center;

  @media @max575 {
    max-width: 40vw;
  }
}

.right-placed > .app-tooltip-hint {
  top: 50%;
  transform: translateY(-50%);
  left: 100%;
  margin-left: 10px;
}

.top-placed > .app-tooltip-hint {
  top: 0%;
  transform: translate(-50%, -100%);
  left: -100%;
  margin-left: 5px;
  margin-top: -5px;
}

</style>
