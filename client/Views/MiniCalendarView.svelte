<script lang="ts">
  import Calendar from "../Calendar/Calendar.svelte";
  import SubtitleWithTooltip from "./SubtitleWithTooltip.svelte";
  import { link } from "svelte-navigator";
  import type BaseballGame from "../Models/DataClasses";
  import { MONTH_NUM_MAP } from "../Models/Month";
  import { getFullSchedule } from "../API";
  import { getDayFromDateStr, getMonthFromDateStr, todaysSplitDate } from "../HelperFuncs/DateExtension";
  import { createEventDispatcher } from "svelte";
	const dispatch = createEventDispatcher();

  //* Normal props
  export let months: string[]; //* Expected months of the season

  $: innerWidth = window.innerWidth;
  $: smallScreen = innerWidth < 576;
  $: innerHeight = window.innerHeight;
  $: tabletScreen = innerWidth <= 1024 && innerHeight > innerWidth + 100; //* Since tablets are tall, but not wide, this excludes laptops

  async function splitGames() {
    let loadedGames = await getFullSchedule();

    //? Still returning undefined keeps render conditional as a super simple "if true, then calendar; else error msg"
    if (loadedGames === undefined || loadedGames.length === 0) { return undefined }

    //? Can't use Array(length).fill([]) since it fills each spot with the same array ref, so each change affects the other
    const gamesSplitByMonth: BaseballGame[][] = Array.from({ length: months.length }, _ => []);
    let gamesIndex = 0;
    for (let i = 0; i < gamesSplitByMonth.length; i++) { //TODO: May be able to condense these loops into single "while" loop
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

  //TODO: Instead of this next func, let the parent view pass in its own click handler to fill a clickHandler prop in this component?
  async function propagateModalOpening(event: Event) { 
    const dividedGames = await splitGames();
    if (dividedGames) {
      const monthIndex = parseInt(currentMonth) - 3; //* Since starting season starts in March, offset is 3
      const foundMonth = dividedGames[monthIndex];
      const foundGame = foundMonth?.find(game => parseInt(getDayFromDateStr(game.date)) === parseInt(currentDay));
      if (!foundGame) { dispatch("openAlert", true) } //* If off-day or off-season, open alert to say so!
      else { dispatch("openModal", foundGame) }
    }
  }
</script>

<svelte:window bind:innerWidth bind:innerHeight />

<SubtitleWithTooltip subtitle={`${tabletScreen ? "Tap" : "Click"} the date to show game specifics`} />

{#await dividedGamesList}
  <h1>Loading up this month's games!</h1>
{:then gamesByMonth} 
  {#if gamesByMonth}
    <div class="container mt-2">
        {#if smallScreen}
          <a use:link href="{MONTH_NUM_MAP[parseInt(currentMonth)]}/{currentDay}" class="btn">Today's Game is:</a>
        {:else}
          <button type="button" class="btn ms-lg-5" on:click={propagateModalOpening}>Today's Game is:</button>
        {/if}
    </div>

    <div class="d-flex flex-wrap w-100 justify-content-center">
      {#each months as month, i (month)}
        <Calendar mini tableClass="mx-2" monthName={month} gamesList={gamesByMonth[i]} on:openModal />
      {/each}
    </div>
  {:else}
    <h1>Sorry! Seems we hit a snag!</h1>
  {/if}
{/await}

<style lang="less">
  @import "../CSS/variables";

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
