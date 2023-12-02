<script lang="ts">
  import { beforeUpdate, onMount } from "svelte";
  import { Router, Route, navigate } from "svelte-navigator";
  import Alert from "./Common/Alert.svelte";
  import GameModal from "./GameModal.svelte";
  import Navbar from "./Navbar.svelte";
  import Redirect from "./Common/Redirect.svelte";
  import MiniCalendarView from "./Views/MiniCalendarView.svelte";
  import SingleDayView from "./Views/SingleDayView.svelte";
  import SingleMonthView from "./Views/SingleMonthView.svelte";
  import { Modal as BsModal, Alert as BsAlert } from "bootstrap";
  import { MONTH_MAP } from "./Models/Month";
  import type BaseballGame from "./Models/DataClasses";
  import { currentYear } from "./HelperFuncs/DateExtension";
  import { isString } from "./HelperFuncs/TypePredicates";
  import { differenceInCalendarDays, isBefore, isToday } from "date-fns";

  //? Using a function introduces a bit of reactivity! Instead of a simple var or even just writing the main find() fn
  const monthsInSeason = Object.keys(MONTH_MAP).slice(2, -2);
  const thisYear = currentYear();

  let ballGameModal;
  let invisibleAlert = true; //* Alert starts invisible
  onMount(()=> {
    ballGameModal = new BsModal(document.getElementById("gameModal")); //* Must specify here or modal div does not exist!
    new BsAlert(document.getElementById("offDayAlert")); //* Could use data attr but for this use case (custom event handler) easier to do this
  });
  beforeUpdate(() => {
    const month = window.location.pathname.split("/")[1]; //* URLs should split as ['', 'month', 'day'], so just get the month
    const foundMonth = MONTH_MAP[month.slice(0,1).toUpperCase() + month.slice(1)];
    if (!foundMonth) { navigate("/fullSchedule"); return; } //* Basic programmatic redirect with svelte
  });
  //TODO: Svelte-Routing now offers a useLocation hook, just like svelte-navigator, useful for the Navbar!

  //! Click Listeners
  let modalBallGame: BaseballGame | null = null;
  function displayBaseballGameModal(event: CustomEvent<BaseballGame | string>) { //? `event.type` === name of custom event
    if (isString(event.detail)) { displayOffdayAlert(true, event.detail); }
    else { //* ELSE a BaseballGame bubbled up
      ballGameModal.show();
      modalBallGame = event.detail;
    }
  }
  let alertMessage = "";
  let previousTimeout: ReturnType<typeof setTimeout> | null = null;
  function onOpenAlert(event: CustomEvent<boolean>) {
    displayOffdayAlert(event.detail, "Closing Alert"); //? onOpenAlert currently only fires on closing of the Alert
  }
  function displayOffdayAlert(shouldOpen: boolean, message: string) {
    if (previousTimeout) { clearTimeout(previousTimeout); } //* Prevents quick closures by an existing timeout fn;
    alertMessage = computeAlertMessage(message); //TODO: Maybe let the Child Routed View decide/compute the message?
    invisibleAlert = !shouldOpen;
    previousTimeout = setTimeout(() => { if (!invisibleAlert) { invisibleAlert = true; } }, 3000); //* Hide alert after 3 seconds
  }
  function computeAlertMessage(message: string) {
    const [monthNum, dayNum] = message.split("/"); //* Grab date vals from Slash-Split string: "MonthNum/DayNum"
    const parsedMonthNum = parseInt(monthNum);
    const parsedYearNum = parseInt(thisYear);
    const expectedDate =  new Date(parsedYearNum, parsedMonthNum - 1, parseInt(dayNum));
    const isItToday = isToday(expectedDate);
    const daysUntilRegularSeason = differenceInCalendarDays(new Date(2024, 2, 20), expectedDate);
    const daysUntilSeasonMessage = `Only ${daysUntilRegularSeason} days until the ${parsedYearNum + 1} Season officially begins!`;
    if (isItToday && parsedMonthNum === 2) { //TODO: Handle March Spring Training Dates
      const springTrainingStart = new Date(2024, 1, 22); //? Spring Training starts February 22 2024
      const springTrainingEnd = new Date(2024, 2, 26); //? AND ends just over a month later March 26 2024
      //? BUT due to early regular season international games, it seems Spring Training is briefly interrupted by actual games... Weird.
      const beforeSpringTraining = isBefore(expectedDate, springTrainingStart);
      return (beforeSpringTraining) ? "Spring Training is starting soon! Season's almost here!" :
        (isBefore(expectedDate, springTrainingEnd)) ? `Spring Training has begun! ${daysUntilSeasonMessage}` : "The regular season has begun!";
    }
    else {
      //* Ternary if fires when user clicks a date on the calendar OR if today is during the regular season
      //* Else condition assumes Today button was clicked because it's some unclickable date in November, December, or January
      //* Must offset months by 3 to account for March Season start
      return (monthsInSeason[parsedMonthNum - 3]) ? `Sorry! No Dodger Game on ${isItToday ? "this" : "that"} day!`
        : `Off-Season has begun! ${daysUntilSeasonMessage}`;
    }
  }
</script>

<!-- Svelte-Navigator unlike svelte-routing includes 'a11y' which, while helpful, manages focus!
  and can lead to somewhat odd behavior like unexpected outlined headers -->
<Router primary={false}> <!-- Setting primary to false prevents the odd focus a11y behavior -->
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
      <MiniCalendarView months={monthsInSeason} on:clickCalendarDay={displayBaseballGameModal} on:clickTodaysGame={displayBaseballGameModal} />
    </Route>

    <Route path="/*">
      <Redirect to="/fullSchedule" />
    </Route>

    <GameModal modalID="gameModal" game={modalBallGame} />

    <Alert alertID="offDayAlert" invisible={invisibleAlert} on:openAlert={onOpenAlert}
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