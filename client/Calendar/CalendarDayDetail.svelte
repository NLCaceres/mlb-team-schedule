<script lang="ts">
  import type BaseballGame from "../Models/DataClasses";
  import Image from "../Common/Image.svelte";

  $: innerWidth = window.innerWidth;
  $: smallScreen = innerWidth < 576;
  $: tabletScreen = innerWidth <= 768;

  export let game: BaseballGame | null;
  export let mini: boolean = false;
  export let even: boolean = true;

</script>

<svelte:window bind:innerWidth />

<div class:even class:odd={!even} class="{(mini) ? 'd-flex' : ''}">
  <div class='d-flex justify-content-evenly align-items-center link-shadow mt-2 mb-4 {(smallScreen || mini) ? 'flex-column' : ''} {(!mini) ? 'me-1':''}'>
      <Image source="{game?.awayTeam.teamLogo ?? ""}" altText="{game?.awayTeam.abbreviation} Logo" miniView="{mini}"/>
      vs 
      <Image source="{game?.homeTeam.teamLogo ?? ""}" altText="{game?.homeTeam.abbreviation} Logo" miniView="{mini}"/>
  </div>
  <div class='link-shadow {(!mini) ? 'mt-3': ''}'>
    {#if !mini && game?.promos && game?.promos.length > 0}
      <h6>* Promos</h6>
      <ul class="promo-list">
        {#each game?.promos as promo (promo.id)}
          <li>
            <Image source="{promo.thumbnailUrl}" altText="{promo.name} Thumbnail" miniView={mini}
              placeholderStyleString="margin-bottom:7px;{(!even)? 'color:#fff;background-color:#000;' :''}
              {(tabletScreen) ? 'font-size:10px;' : 'font-size:14px'}"/>
              <!--Using font-size since Bootstrap 'fs' utility class is still too big! -->
          </li>
        {/each}
      </ul>
    {:else if mini && game?.promos && game?.promos.length > 0}
      <sup>{(game && game?.promos.length > 0) ? '*' : ''}</sup>

    {:else if !mini && game?.promos && game?.promos.length === 0}
      {#if game?.homeTeam.teamName === 'Dodgers'}
        <h6>Sorry! No Dodgers promos today!</h6>
      {:else}
        <h6>Sorry! The Dodgers away, No promos today!</h6>
      {/if}
    {/if}
  </div>
</div>

<style lang="less">
  @import '../CSS/variables';

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