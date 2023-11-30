<script lang="ts">
  import Calendar from "../Calendar/Calendar.svelte";
  import SubtitleWithTooltip from "./SubtitleWithTooltip.svelte";
  import { getMonthsGames } from "../API";
  import { useLocation } from "svelte-navigator";

  //? As a bonus the following location is completely compatible with svelte-routing
  const location = useLocation(); //? Ex: Grab "/april" and ONLY take "april"
  $: month = $location.pathname.slice(1, 2).toUpperCase() + $location.pathname.slice(2);
  export let currentYear: string;

  //TODO: Optimize following since it gets called 3 times in a row
  $: loadingGames = getMonthsGames(month);
  $: innerWidth = window.innerWidth;
</script>

<svelte:window bind:innerWidth />

<SubtitleWithTooltip subtitle="{month} {currentYear} Games" />

{#await loadingGames}
  <h1>Loading up this month's games!</h1>
{:then fullGames}
  {#if fullGames}
    <Calendar monthName={month} mini={innerWidth < 576} gamesList={fullGames} on:clickCalendarDay />
  {:else}
    <h1>Sorry! Seems we hit a snag!</h1>
  {/if}
{/await}
