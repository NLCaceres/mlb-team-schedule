<script lang="ts">
  import type BaseballGame from "./Models/DataClasses";
  import Modal from "./Common/Modal.svelte";
  import Image from "./Common/Image.svelte";
  import getReadableDate from './HelperFuncs/DateExtension';

  export let modalID: string;
  export let game: BaseballGame | null;

  const gameNumStr = (todaysGame: BaseballGame | null) => {
    if (todaysGame === null) return ''; //* Likely to never be null since null objects shouldn't cause modal event to open
    let gameStr = '';
    if (todaysGame.seriesGameNumber === 1) gameStr = `The First Game`
    else if (todaysGame.seriesGameNumber === todaysGame.seriesGameCount) gameStr = `The Last Game`
    else gameStr = `Game #${todaysGame.seriesGameNumber}`
    return gameStr + ` in a ${todaysGame.seriesGameCount}-day Series`
  }
</script>

<Modal modalID="{modalID}" modalContentClasses="custom-content" modalHeaderClasses="dodger-low-border"> 
  <span slot="title" class="main-title w-100">
    <div class='d-flex justify-content-between'>
      <h2 class="game-day text-decoration-underline">{getReadableDate(game?.date ?? '')}'s Matchup: </h2>
      <p class='game-day text-end'>{gameNumStr(game)}</p>
    </div>
    <h4>
      The <Image source="{game?.awayTeam.teamLogo ?? ""}" altText="{game?.awayTeam.abbreviation} Logo"/>
      {game?.awayTeam.cityName} {game?.awayTeam.teamName} <sup>({game?.awayTeam.wins} - {game?.awayTeam.losses})</sup>
    </h4>
    <h6>vs</h6>
    <h4>
      The <Image source="{game?.homeTeam.teamLogo ?? ""}" altText="{game?.homeTeam.abbreviation} Logo"/>
      {game?.homeTeam.cityName} {game?.homeTeam.teamName} <sup>({game?.homeTeam.wins} - {game?.homeTeam.losses})</sup>
    </h4>
  </span>
  <div slot="body" class="subtitle">
    {#if game && game.promos.length > 0}
      <h4 class='text-decoration-underline'>Promo List!</h4>
      <ul>
        {#each game?.promos ?? [] as promo (promo.id)}
          <li>
            {promo.name}
            <Image source="{promo.thumbnailUrl}" altText="{promo.name} Thumbnail" 
              placeholderStyleString="display:inline;" height={100} width={75}/>
          </li>
        {/each}
      </ul>
    {:else if game && game.homeTeam.teamName === 'Dodgers'}
      <h2>Sorry! No Dodgers Promos tonight!</h2>
    {:else}
      <h2>Sorry! The Dodgers are away, so no promos today!</h2>
    {/if}
  </div>
</Modal>  

<style lang="less">
  @import './CSS/variables';

  //* Using :global tells svelte to unscope and expand what this component's CSS can affect
  :global(.modal-content.custom-content) { //* Bootstrap will normally override so the !important is necessary
    background-color: lighten(@bodyColor, 10%);
    border: 3px solid #012e70 !important;
  }
  :global(.modal-header.dodger-low-border) {
    border-bottom: 1.5px solid @dodgerBlue;
  }
  
  .main-title {
    color: lighten(#004680, 5%);
  }
  .subtitle {
    color: lighten(#004680, 20%);
  }
  h2.game-day {
    flex-grow: 4;
    flex-shrink: 0; //* Keeps it at a 4:1 ratio with the paragraph superscript
  }
  p.game-day {
    line-height: 0.9;
    flex-grow: 1;
    // margin: -0.75em -0.75em 0 1em;
    margin: -0.6em -0.7em 0 1em; //* Thanks to BS text-end, margins much simpler!
    font-size: 2.5vw; //* Handles lower viewport widths (since vw = 1% of viewport width, greater vw needed)
    @media @min850 {
      // margin: -0.5em -0.8em 0 1em;
      font-size: 1.75vw;
    }
    @media @min1440 { //* WHEREAS at high viewport width need lower vw or risk massive font
      // margin: -0.5em -0.5em 0 1em;
      font-size: 1vw;
    }
  }
</style>