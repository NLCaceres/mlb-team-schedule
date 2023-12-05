<script lang="ts">
  import { beforeUpdate } from "svelte";
  import Alert from "./Common/Alert.svelte";
  import GameModal from "./GameModal.svelte";
  import Navbar from "./Navbar.svelte";
  import Redirect from "./Common/Redirect.svelte";
  import MiniCalendarView from "./Views/MiniCalendarView.svelte";
  import SingleDayView from "./Views/SingleDayView.svelte";
  import SingleMonthView from "./Views/SingleMonthView.svelte";
  import { MONTH_MAP } from "./Models/Month";
  import type BaseballGame from "./Models/DataClasses";
  import { currentYear } from "./HelperFuncs/DateExtension";
  import { isString } from "./HelperFuncs/TypePredicates";
  import { isToday } from "date-fns";
  //? TSConfig sets moduleResolution to "Node" to fix the Svelte-Routing typing BUT TS 5.0 prefers "Bundler" resolution for Vite
  import { Router, Route, navigate } from "svelte-routing";

  //? Using a function introduces a bit of reactivity! Instead of a simple var or even just writing the main find() fn
  const monthsInSeason = Object.keys(MONTH_MAP).slice(2, -2);
  const thisYear = currentYear();

  let invisibleAlert = true; //* Alert starts invisible
  beforeUpdate(() => {
    const month = window.location.pathname.split("/")[1]; //* URLs should split as ['', 'month', 'day'], so just get the month
    const foundMonth = MONTH_MAP[month.slice(0,1).toUpperCase() + month.slice(1)];
    if (!foundMonth) { navigate("/fullSchedule"); return; } //* Basic programmatic redirect with svelte
  });

  //! Click Listeners
  let modalBallGame: BaseballGame | null = null;
  function displayBaseballGameModal(event: CustomEvent<BaseballGame | string>) { //? `event.type` === name of custom event
    if (isString(event.detail)) {
      const [monthNum, dayNum] = event.detail.split("/"); //* Grab date vals from Slash-Split string: "MonthNum/DayNum"
      const isItToday = isToday(new Date(parseInt(thisYear), parseInt(monthNum) - 1, parseInt(dayNum)));
      displayOffdayAlert(true, `Sorry! No Dodger Game on ${isItToday ? "this" : "that"} day!`);
    }
    else { modalBallGame = event.detail; } //* ELSE a BaseballGame bubbled up
  }
  let alertMessage = "";
  let previousTimeout: ReturnType<typeof setTimeout> | null = null;
  function onOpenAlert(event: CustomEvent<boolean>) {
    displayOffdayAlert(event.detail, "Closing Alert"); //? onOpenAlert currently only fires on closing of the Alert
  }
  function onErrorMessage(event: CustomEvent<string>) {
    displayOffdayAlert(true, event.detail);
  }
  function displayOffdayAlert(shouldOpen: boolean, message: string) {
    if (previousTimeout) { clearTimeout(previousTimeout); } //* Prevents quick closures by an existing timeout fn;
    alertMessage = message;
    invisibleAlert = !shouldOpen;
    previousTimeout = setTimeout(() => { if (!invisibleAlert) { invisibleAlert = true; } }, 3000); //* Hide alert after 3 seconds
  }
</script>

<Router>
  <Navbar links={monthsInSeason} currentYear={thisYear} />

  <main>
    <h1 class="main-title text-center mx-3 mb-4">Dodger Stadium Promotional Schedule</h1>

    <Route path="/:monthName/:dayNum" let:params>
      <SingleDayView monthName={params.monthName} day={parseInt(params.dayNum)} />
    </Route>
    <Route path="/:monthName">
      <SingleMonthView currentYear={thisYear} on:clickCalendarDay={displayBaseballGameModal} />
    </Route>
    <Route path="/fullSchedule">
      <MiniCalendarView months={monthsInSeason} on:clickCalendarDay={displayBaseballGameModal}
        on:clickTodaysGame={displayBaseballGameModal} on:errorMessage={onErrorMessage} />
    </Route>

    <Route path="/*">
      <Redirect to="/fullSchedule" />
    </Route>

    <GameModal modalID="gameModal" game={modalBallGame} on:openModal={() => modalBallGame = null} />

    <Alert alertID="offDayAlert" fading invisible={invisibleAlert} on:openAlert={onOpenAlert}
      alertClasses="dodgerBlue-bg-dark border rounded border-light border-2">{alertMessage}</Alert>

  </main>

</Router>


<style lang="less">
  @import "./CSS/variables";

  .main-title {
    color: #004680;
    text-transform: uppercase;
    @media @max575 { //* Simplified media query - max-width 575px
      font-size: 2em;
      font-weight: bold;
    }
    @media @min576 { //* - min-width 576px
      font-size: 4em;
      font-weight: bolder;
    }
  }
</style>