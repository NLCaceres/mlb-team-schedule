<script lang="ts">
  import { Router } from "svelte-routing";
  import SingleMonthView from "./SingleMonthView.svelte";

  export let currentYear: string;
</script>

<Router>
  <SingleMonthView {currentYear} />
</Router>