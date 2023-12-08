<script lang="ts">
  export let source = ""; //* Src string
  export let altText = ""; //* Text to display if not able to load img
  let hasError = false;

  export let height = 0; //* Overrides the dimensions
  $: heightStyle = (height !== 0) ? `height:${height}px !important;` : "";
  export let width = 0;
  $: widthStyle = (width !== 0) ? `width:${width}px !important;` : "";

  //* Css Props
  export let miniView = false;
  export let placeholderStyleString = "";
</script>

{#if hasError || source === "" || source === "undefined"}
  <div class="placeholder-img" style={placeholderStyleString}>
    Missing {altText}
  </div>
{:else}
  <img src={source} alt={altText} on:error={() => hasError = true} class:miniView style="{heightStyle} {widthStyle}" />
{/if}

<style lang="less">
  @import "../CSS/variables";
  img {
    &.miniView {
      @media @max575 {
        height: 20px;
        width: 20px;
      }
      @media @min576 { //* Only way to use 'and' as expected in an @media query
        @media @max991 {
          width: 20px;
          height: 25px;
        }
      }
      @media @min992 {
        width: 27px;
        height: 35px;
      }
    }

    @media @max575 {
      height: 20px;
      width: 20px;
    }
    @media @min576 { //* Only way to use 'and' as expected in an @media query
      @media @max991 {
        width: 40px;
        height: 25px;
      }
    }
    @media @min992 {
      width: 55px;
      height: 35px;
    }
  }
  .placeholder-img {
    color: #8c8c8c;
    background-color: #a6a6a6a6;
    max-width: min-content;
    display: inline-flex;
    line-height: 1.1;
    padding: 2px;
    text-align: center;
    text-shadow: 0px 1px 1px white;
  }
</style>
