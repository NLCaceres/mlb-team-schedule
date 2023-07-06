<script lang="ts">
	import { beforeUpdate, onMount } from 'svelte';
	import { Router, Route, navigate } from "svelte-navigator";
	
	import Navbar from './Navbar.svelte';
	import { Modal as BsModal, Alert as BsAlert } from "bootstrap";
	import GameModal from './GameModal.svelte';
	import Redirect from "./Utility/Components/Redirect.svelte";
	import SingleDayView from "./Views/SingleDayView.svelte";
	import SingleMonthView from "./Views/SingleMonthView.svelte";
	import MiniCalendarView from './Views/MiniCalendarView.svelte'

	import type { Month } from "./Models/Month";
	import { Day } from "./Models/Month";
	import type RouteParams from 'svelte-navigator/types/RouteParam';
	import type BaseballGame from './Models/DataClasses';
	import Alert from './Utility/Components/Alert.svelte';
  import { currentYear } from './Utility/Functions/DateFormatter';

	let monthsDict = { //todo Try using API to set startDays
		'march': { monthName: 'March', startDay: Day.Wednesday, numDays: 31 },
		'april': { monthName: 'April', startDay: Day.Saturday, numDays: 30 },
		'may': { monthName: 'May', startDay: Day.Monday, numDays: 31 },
		'june': { monthName: 'June', startDay: Day.Tuesday, numDays: 30 },
		'july': { monthName: 'July', startDay: Day.Thursday, numDays: 31 },
		'august': { monthName: 'August', startDay: Day.Sunday, numDays: 31 }, 
		'september': { monthName: 'September', startDay: Day.Wednesday, numDays: 30 }, 
		'october': { monthName: 'October', startDay: Day.Friday, numDays: 31 }
	};

	//? Using a function introduces a bit of reactivity! Instead of a simple var or even just writing the main find() fn 
	const dodgerMonths = Object.values(monthsDict);
	const thisYear = currentYear();

	let ballGameModal;
	let invisibleAlert = true; //* Alert starts invisible
	onMount(()=> {
		ballGameModal = new BsModal(document.getElementById("gameModal")); //* Must specify here or modal div does not exist!
		new BsAlert(document.getElementById('offDayAlert')); //* Could use data attr but for this use case (custom event handler) easier to do this
	})
	beforeUpdate(() => {
		const nextUrlParam = window.location.pathname.slice(1); //* Don't need '/foo' with slash, need 'foo'
		const foundMonth: Month = monthsDict[nextUrlParam];
		if (!foundMonth) { navigate('/fullSchedule'); return; } //* Basic programmatic redirect with svelte
	})
	//todo Svelte-Routing now offers a useLocation hook, just like svelte-navigator, useful for the Navbar!

	let modalBallGame: BaseballGame | null = null;
	function displayBaseballGameModal(event: CustomEvent<BaseballGame | null>) { 
		if (event.detail) {
			ballGameModal.show(); 
			modalBallGame = event.detail;
		}
  }
	let previousTimeout: NodeJS.Timeout | null = null;
	function displayOffdayAlert(event: CustomEvent<boolean>) { 
		//* Event detail can only be true or false, so to be clear, receiving false will make alert invisible!
		if (previousTimeout) clearTimeout(previousTimeout); //* Prevents quick closures by an existing timeout fn;
		invisibleAlert = !event.detail;
		previousTimeout = setTimeout(() => { if (!invisibleAlert) invisibleAlert = true }, 3000); //* Hide alert after 3 seconds
  }
</script>

<!-- Svelte-Navigator unlike svelte-routing includes 'a11y' which, while helpful, manages focus! 
	and can lead to somewhat odd behavior like unexpected outlined headers -->
<Router primary={false}> <!-- Setting primary to false prevents the odd focus a11y behavior -->
	<Navbar links={dodgerMonths.map(month => month.monthName)} currentYear={thisYear} />
	
	<main>
		<h1 class="main-title text-center mx-3 mb-4">Dodger Stadium Promotional Schedule {thisYear}!</h1>

		<Route path="/:monthName/:dayNum" let:params>
			<SingleDayView monthName={params.monthName} day={parseInt(params.dayNum)} />
		</Route>
		<Route path="/:monthName" let:params>
			<SingleMonthView currentYear={thisYear} month={monthsDict[params.monthName]} on:openModal={displayBaseballGameModal} />
		</Route>
		<Route path="/fullSchedule">
			<MiniCalendarView currentYear={thisYear} months={dodgerMonths} on:openModal={displayBaseballGameModal} on:openAlert={displayOffdayAlert}/>
		</Route>

		<Route path="/*">
			<Redirect to="/fullSchedule"/>
		</Route>

		<GameModal modalID='gameModal' game={modalBallGame} />

		<Alert alertID="offDayAlert" invisible={invisibleAlert} on:openAlert={displayOffdayAlert}
			alertClasses="dodgerBlue-bg-dark border rounded border-light border-2">
				Sorry! No Dodger Game today!
		</Alert>
	
	</main>

</Router>


<style lang='less'>
	@import './Utility/Less/variables';

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