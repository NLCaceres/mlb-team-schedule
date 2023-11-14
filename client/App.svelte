<script lang="ts">
	import { beforeUpdate, onMount } from 'svelte';
	import { Router, Route, navigate } from "svelte-navigator";
	import Alert from './Common/Alert.svelte';
	import GameModal from './GameModal.svelte';
	import Navbar from './Navbar.svelte';
	import Redirect from "./Common/Redirect.svelte";
	import MiniCalendarView from './Views/MiniCalendarView.svelte'
	import SingleDayView from "./Views/SingleDayView.svelte";
	import SingleMonthView from "./Views/SingleMonthView.svelte";
	import { Modal as BsModal, Alert as BsAlert } from "bootstrap";
	import { MONTH_MAP } from "./Models/Month";
	import type BaseballGame from './Models/DataClasses';
  import { currentYear } from './HelperFuncs/DateExtension';

	//? Using a function introduces a bit of reactivity! Instead of a simple var or even just writing the main find() fn 
	const monthsInSeason = Object.keys(MONTH_MAP).slice(2, -2);
	const thisYear = currentYear();

	let ballGameModal;
	let invisibleAlert = true; //* Alert starts invisible
	onMount(()=> {
		ballGameModal = new BsModal(document.getElementById("gameModal")); //* Must specify here or modal div does not exist!
		new BsAlert(document.getElementById('offDayAlert')); //* Could use data attr but for this use case (custom event handler) easier to do this
	})
	beforeUpdate(() => {
		const month = window.location.pathname.split('/')[1]; //* URLs should split as ['', 'month', 'day'], so just get the month
		const foundMonth = MONTH_MAP[month.slice(0,1).toUpperCase() + month.slice(1)];
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
	<Navbar links={monthsInSeason} currentYear={thisYear} />
	
	<main>
		<h1 class="main-title text-center mx-3 mb-4">Dodger Stadium Promotional Schedule {thisYear}!</h1>

		<Route path="/:monthName/:dayNum" let:params>
			<SingleDayView monthName={params.monthName} day={parseInt(params.dayNum)} />
		</Route>
		<Route path="/:monthName">
			<SingleMonthView currentYear={thisYear} on:openModal={displayBaseballGameModal} />
		</Route>
		<Route path="/fullSchedule">
			<MiniCalendarView currentYear={thisYear} months={monthsInSeason} on:openModal={displayBaseballGameModal} on:openAlert={displayOffdayAlert}/>
		</Route>

		<Route path="/*">
			<Redirect to="/fullSchedule"/>
		</Route>

		<GameModal modalID='gameModal' game={modalBallGame} />

		<Alert alertID="offDayAlert" invisible={invisibleAlert} on:openAlert={displayOffdayAlert}
			alertClasses="dodgerBlue-bg-dark border rounded border-light border-2">
				Sorry! No Dodger Game today! <!--TODO: Handle off-season too? Diff message? -->
		</Alert>
	
	</main>

</Router>


<style lang='less'>
	@import './CSS/variables';

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