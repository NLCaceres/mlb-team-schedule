<script lang="ts">
  import Image from "../Common/Image.svelte";
  import type BaseballGame from "../Models/DataClasses";

  export let game: BaseballGame;
  export let even = true; //* Helps create contrast in colors
  export let mini = false;

  $: innerWidth = window.innerWidth;
  $: tabletScreen = innerWidth <= 768; //todo <Image> accepts CSS classes, so use instead of a style string
</script>

<svelte:window bind:innerWidth />

<div class:even class:odd={!even} class:d-flex={mini}>
  <div class="d-flex justify-content-evenly align-items-center link-shadow mt-2 mb-4" class:flex-column={mini} class:me-1={!mini}>
    <Image source={game.awayTeam.teamLogo} altText="{game.awayTeam.abbreviation} Logo" miniView={mini} />
    vs
    <Image source={game.homeTeam.teamLogo} altText="{game.homeTeam.abbreviation} Logo" miniView={mini} />
  </div>
  <div class="link-shadow" class:mt-3={!mini}>
    {#if game.promos.length > 0}
      {#if mini}
        <sup>*</sup>

      {:else}
        <h6>* Promos</h6>
        <ul class="promo-list">
          {#each game.promos as promo (promo.id)}
            <li>
              <Image source={promo.thumbnailUrl} altText="{promo.name} Thumbnail" miniView={mini}
                placeholderStyleString="margin-bottom:7px;{(!even) ? "color:#fff;background-color:#000;" : ""}
                  {(tabletScreen) ? "font-size:10px;" : "font-size:14px"}" />
            </li>
          {/each}
        </ul>
      {/if}

    {:else if !mini}
      {#if game.homeTeam.teamName === "Dodgers"}
        <h6>Sorry! No Dodgers promos today!</h6>
      {:else}
        <h6>Sorry! The Dodgers away, No promos today!</h6>
      {/if}

    {:else}
      <!--* Just a colored-in empty space -->
    {/if}
  </div>
</div>

<style lang="less">
  @import "../CSS/variables";

  .even > .link-shadow {
    color: @dodgerBlue;
    text-shadow: 0px 1px 1px darkgoldenrod;
  }

  .odd > .link-shadow {
    color: white;
    text-shadow: 0px 1px 1px darkgoldenrod;
  }
  .promo-list {
    padding-left: 1.5rem;
  }
</style>