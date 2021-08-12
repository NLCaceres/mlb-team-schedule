<script lang="ts">
export let source: string | null; //* Src string
export let altText: string; //* Text to display if not able to load img;
export let height: number = 0;; //* Overrides
export let width: number = 0;

$: heightStyle = (height !== 0) ? `height:${height}px !important;` : '';
$: widthStyle = (width !== 0) ? `width:${width}px !important;` : '';

//* Css Props
export let miniView = false;
export let placeholderStyleString = '';
let isLoaded = true;

</script>

{#if isLoaded || source && source !== 'undefined'}
  <!-- Loading src with 'error' will cause error on img tag and result in displaying else div as backup-->
  <img src="{source ?? 'error'}" alt="{altText}" on:error={event => isLoaded = false} class:miniView 
    style="{heightStyle}{widthStyle}">
{:else}
  <div class="placeholder-img" style="{placeholderStyleString}">
    Missing {altText}
  </div>
{/if}

<style lang="less">
  @import '../Less/variables';
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
