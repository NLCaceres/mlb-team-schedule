<script lang="ts">
  import Calendar from '../Calendar/Calendar.svelte';
	import { getMonthsGames } from "../API";
  import { useLocation } from "svelte-navigator";

  //? As a bonus the following location is completely compatible with svelte-routing
  const location = useLocation(); //? Ex: Grab "/april" and ONLY take "april"
  $: month = $location.pathname.slice(1, 2).toUpperCase() + $location.pathname.slice(2);
  export let currentYear: string;

	//todo Optimize following since it gets called 3 times in a row
	$: loadingGames = getMonthsGames(month);
  $: innerWidth = window.innerWidth;
</script>

<svelte:window bind:innerWidth />

<h3 class='subtitle text-center mb-2'>Below you'll find all the promos for the month of {month} {currentYear} </h3>

<p class='subtitle text-center mb-0'>* indicates promo days at Dodger Stadium</p>

{#await loadingGames}
  <h1>Loading up this month's games!</h1>
{:then fullGames}
  {#if fullGames}
		<Calendar monthName={month} mini={innerWidth < 576} gamesList={fullGames} on:openModal/>
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

</style>