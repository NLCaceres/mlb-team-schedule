<script lang="ts">
  import CalendarDayDetail from "./CalendarDayDetail.svelte";
  import Image from "../Common/Image.svelte";
  import { getTimeFromDateStr } from "../HelperFuncs/DateExtension";
  import type BaseballGame from "../Models/DataClasses";
  import { MONTH_MAP } from "../Models/Month";
  import { navigate } from "svelte-navigator";
  import { createEventDispatcher } from "svelte";
  const dispatch = createEventDispatcher<{ clickCalendarDay: BaseballGame | string }>();

  //* Normal Props
  export let currentMonth: string;
  export let dayNum: string; //* Day N of this month, i.e. 1 to 31
  export let games: BaseballGame[] = [];
  //* Css Related Props
  export let even = true; //* Helps create contrast in colors
  export let mini = false;
  export let cssClasses = "";

  $: innerWidth = window.innerWidth;
  $: smallScreen = innerWidth < 576;
  $: largeCalendarView = !smallScreen && !mini; //* When in a tablet or greater view + not in the multicalendar month page == true

  function handleClick() { //* Nav to DetailView on mobile, Else bubble up the click event
    if (smallScreen) { navigate(`${currentMonth}/${dayNum}`); }
    else {
      const monthNum = MONTH_MAP[currentMonth.slice(0,1).toUpperCase() + currentMonth.slice(1)];
      dispatch("clickCalendarDay", (games.length > 0) ? games[0] : `${monthNum}/${dayNum}`);
    }
  }
/* Good Example of Svelte Reactivity - common pattern: handle complex computed props with a reactive block
  $: { //* When DRYing code, note Svelte can't react to vars in or changed by an external func, of course!
    const dimensions = (smallScreen || mini) ? '15' : (bigScreen) ? '45' : '30' //* Since img is square, can set to both height/width
    //* BUT svelte CAN react to the above dimensions init, and we can pass 'dimensions' to our DRY fn, making non reactive props reactive!
    awayLogoSvg = createSvgElem(awayLogo, dimensions);
  } */
</script>

<svelte:window bind:innerWidth />

<td class={`standard-detail ${cssClasses}`} class:different-month={dayNum === ""} class:even class:odd={!even}>
  <!--todo Divs aren't clickable so the following causes an a11y issue, so need to convert this div into a button -->
  <div class="fs-6 justify-content-between d-flex" class:flex-column={largeCalendarView || games.length === 0} on:click={handleClick}>
    {#if dayNum.length > 0}
      <!--* Calendar Days always need the numbered day of the week (1-31) -->
      <div class={(largeCalendarView) ? "d-flex justify-content-between" : ""}>
        <p class="calendar-text text-decoration-underline me-2" class:text-dodger-blue={even} class:text-white={!even} class:mini>
          {dayNum}
        </p>
        <!--* If game happening, give the time -->
        {#if games.length > 0}
          <p class="game-time link-shadow {(largeCalendarView) ? "fs-5 text-end lh-1 mt-1" : ""}">
            {getTimeFromDateStr(games[0].date)}
          </p>
        {/if}
      </div>

      <!--* Main Game + Promo Section -->
      {#if games.length > 0 && !smallScreen}
        <CalendarDayDetail game={games[0]} {mini} {even} />

      {:else if games.length > 0}
        <div class="d-flex justify-content-evenly align-items-center link-shadow mt-2 text-decoration-underline" class:flex-column={mini}>
          <Image source={games[0].awayTeam.teamLogo} altText="{games[0].awayTeam.abbreviation} Logo" miniView={mini} />
          vs
          <Image source={games[0].homeTeam.teamLogo} altText="{games[0].homeTeam.abbreviation} Logo" miniView={mini} />
        </div>
        <div class="link-shadow me-1"><sup>{games[0].promos.length > 0 ? "*" : ""}</sup></div>

      {:else if currentMonth === "march" && parseInt(dayNum) < 20 }
        <p class:mini class="calendar-text text-center lh-1">Spring Training!</p>

      {:else if currentMonth === "october" && parseInt(dayNum) > 30}
        <p class:mini class="calendar-text text-center lh-1">Season Over!</p>

      {:else if currentMonth === "october"}
        <p class:mini class="calendar-text text-center lh-1">Post Season!</p>

      {:else}
        <p class:mini class="calendar-text text-center lh-1">Off Day!</p>
      {/if}

    {:else}
      <!--* Just a colored-in empty space -->
    {/if}
  </div>
</td>

<style lang="less">
  @import "../CSS/variables";

  .standard-detail {
    @media @max575 {
      max-width: 25px; //* Prevents overly wide td elems
      height: 80px; //* Keeps equal table rows/tds in mobile view
    }
    @media @min576 {
      max-width: 40px; //* Only width setting needed to limit table at lower widths
      height: 190px; //* Only setting needed to create equal rows/td elements, while allowing some to stretch bigger to fit content
    }
    font-size: 1rem;
    font-weight: bolder;
    padding-top: 0;

    &:hover.even:not(.different-month) {
      background-color: darken(#ececec, 25%);
    }
    &:hover.odd:not(.different-month) {
      background-color: lighten(#0290f5, 20%);
    }

    &.mini { //* Following keeps table rows/tds equal in mini calendar
      @media @min576 {
        height: 100px;
      }
      @media @min992 {
        height: 131px; //* Oddly works
      }
    }
  }

  td>div {
    p.calendar-text {
      &.mini {
        font-size: 12px;
        @media @min576 { //* Only way to use 'and' as expected in an @media query
          @media @max991 {
            font-size: 14px;
          }
        }
        @media @min992 {
          font-size: 16px;
        }
      }
      font-size: 12px;
      @media @min576 { //* Only way to use 'and' as expected in an @media query
        @media @max991 {
          font-size: 20px;
        }
      }
      @media @min992 {
        font-size: 24px;
      }
    }
    p.game-time {
        font-size: 8px;
        @media @min576 { //* Only way to use 'and' as expected in an @media query
          @media @max991 {
            font-size: 10px;
          }
        }
        @media @min992 {
          font-size: 14px;
        }
      }
  }

  .even {
    .text-dodger-blue {
      color: @dodgerBlue;
    }
    .link-shadow {
      color: @dodgerBlue;
      text-shadow: 0px 1px 1px darkgoldenrod;
    }
  }

  .odd {
    .link-shadow {
      color: white;
      text-shadow: 0px 1px 1px darkgoldenrod;
    }
  }

  .different-month {
    &.even {
      background-color: darken(#ececec, 50%);
    }
    &.odd {
      background-color: darken(#0290f5, 20%);
    }
  }
</style>