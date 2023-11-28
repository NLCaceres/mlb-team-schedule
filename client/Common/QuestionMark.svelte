<script lang="ts">
  export let width: number;
  export let height: number;
  export let outlineColor: string | undefined = undefined;
  export let fillColor: string | undefined = undefined;
</script>

<svg xmlns="http://www.w3.org/2000/svg" {width} {height} viewBox="0 0 38 38" role="img" aria-labelledby="question-mark-icon">
  <title id="question-mark-icon">Question Mark Icon</title>
  <circle cx="19" cy="19" r="17" stroke={outlineColor} stroke-width="2.5" fill="none" />
  <path d="M 9.5,15 C 11.5,3 27.5,3 28,15 C 28,21 21.5,19 21.5,24.25 L 16.5,24.25
    C 15.5,18 22.5,19 24.5,15 C 25.5,7 13.5,7 13,15 L 9.5,15" stroke="black" stroke-width="1" fill="black" />
  <rect x="16.9" y="27.5" width="4.5" height="4.5" stroke={outlineColor} stroke-width="1" fill={fillColor} />
</svg>
