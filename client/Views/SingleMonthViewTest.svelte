<script lang="ts">
  import { Router } from "svelte-navigator";
  import SingleMonthView from "./SingleMonthView.svelte";

  export let currentYear: string;
</script>

<Router>
  <SingleMonthView currentYear={currentYear} />
</Router>