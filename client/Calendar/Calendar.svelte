<script lang='ts'>
import { beforeUpdate, onMount } from 'svelte';

  import type BaseballGame from '../Models/DataClasses';

  import type { Month } from '../Models/Month'; //? As of TS 3.8, this syntax is used to import ONLY the type (rather than the whole file)
  import { CreateRemainingMonth, CreateStartingWeek } from '../Utility/Functions/CreateCalendar';
  import CalendarDay from "./CalendarDay.svelte";
  
  //* Normal Props
  export let calendarMonth: Month;
  export let mini: boolean = false;
  
  export let gamesList: BaseballGame[];
  let offDays: number = 0; //* Tracks days without a game to calc game assignment
  beforeUpdate(() => {
    offDays = 0; //* Useful to prevent accessing negative indices
  })
  function grabGame(day: string): BaseballGame | null {
    if (day) {
      if (!gamesList || gamesList.length === 0) return null;
      const properCalendarDayNum = parseInt(day); //* Converts '01' -> 1 properly
      const nextIndex = properCalendarDayNum - (1 + offDays); //* Goal: Assign every game in list to a day!
      // console.log(`Next Index is ${nextIndex}`);
      const expectedGame = (nextIndex < gamesList.length) ? gamesList[nextIndex] : null;
      // console.log(expectedGame);
      if (expectedGame) {
        const gameDayNum = expectedGame.date.split(' ')[2]; //* Format: 'Weekday Month DayNum...'
        if (parseInt(gameDayNum) === properCalendarDayNum) { return expectedGame } 
        else { offDays++; return null; } //* No Games today so do best to keep gameList at same index
      }
    }
    // console.log("Not a day of this month");
    return null;
  }

  //* Css Props
  export let tableClass: string = ''; //* Allow default prop

  $: month = [CreateStartingWeek(calendarMonth), ...CreateRemainingMonth(calendarMonth) ];
</script>

<table class={`table table-bordered table-sm ${tableClass}`} class:mini-calendar={mini}>
  <caption>{calendarMonth.monthName}</caption>
  <thead>
    <tr>
      {#each ['Sun', 'Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat'] as day (day+'-head')}
        <th class='text-center'>{day}</th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each month as week, i ("week-"+i)} <!-- Can actually loop thru ANYTHING with length prop so {length: 6} would work too -->
      <tr> <!-- Following key seems to rerender multiple times but uncertain why -->
        {#each week as day, j ("date-box-"+i*7+j) } <!--"date-box-" + WeekNum*7 DateBoxNum e.g. 'date-box-6'-->
          <CalendarDay game={grabGame(day)} currentMonth={calendarMonth.monthName.toLowerCase()} dayOfWeek={day} 
            mini={mini} even={i % 2 === 0} on:openModal/>
        {/each}
      </tr>
    {/each}
  </tbody>
</table>

<style lang='less'>
  @import '../Utility/Less/variables';

  table {
    font-family: 'Rambla', sans-serif !important;
    border-collapse: collapse;
    margin-left: auto;
    margin-right: auto;
    @media @max575 {
      width: 350px;
      height: 350px;
    }
    @media @min576 { //* Only way to use 'and' as expected in an @media query
      @media @max767 {
        width: 600px;
        height: 600px;
      }
    }
    @media @min768 {
      @media @max991 {
        width: 750px;
        height: 900px;
      }
    }
    @media @min992 {
      width: 975px;
      height: 1100px;
    }

    &.mini-calendar {
      max-width: 375px;
      max-height: 325px;
      @media @min576 { //* Only way to use 'and' as expected in an @media query
        @media @max991 {
          max-width: 380px;
          max-height: 325px;
        }
      }
      @media @min992 {
        max-width: 440px;
        max-height: 400px;
      }
    }
  }
  caption {
    color: #004680;
    font-size: 22px;
    text-align: center;
    caption-side: top;
  }
  thead {
    color: white;
    background-color: darken(@dodgerBlue, 12%) !important;
    & > tr th {
      @media @max575 {
        max-width: 10px;
        width: 10px;
        height: 10px;
      }
      @media @min576 {
        max-width: 40px;
        width: 40px;
        height: 30px;
      }
    }
  }
  
  tbody, th, thead, tr {
    border-color: black;
  }
  tbody {
    & > tr:nth-child(odd) {
      background-color: #ececec;
      color: black;
    }
    & > tr:nth-child(even) {
      background-color: #0290f5;
      color: white;
    }
  }
</style>