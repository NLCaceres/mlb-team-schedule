<script lang="ts">
import Tooltip from "../Common/Tooltip.svelte";
import Asterisk from "../Common/Asterisk.svelte";

export let subtitle: string;

$: innerWidth = window.innerWidth;
</script>

<svelte:window bind:innerWidth />

<div class="title-container">
  <h2 class="subtitle text-center mb-0">{subtitle}</h2>
  <Tooltip placement={innerWidth > 991 ? "right-placed" : "top-placed"}>
    <svelte:fragment slot="hint">
      <Asterisk svgClasses="asterisk-icon" width={10} height={10} outlineColor="transparent" fillColor="white"/> indicates a home game with promotions
    </svelte:fragment>
  </Tooltip>
</div>

<style lang="less">
  @import "../CSS/variables";

  .title-container {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .subtitle {
    color: #004680;
    @media @max575 {
      max-width: 75vw;
    }
  }

  //? ClassName props generally don't work in Svelte, so :global() is used to unscope the CSS and apply it
  //? BUT :global() can pollute your CSS, resulting in unexpected styling, so can use parent or sibling selectors to restrict it
  .title-container :global(.asterisk-icon) {
    margin-left: -5px;
    margin-right: 2px;
    margin-bottom: 2px;
  }
  //? There are 2 other solutions:
  //? Using $$props.class to force in the scoped CSS
  //? CSS Custom properties -> `<Child --color="blue" />` so the component can grab the string and access it in CSS via var(--color)

</style>
