<script lang="ts">
  import Calendar from "../Calendar/Calendar.svelte";
  import SubtitleWithTooltip from "./SubtitleWithTooltip.svelte";
  import { getMonthsGames } from "../API";
  import type BaseballGame from "../Models/DataClasses";
  import { useLocation } from "svelte-routing";

  const location = useLocation(); //? Ex: Grab "/april" and ONLY take "april"
  $: month = $location.pathname.slice(1, 2).toUpperCase() + $location.pathname.slice(2);
  export let currentYear: string;

  //? This pattern is useful for ensuring the async HTTP request is called ONLY ONCE!
  async function getThisMonthsGames(thisMonth: string) {
    monthsGames = await getMonthsGames(thisMonth) ?? [];
  }
  $: fetcher = getThisMonthsGames(month); //? Using `month` as a param seems to keep `$location.pathname` from being read as `undefined` in the async func
  let monthsGames: BaseballGame[] = [];

  $: innerWidth = window.innerWidth;
</script>

<svelte:window bind:innerWidth />

<SubtitleWithTooltip subtitle="{month} {currentYear} Games" />

{#await fetcher}
  <h1>Loading up this month's games!</h1>
{:then}
  {#if monthsGames.length > 0}
    <Calendar monthName={month} mini={innerWidth < 576} gamesList={monthsGames} on:clickCalendarDay />
  {:else}
    <h1>Sorry! Seems we hit a snag!</h1>
  {/if}
{/await}
