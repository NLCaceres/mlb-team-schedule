<script lang="ts">
  import { navigate } from "svelte-navigator";
  import Image from "../Common/Image.svelte";
  import type BaseballGame from '../Models/DataClasses';
  import { getSingleGame } from '../API';
  import getReadableDate from "../HelperFuncs/DateExtension";

  export let day: number;
  export let monthName: string;

  async function getTodaysGame() {
    todaysGame = await getSingleGame(monthName, ''+day).catch(err => { //? Simpler to append catch() in place of try/catch block
      navigate('/fullSchedule'); //? The catch() block implicitly returns SOMETHING
      return undefined; //? So must be explicit and add this return, or else navigate() causes `void` to be returned
    });
  }
  //? Async Funcs always return a promise, so save it in `fetcher`, so we can await it!
  $: fetcher = getTodaysGame() //? Letting this reactive statement mutate `todaysGame`
  var todaysGame: BaseballGame | undefined; //? AND keeping this prop's type simple! (No Promise wrapper!)

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
  {#await fetcher}
    <h1>Loading up today's matchup!</h1>
  {:then completed}
    {#if todaysGame}
      <h1 class="text-decoration-underline">{getReadableDate(todaysGame.date)}'s Matchup:</h1>
      <h3 class='text-center'>
        The <Image source="{todaysGame.awayTeam.teamLogo}" altText="{todaysGame.awayTeam.abbreviation} Logo"/>
        {todaysGame.awayTeam.cityName} {todaysGame.awayTeam.teamName} <sup>({todaysGame.awayTeam.wins} - {todaysGame.awayTeam.losses})</sup>
      </h3>
      <h3 class='text-center'>vs</h3>
      <h3 class='text-center'>
        The <Image source="{todaysGame.homeTeam.teamLogo}" altText="{todaysGame.homeTeam.abbreviation} Logo"/>
        {todaysGame.homeTeam.cityName} {todaysGame.homeTeam.teamName} <sup>({todaysGame.homeTeam.wins} - {todaysGame.homeTeam.losses})</sup>
      </h3>
      <h5 class='text-center'>{gameNumStr(todaysGame)}</h5>

      <hr class="mt-1 mb-4">
      
      <div class='ms-3 me-4 subtitle'>
        {#if todaysGame.promos.length > 0}
          <h3 class='text-decoration-underline'>Promotions for Today</h3>
          <ul>
            {#each todaysGame.promos as promo (promo.id)}
              <li>
                {promo.name}
                <Image source="{promo.thumbnailUrl}" altText="{promo.name} thumbnail" height={100} width={100} />
              </li>
            {/each}
          </ul>
        {:else if todaysGame.homeTeam.teamName === "Dodgers"}
          <h3>Sorry! No Dodgers Promos today!</h3>
        {:else}
          <h3>Sorry! The Dodgers are away, so no promos today!</h3>
        {/if}
      </div>
    {:else}
      <h1>Just a Dodgers Day off!</h1>
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