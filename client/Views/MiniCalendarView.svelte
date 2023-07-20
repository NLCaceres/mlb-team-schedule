<script lang='ts'>
  import Calendar from '../Calendar/Calendar.svelte';
  import { link } from 'svelte-navigator';
  import type BaseballGame from "../Models/DataClasses";
  import { MONTH_NUM_MAP } from '../Models/Month';
  import { getFullSchedule } from "../API";
  import { getDayFromDateStr, getMonthFromDateStr, todaysSplitDate } from '../HelperFuncs/DateExtension';
  import { createEventDispatcher } from 'svelte';
	const dispatch = createEventDispatcher();

  //* Normal props
  export let months: string[]; //* Expected months of the season
  export let currentYear: string;

  $: innerWidth = window.innerWidth;
  $: smallScreen = innerWidth < 576;
  $: innerHeight = window.innerHeight;
  $: tabletScreen = innerWidth <= 1024 && innerHeight > innerWidth + 100; //* Since tablets are tall, but not wide, this excludes laptops

  async function splitGames() {
    let loadedGames = await getFullSchedule();
    if (loadedGames === undefined) { return undefined }
    //? Can't use Array(length).fill([]) since it fills each spot with the same array ref, so each change affects the other
    const gamesSplitByMonth: BaseballGame[][] = Array.from({ length: months.length }, _ => []);
    let gamesIndex = 0;
    for (let i = 0; i < gamesSplitByMonth.length; i++) { //todo May be able to condense these loops into single "while" loop
      for (let j = gamesIndex; j < loadedGames.length; j++) {
        const monthName = getMonthFromDateStr(loadedGames[j].date);
        if (monthName !== months[i]) {
          gamesIndex = j; //* In next iteration of the "i" for-loop start the j-loop at gamesIndex of loadedGames
          break;
        }
        gamesSplitByMonth[i].push(loadedGames[j]);
      }
    }
    return gamesSplitByMonth;
  }
  const dividedGamesList = splitGames();

  const [_, currentMonth, currentDay] = todaysSplitDate();

  async function propagateModalOpening(event: Event) { 
    const dividedGames = await splitGames();
    if (dividedGames) {
      const monthIndex = parseInt(currentMonth) - 3; //* Since starting season starts in March, offset is 3
      const foundMonth = dividedGames[monthIndex];
      const foundGame = foundMonth.find(game => parseInt(getDayFromDateStr(game.date)) === parseInt(currentDay));
      if (!foundGame) { dispatch('openAlert', true) } //* If offday, open alert to say so!
      else { dispatch('openModal', foundGame) }
    }
  }
</script>

<svelte:window bind:innerWidth bind:innerHeight />

<h3 class='subtitle text-center mb-2'>
  Below you'll find a full list of the Dodgers Promo schedule {currentYear}.
  {tabletScreen ? 'Tapping' : 'Clicking'} the date will show you the details!
</h3>

<p class='subtitle text-center mb-0'>* indicates promo days at Dodger Stadium</p>

{#await dividedGamesList}
  <h1>Loading up this month's games!</h1>
{:then gamesByMonth} 
  {#if gamesByMonth}
    <div class="container mt-2">
        {#if smallScreen}
          <a use:link href="{MONTH_NUM_MAP[parseInt(currentMonth)]}/{currentDay}" class="btn">Today's Game is:</a>
        {:else}
          <button type='button' class="btn ms-lg-5" on:click={propagateModalOpening}>Today's Game is:</button>
        {/if}
    </div>

    <div class="d-flex flex-wrap w-100 justify-content-center">
      {#each months as month, i (month)}
        <Calendar mini tableClass={`mx-2`} monthName={month} gamesList={gamesByMonth[i]} on:openModal />
      {/each}
    </div>
  {:else}
    <h1>Sorry! Seems we hit a snag!</h1>
  {/if}
{/await}

<style lang="less">
  @import '../CSS/variables';

  .subtitle {
    color: #004680;
    @media @max575 {
			margin-left: 2rem;
			margin-right: 2rem;
		}
		@media @min576 {
			margin-left: 4rem;
			margin-right: 4rem;
		}
  }

  button.btn {
    @media @min576 {
      @media @max768 {
        margin-left: 6rem;
      }
    }
  }

  .btn {
    background-color: lighten(@dodgerBlue, 5%);
    color: white;
    font-size: 18px;
    &:hover {
      text-decoration: underline;
      color:white;
      text-shadow: 0px 1px 1px darkgoldenrod;
    }
  }

</style>