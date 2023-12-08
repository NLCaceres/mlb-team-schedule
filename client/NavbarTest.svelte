<script lang="ts">
  import Navbar from "./Navbar.svelte";
  import { Router } from "svelte-routing";

  export let links: string[] = [];
  export let currentYear: string;
</script>

<Router>
  <Navbar {links} {currentYear} />
</Router>
