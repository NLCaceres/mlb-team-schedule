<script lang='ts'>
  import type BaseballGame from '../Models/DataClasses';
  import { getTimeFromDateStr } from '../HelperFuncs/DateExtension';
  import { link } from 'svelte-navigator';
  import { createEventDispatcher } from 'svelte';
	const dispatch = createEventDispatcher();

  import Image from '../Utility/Components/Image.svelte';
  import CalendarDayDetail from './CalendarDayDetail.svelte';

  //* Normal Props
  export let mini: boolean = false;
  export let currentMonth: string;
  export let dayOfWeek: string = '';
  export let game: BaseballGame | null;

  //* Css Related Props
  export let even: boolean; //* 
  export let cssClasses: string = '';

  $: innerWidth = window.innerWidth;
  $: smallScreen = innerWidth < 576;
  
  $: bigScreenSingleCalendar = !smallScreen && !mini; //* When in a tablet or greater view + not in the multicalendar month page == true

  /* Good Example of Svelte Reactivity - common pattern: handle complex computed props with a reactive block
  $: { //* When DRYing code, note Svelte can't react to vars in or changed by an external func, of course!
    const dimensions = (smallScreen || mini) ? '15' : (bigScreen) ? '45' : '30' //* Since img is square, can set to both height/width
    //* BUT svelte CAN react to the above dimensions init, and we can pass 'dimensions' to our DRY fn, making non reactive props reactive!
    awayLogoSvg = createSvgElem(awayLogo, dimensions); 
  } */
</script>

<svelte:window bind:innerWidth />

<!-- Bootstrap 5 does expose events to listen on modal opening/closing BUT -->
<td class={`standard-detail ${cssClasses}`} class:different-month={dayOfWeek === ''} class:even class:odd={!even} >
    <div class="fs-6 justify-content-between {(bigScreenSingleCalendar || !game) ? 'flex-column' : 'd-flex'}" on:click={e => dispatch('openModal', game)}>
      {#if dayOfWeek}
        <div class="{(bigScreenSingleCalendar) ? 'd-flex justify-content-between' : ''}">
          <p class="calendar-text text-decoration-underline {even ? 'text-dodger-blue' : 'text-white'} me-2" class:mini>
            {dayOfWeek}
          </p>
          {#if game}
            <p class="game-time link-shadow {(bigScreenSingleCalendar) ? 'fs-5 text-end lh-1 mt-1' : ''}">
              {getTimeFromDateStr(game.date)}
            </p>
          {/if}
        </div>
        {#if game && !smallScreen}
          <CalendarDayDetail game={game} mini={mini} even={even}/>

        {:else if game}
          <a use:link href="/{currentMonth}/{dayOfWeek}" class='d-flex justify-content-evenly 
            align-items-center link-shadow mt-2 {(smallScreen || mini) ? 'flex-column' : ''}'>
              <Image source="{game.awayTeam.teamLogo}" altText="{game.awayTeam.abbreviation} Logo" miniView="{mini}"/>
              vs 
              <Image source="{game.homeTeam.teamLogo}" altText="{game.homeTeam.abbreviation} Logo" miniView="{mini}"/>
          </a>
          <div class='link-shadow me-1'><sup>{game.promos.length > 0 ? '*' : ''}</sup></div>

        {:else if currentMonth === 'october' && parseInt(dayOfWeek) > 30}
          <p class:mini class='calendar-text text-center lh-1'>Season Over!</p>

        {:else if currentMonth === 'october'}
          <p class:mini class='calendar-text text-center lh-1'>Post Season!</p>
        {:else}
          <p class:mini class="calendar-text text-center lh-1">Off Day!</p>
        {/if}
      {/if}
    </div>
</td>

<style lang="less">
  @import '../Utility/Less/variables';

  .standard-detail {
    @media @max575 {
      max-width: 25px;
      min-width: 25px;
      width: 25px;
      min-height: 55px;
      height: 55px;
    }
    @media @min576 {
      max-width: 40px;
      min-width: 40px;
      width: 40px;
      min-height: 100px;
      height: 100px;
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