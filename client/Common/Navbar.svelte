<script lang="ts">
  import { useLocation, Link } from "svelte-routing";
  import { fade } from "svelte/transition";
  import { expandable } from "../Actions/UseExpandable";

  $: innerWidth = window.innerWidth;

  export let links: string[] = [];
  export let currentYear: string;
  const location = useLocation(); //? Exposes $location which acts as a basic reactive location obj
  const isActive = (linkURL: string) => ($location.pathname.slice(1) === linkURL.toLowerCase()) ? "active" : "";

  let expanded = false;
</script>

<svelte:window bind:innerWidth />

<nav class="navbar navbar-expand-lg navbar-dark custom-nav" use:expandable={expanded}>
  <div class="container-fluid">

    <a class="navbar-brand fs-2" href="/">Dodgers {currentYear}</a>
    <button class="navbar-toggler" type="button" aria-controls="navbarNav" on:click={() => { expanded = !expanded; }}
      aria-expanded={(expanded || innerWidth > 991) ? "true" : "false"} aria-label="Toggle navigation">
      <span class="navbar-toggler-icon" />
    </button>

    {#if expanded || innerWidth >= 992}
      <div class="navbar-collapse collapse show" transition:fade id="navbarNav">
        <ul class="navbar-nav fs-4">
          {#each links as linkURL (linkURL)}
            <li class="nav-item">
              <!-- Good to use toLowerCase() since search engines may prefer simple all lowercased URLs -->
              <Link to="/{linkURL.toLowerCase()}" class={`nav-link ${isActive(linkURL)}`.trim()} on:click={() => { expanded = false; }}>
                {linkURL}
              </Link>
            </li>
          {/each}
        </ul>
      </div>
    {/if}

  </div>
</nav>

<style lang="less">
  @import "../CSS/variables";

  .custom-nav {
    background-color: darken(@dodgerBlue, 30%);
    overflow: hidden;
    align-items: start;
    width: 100%;
    position: absolute;
    top: 0;
    z-index: 1000;
  }
  .nav-item {
    @media @max768 {
      margin-left: 1.5em;
    }
  }
</style>