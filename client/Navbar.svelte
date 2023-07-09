<script lang='ts'>
  import { link as linkNav, navigate, useLocation } from "svelte-navigator";

  export let links: string[] = [];
  export let currentYear: string;
  const location = useLocation(); //? Exposes $location which acts as a basic reactive location obj
</script>

<nav class="navbar navbar-expand-lg navbar-dark custom-nav">
  <div class="container-fluid">

    <a class="navbar-brand fs-2" href="/">Dodgers {currentYear}</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav fs-4">
        {#each links as link} <!-- COULD include a key but not dynamic so not helpful-->
          <li class="nav-item">
            <!-- Without on:click event, Bootstrap 5 will prevent link from working as normal -->
            <!-- Also! navigate(to:string) will append 'toLink' to end of current url so be specific! add the prefix '/' if wanted to change baseUrl-->
            <a href="/{link.toLowerCase()}" on:click={() => navigate(`/${link.toLowerCase()}`)} 
              class="nav-link {$location.pathname.slice(1) === link.toLowerCase() ? 'active' : ''}"
              data-bs-toggle="collapse" data-bs-target=".navbar-collapse.show">
                {link}
            </a>
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