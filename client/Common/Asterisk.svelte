<script lang="ts">
  export let svgClasses = "";
  export let width: number;
  export let height: number;
  export let outlineColor: string | undefined = undefined;
  export let fillColor: string | undefined = undefined;
</script>

<!--? SVG <Path> treats all uppercase commands as ABSOLUTE POSITIONING. All lowercase commands are RELATIVE POSITIONING -->
<!--? SVG <Path> treats each command differently if it finds extra (X,Y) coordinates -->
<!--? If an "M" command has an extra (X,Y) coordinate, it'll create an L command to that next set of coordinates -->
<!--? If a "C" command has 3 extra (X,Y) coordinates then it'll just create a new C command -->
<svg xmlns="http://www.w3.org/2000/svg" class={svgClasses} {width} {height} viewBox="0 0 38 38" role="img" aria-labelledby="asterisk-icon">
  <title id="asterisk-icon">Asterisk Icon</title>
  <circle cx="19" cy="19" r="17" stroke={outlineColor} stroke-width="3" fill="none" />
  <!--* Original unscaled version -->
  <!-- <path d="M 3, 17.36 L 5.25, 10.42 L 16.53, 15.16
           L 15.55, 3 L 22.63, 3 L 21.51, 15.11
           L 33.03, 10.42 L 35.28, 17.35 L 23.12, 20.08
           L 31.62, 29.31 L 25.66, 33.47 L 18.97, 22.97
           L 12.62, 33.47 L 6.86, 29.32 L 14.96, 20.09
           L 3, 17.36" stroke="black" stroke-width="1" fill="none" /> -->
  <!--* Scaled to fit in Circle. Each line represents a point of the 5-sided Asterisk -->
  <path d="M 5.25, 17.5 L 8, 11.57 L 16.53, 15.16 L 15.79, 6.03 L 22.35, 6.03 L 21.51, 15.11
    L 30.00, 11.66 L 32.38, 17.95 L 23.12, 20.08 L 29.62, 27.17 L 24.06, 30.96 L 18.97, 22.97
    L 14.12, 30.99 L 8.86, 27.04 L 14.96, 20.09 L 5.25, 17.5" stroke={outlineColor} stroke-width="1" fill={fillColor} />
</svg>
<!--* The above works a bit better for positioning than using a <text> elem with a standard font asterisk -->
<!-- <svg xmlns="http://www.w3.org/2000/svg" width={width} height={height} viewBox="0 0 38 38" preserveAspectRatio="none">
  <text x="0" y="75" font-size="100" font-family="arial">*</text>
</svg> -->
