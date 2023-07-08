<script lang="ts">
  import { getSingleGame } from '../api';
  import Image from "../Utility/Components/Image.svelte";
  import type BaseballGame from '../Models/DataClasses';
  import getReadableDate from "../HelperFuncs/DateExtension";

  export let day: number;
  export let monthName: string;

  //? Async functions always return a promise, so we deal with it in the template! Rather than here
  let todaysGame: Promise<BaseballGame | undefined> = getSingleGame(monthName, ''+day); //* Bit faster than .toString num to str conversion
    
  const gameNumStr = (todaysGame: BaseballGame) => {
    if (todaysGame === null) return ''; //* Likely to never be null since null objects shouldn't cause modal event to open
    let gameStr = '';
    if (todaysGame.gameNumInSeries === 1) gameStr = `The First Game`
    else if (todaysGame.gameNumInSeries === todaysGame.gamesInSeries) gameStr = `The Last Game`
    else gameStr = `Game #${todaysGame.gameNumInSeries}`
    return gameStr + ` in a ${todaysGame.gamesInSeries}-day Series`
  }
</script>

<div class='mx-3 main-title'>
  {#await todaysGame}
    <h1>Loading up today's matchup!</h1>
  {:then currentGame} 
    {#if currentGame}
      <h1 class="text-decoration-underline">{getReadableDate(currentGame.date)}'s Matchup:</h1>
      <h3 class='text-center'>
        The <Image source="{currentGame.awayTeam.teamLogo}" altText="{currentGame.awayTeam.abbreviation} Logo"/>
        {currentGame.awayTeam.cityName} {currentGame.awayTeam.teamName} <sup>({currentGame.awayTeam.wins} - {currentGame.awayTeam.losses})</sup> 
      </h3>
      <h3 class='text-center'>vs</h3>
      <h3 class='text-center'>
        The <Image source="{currentGame.homeTeam.teamLogo}" altText="{currentGame.homeTeam.abbreviation} Logo"/>
        {currentGame.homeTeam.cityName} {currentGame.homeTeam.teamName} <sup>({currentGame.homeTeam.wins} - {currentGame.homeTeam.losses})</sup> 
      </h3>
      <h5 class='text-center'>{gameNumStr(currentGame)}</h5>

      <hr class="mt-1 mb-4">
      
      <div class='ms-3 me-4 subtitle'>
        {#if currentGame.promos.length > 0}
          <h3 class='text-decoration-underline'>Promotions for Today</h3>
          <ul>
            {#each currentGame.promos as promo (promo.id)}
              <li>
                {promo.name}
                <Image source="{promo.thumbnailUrl}" altText="{promo.name} thumbnail" height={100} width={100}/>
              </li>
            {/each}
          </ul>
        {:else if currentGame.homeTeam.teamName === "Dodgers"}
          <h3>Sorry no Dodgers Promos today!</h3>
        {:else}
          <h3>Sorry! The Dodgers are away, so no promos today!</h3>
        {/if}
      </div>
    {:else}
      <h1>Just a Dodger's Day off!</h1>
    {/if}
  {/await}
</div>

<style lang="less">
  .main-title {
    color: lighten(#004680, 12%);
  }
  .subtitle {
    color: lighten(#004680, 20%);
  }
</style>