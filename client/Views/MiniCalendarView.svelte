<script lang='ts'>
  import type { Month } from "../Models/Month";
  import { link } from 'svelte-navigator';
  import Calendar from '../Calendar/Calendar.svelte';
  import { getFullSchedule } from "../api";
  import type BaseballGame from "../Models/DataClasses";
  import { createEventDispatcher } from 'svelte';
	const dispatch = createEventDispatcher();

  //* Normal props
  export let months: Month[];
  export let currentYear: string;

  $: innerWidth = window.innerWidth;
  $: smallScreen = innerWidth < 576;
  $: innerHeight = window.innerHeight;
  //* Following should handle most tablets since they're usually taller than wide, unlike laptops
  $: tabletScreen = innerWidth <= 1024 && innerHeight > innerWidth + 100; 

  async function splitGames() {
    let loadedGames = await getFullSchedule();
    if (loadedGames) {
      const gamesSplitByMonth: BaseballGame[][] = [[],[],[],[],[]];
      let gamesIndex = 0;
      for (let i = 0; i < gamesSplitByMonth.length; i++) {
        let currentMonthName = months[i].monthName;
        // console.log(`Beginning Following Month: ${currentMonthName}`);
        for (let j = gamesIndex; j < loadedGames.length; j++) {
          const loadedGame = loadedGames[j];
          const monthName = loadedGame.date.split(' ')[1]; //* Format: 'Weekday Month...'
          // console.log(`LoadedGameMonthName: ${monthName} vs MonthSelectingFor: ${currentMonthName}`)
          if (monthName === currentMonthName) {
            // console.log("Matched months! Adding game");
            gamesSplitByMonth[i].push(loadedGame);
          } else {
            // console.log(`Done Processing ${currentMonthName}`);
            gamesIndex = j; //* So next for loop in next iteration of i, starts at this index
            break;
          }
        }
      }
      return gamesSplitByMonth;
    }
    return undefined;
  }
  const dividedGamesList = splitGames();

  const currentDate = new Date();
  const currentMonth = currentDate.toLocaleString('default', { month: 'long'}).toLowerCase();
  const currentDay = currentDate.toLocaleString('default', { day: 'numeric'});

  async function propagateModalOpening(event: Event) { 
    const dividedGames = await splitGames();
    if (dividedGames) {
      const monthIndex = currentDate.getMonth() - 5 //* Since starting at June, offset is 5 (6th month of year zero-indexed)
      const foundMonth = dividedGames[monthIndex];
      const foundGame = foundMonth.find(game => parseInt(game.date.split(' ')[2]) === parseInt(currentDay));
      if (!foundGame) dispatch('openAlert', true); //* If offday, open alert to say so!
      else dispatch('openModal', foundGame);
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
          <a use:link href="{currentMonth}/{currentDay}" class="btn">Today's Game is:</a>
        {:else}
          <button type='button' class="btn ms-lg-5" on:click={propagateModalOpening}>Today's Game is:</button>
        {/if}
    </div>

    <div class="d-flex flex-wrap w-100 justify-content-center">
      {#each months as month, i (month.monthName)}
        <Calendar tableClass={`mx-2`} calendarMonth={month} mini gamesList={gamesByMonth[i]} on:openModal/>
      {/each}
    </div>
  {:else}
    <h1>Sorry! Seems we hit a snag!</h1>
  {/if}
{/await}

<style lang="less">
  @import '../Utility/Less/variables';

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