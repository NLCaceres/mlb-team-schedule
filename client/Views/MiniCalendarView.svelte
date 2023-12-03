<script lang="ts">
  import Calendar from "../Calendar/Calendar.svelte";
  import SubtitleWithTooltip from "./SubtitleWithTooltip.svelte";
  import type BaseballGame from "../Models/DataClasses";
  import { getDayFromDateStr, getMonthFromDateStr, todaysSplitLocalDate } from "../HelperFuncs/DateExtension";
  import { MONTH_NUM_MAP } from "../Models/Month";
  import { getFullSchedule } from "../API";
  import { differenceInCalendarDays, isBefore } from "date-fns";
  import { link } from "svelte-routing";
  import { createEventDispatcher } from "svelte";
  const dispatch = createEventDispatcher<{ clickTodaysGame: BaseballGame, errorMessage: string }>();

  //* Normal props
  export let months: string[]; //* Expected months of the season

  $: innerWidth = window.innerWidth;
  $: smallScreen = innerWidth < 576;
  $: innerHeight = window.innerHeight;
  $: tabletScreen = innerWidth <= 1024 && innerHeight > innerWidth + 100; //* Since tablets are tall, but not wide, this excludes laptops

  async function splitGames() {
    let loadedGames = await getFullSchedule();

    if (loadedGames.length === 0) { return; }

    //? Can't use Array(length).fill([]) since it fills each spot with the same array ref, so each change affects the other
    const gamesSplitByMonth: BaseballGame[][] = Array.from({ length: months.length }, () => []);
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
    gamesByMonth = gamesSplitByMonth;
  }
  $: fetcher = splitGames();
  let gamesByMonth: BaseballGame[][] = [];

  const [currentYear, currentMonth, currentDay] = todaysSplitLocalDate();

  function clickTodaysGame() {
    if (gamesByMonth.length === 0) { return; }
    const normalMonthNum = parseInt(currentMonth);
    const monthIndex = normalMonthNum - 3; //* Since starting season starts in March, offset is 3
    const gamesOfTheMonth = gamesByMonth[monthIndex] ?? [];
    const foundGame = gamesOfTheMonth.find(game => parseInt(getDayFromDateStr(game.date)) === parseInt(currentDay));
    if (foundGame) { dispatch("clickTodaysGame", foundGame); }
    else { dispatch("errorMessage", checkTodaysDate(`${normalMonthNum}/${currentDay}`)); }
  }
  function checkTodaysDate(dateStr: string) {
    const [monthNum, dayNum] = dateStr.split("/"); //* Grab date vals from Slash-Split string: "MonthNum/DayNum"
    const expectedDate =  new Date(parseInt(currentYear), parseInt(monthNum) - 1, parseInt(dayNum));
    const daysUntilRegularSeason = differenceInCalendarDays(new Date(2024, 2, 20), expectedDate);
    const daysUntilSeasonMessage = `Only ${daysUntilRegularSeason} days until the ${expectedDate.getFullYear() + 1} Season officially begins!`;
    if (expectedDate.getMonth() === 1) { // TODO: Handle dynamic Spring Training game dates
      const springTrainingStart = new Date(2024, 1, 22); //? Spring Training starts February 22 2024
      return (isBefore(expectedDate, springTrainingStart)) ? "Spring Training is starting soon! Season's almost here!" :
        `Spring Training has begun! ${daysUntilSeasonMessage}`;
    }
    else if (expectedDate.getMonth() === 2) {
      const springTrainingEnd = new Date(2024, 2, 26); //? AND ends March 26 2024, BUT, oddly, with an International regular season game on March 20th...
      return (isBefore(expectedDate, springTrainingEnd)) ? `Spring Training has begun! ${daysUntilSeasonMessage}` : "The regular season has begun!";
    }
    else { return `Off-Season has begun! ${daysUntilSeasonMessage}`; }
  }
</script>

<svelte:window bind:innerWidth bind:innerHeight />

<SubtitleWithTooltip subtitle={`${tabletScreen ? "Tap" : "Click"} the date to show game specifics`} />

{#await fetcher}
  <h1>Loading up this month's games!</h1>
{:then}
  {#if gamesByMonth.length > 0}
    <div class="container mt-2">
      {#if smallScreen}
        <a use:link href="/{MONTH_NUM_MAP[parseInt(currentMonth)].toLowerCase()}/{currentDay}" class="btn">Today's Game is:</a>
      {:else}
        <button type="button" class="btn ms-lg-5" on:click={clickTodaysGame}>Today's Game is:</button>
      {/if}
    </div>

    <div class="d-flex flex-wrap w-100 justify-content-center">
      {#each months as month, i (month)}
        <Calendar mini tableClass="mx-2" monthName={month} gamesList={gamesByMonth[i]} on:clickCalendarDay />
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
