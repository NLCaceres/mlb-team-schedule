<script lang="ts">
  import { navigate, useLocation } from "svelte-routing";

  export let links: string[] = [];
  export let currentYear: string;
  const location = useLocation(); //? Exposes $location which acts as a basic reactive location obj
</script>

<nav class="navbar navbar-expand-lg navbar-dark custom-nav">
  <div class="container-fluid">

    <a class="navbar-brand fs-2" href="/">Dodgers {currentYear}</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon" />
    </button>

    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav fs-4">
        {#each links as linkURL (linkURL)}
          <li class="nav-item">
            <!-- Without on:click event, the <li> tag seems to swallow the <a>'s routing event -->
            <!-- ALSO better to use toLowerCase() since search engines may prefer simple all lowercased URLs -->
            <a href="/{linkURL.toLowerCase()}" on:click={() => { navigate(`/${linkURL.toLowerCase()}`); }}
              class="nav-link" class:active={$location.pathname.slice(1) === linkURL.toLowerCase()}
              data-bs-toggle="collapse" data-bs-target=".navbar-collapse.show"> {linkURL} </a>
          </li>
        {/each}
      </ul>
    </div>

  </div>
</nav>

<style lang="less">
  @import './CSS/variables';

  .custom-nav {
    background-color: darken(@dodgerBlue, 30%);
  }
  .nav-item {
    @media @max768 {
      margin-left: 1.5em;
    }
  }
</style>