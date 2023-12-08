<script lang="ts">
  import CalendarDay from "./CalendarDay.svelte";
  import type BaseballGame from "../Models/DataClasses";
  import { CreateMonth } from "./CreateCalendar";
  import { getDayFromDateStr } from "../HelperFuncs/DateExtension";

  //* Normal Props
  export let monthName: string;
  export let gamesList: BaseballGame[];
  let offDays = 0; //* Tracks days without a game to calc game assignment
  //* Css Props
  export let mini = false;
  export let tableClass = ""; //* Allow default prop

  const month = CreateMonth(gamesList[0]); //* If gamesList is empty, then val at index 0 is undefined

  function getTodaysGames(day: string): BaseballGame[] {
    if (day.length === 0 || gamesList.length === 0) { return []; }

    const calendarDayNum = parseInt(day); //* Proper way of turning "1" -> 1 (rather than +day via "+" unary operator)
    const nextIndex = calendarDayNum - (1 + offDays); //* Goal: Assign every game in list to a day!
    if (nextIndex >= gamesList.length) { return []; } //* At end of the month, so no more off-days/games. Rest of calendar is empty
    const expectedGame = gamesList[nextIndex];
    const todaysGames = [expectedGame];
    if (nextIndex < gamesList.length - 1) {
      todaysGames.push(gamesList[nextIndex + 1]); //* Add next game just in case a doubleheader is happening
    }

    //* Each iteration takes the day # of the month in int form, not string form
    const finalGamesList = todaysGames.filter(game => parseInt(getDayFromDateStr(game.date)) === calendarDayNum);
    if (finalGamesList.length === 0) { offDays++; return []; } //* No game on this day, so this keeps the gameList index in the same spot
    return finalGamesList;
  }
</script>

<table class={`table table-bordered table-sm ${tableClass}`} class:mini-calendar={mini}>
  <caption>{monthName}</caption>
  <thead>
    <tr>
      {#each ["Sun", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat"] as day (day+"-head")}
        <th class="text-center">{day}</th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each month as week, i ("week-"+i)} <!-- Can actually loop thru ANYTHING with length prop so {length: 6} would work too -->
      <tr> <!-- Following key seems to rerender multiple times but uncertain why -->
        {#each week as day, j ("date-box-"+i*7+j) } <!--"date-box-" + WeekNum*7 DateBoxNum e.g. "date-box-6"-->
          <CalendarDay games={getTodaysGames(day)} currentMonth={monthName.toLowerCase()} dayNum={day} even={i % 2 === 0} {mini} on:clickCalendarDay />
        {/each}
      </tr>
    {/each}
  </tbody>
</table>

<style lang="less">
  @import "../CSS/variables";

  table {
    font-family: "Rambla", sans-serif !important;
    border-collapse: collapse;
    margin-left: auto;
    margin-right: auto;
    @media @max575 {
      width: 350px;
      height: 350px;
    }
    @media @min576 { //* Only way to use `and` as expected in an @media query
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
      @media @min576 { //* Only way to use `and` as expected in an @media query
        @media @max991 {
          max-width: 380px;
          width: 380px; //* Solves an odd safari issue for wider screens
          max-height: 325px;
        }
      }
      @media @min992 {
        max-width: 440px;
        width: 440px; //* Solves an odd safari issue for wider screens
        height: 800px;
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