# Dodgers Promotions Schedule - Powered by Svelte - A Boilerplate and Virtual-Dom-Free Reactive Front-End Framework!

- To start with svelte, `npm init vite` is all you need

- Then to start it, run the `vite` command by making a `dev` script in the `package.json`, so you can run `npm run dev`
  - To change the Svelte dev server's PORT, prepend `PORT=xxxx`, i.e. `PORT=5001 npm run dev`
  - Since `Vite` does not produce a build in dev mode, Vite must use a proxy to send API requests to the `Flask` API in dev
    - Setup is required in the `vite.config.js`, setting the `server.proxy` key, to have the following config:
      - `target: 127.0.0.1:FLASK_API_PORT` -> Typically PORT 5000, and NOT `localhost`
      - `changeOrigin: true`, `secure: false`, and SOMETIMES `ws: true`
    - Alternatively, running `vite build -w` MOSTLY works since it produces a build in a `dist` folder that `Flask` can serve
      - This method SHOULD eliminate the need for `forego` since `Flask` could just serve Svelte's index.html from the `templates` directory as long as 
      all of the `url_for('static')` calls are updated properly in `templates/index.html`
      - The problem `url_for('static')` call that needs adjusting/updating is `build/bundle` files since Vite prefers to use `assets/index` files which can
      include a hash extension that may change every re-build
      - The solution (seemingly) is to add a `build.rollupOptions.output` key to your `vite.config.ts`. Inside this `output` key, 
      a simple adjustment to the `assetFileNames` and `entryFileNames` options can be made that should ensure consistent `assets/index` files across builds

- To generate a production build, add a `build` script into the `package.json` that runs `vite build`
  - To re-run the `build` script on save, change the `build` script to `vite build -w`, which is a helpful command for previewing what Flask will serve in
  production


## Recent Changes
- Prep for Svelte 4 by updating package.json completely, in particular to Typescript 5.1 and Node 18
- Add Vitest for unit testing + `testing-library/Svelte` for Component testing
- Update Calendar props to adapt to a normal/generalized Baseball season each year
  - Speed up rendering with less prop-drilling, simpler algorithm, quick dependencies like date-fns, and more edge-cases considered
  - Get rid of TS enums + unnecessary Month interface
- Use current year to set the schedule year dynamically
- `Client/Utility` directory reorganized across the `Client` folder into `Common` components, `CSS` style files, and `HelperFuncs` directories
  - Several files moved entirely, specifically `CreateCalendar.ts` moved into `Calendar` and `CreateSvgElement` now contains its necessary `unescape()` function
  - Lodash dropped entirely
- `API` folder added to organize common HTTP Request functionality, the main set of API endpoints, and, in the future, a set of MLB endpoints


## Future Changes
- Svelte 4 is now an option! BUT Svelte-Navigator is currently the main issue as it lags behind in development
  - Svelte-Routing is an option since it, now, includes the useLocation hook
- If Flask changes the selected team, use the new team to theme the app, i.e. instead of Dodger blue, use Yankee blue, etc.
  - Is it possible to dynamically update the favicon?
  - Similarly, can the individual detail view of a game be better themed based partly on the opposing team?
- Provide a view that shows the box score of a game in progress AND completed games
  - Best to directly call the MLB stats API to limit work of Flask server and reduce storage cost in DB
    - Update in real time? setInterval API call? websocket?
- Update calendar view
  - Double header -> Diagonally or horizontally split box?
  - Update Image Component to not only provide a placeholder but lazy load only when on-screen
  - CalendarDay currently is difficult to access for screen readers since a `<div>` will only have its text read aloud without any interactivity.
  Consequently, the `<div>` inside `<td>` should be swapped for a `<button>` that calls the new onClick handler
    - Alternatively, the tap target can be made larger by placing the onClick handler on the `<td>` itself, which is already easily accessible.
    - Additionally, to simplify the conditional rendering of its Game/Promo section, CalendarDayDetail should be styled so that the first
    `{:else if game}` condition is not needed. Instead, CalendarDayDetail should render something similar to the `else if` condition's simple layout
- If dropping Bootstrap, one of the first components that can be improved is the Modal via the new `<dialog>` elem
  - Partially because testing Svelte Slots currently requires making test components because there is no simple internal Svelte createSlot API
- `DynamicEventBinding` is an incredibly powerful option for Components BUT completely unused at the moment so it may be a case of
optimizing too early, and better to drop rather than work out the testing
- A `StringHelper` file would probably be super helpful to process a number of strings across the app, in particular:
  - Trim concatenated `string` props as well as CSS & Style strings
  - Identify empty strings (i.e. "") since Svelte Props can't be set to Optional via the `?` marker
    - An alternative around this limitation is either:
      - `export let someProp: someClass | undefined = undefined`
      - `export let someProp: Optional<someClass> = undefined` via a type alias like `type Optional<T> = T | undefined;`

## Deploying to the web
- Modern Svelte recommends using SvelteKit, since it handles just about everything you can think of, BUT it's still possible to deploy a standard Svelte
app onto the following platforms
#### With [Vercel](https://vercel.com)

Install `vercel` if you haven't already:

```bash
npm install -g vercel
```

Then, from within your project folder:

```bash
cd public
vercel deploy --name my-project
```

#### With [Surge](https://surge.sh/)

Install `surge` if you haven't already:

```bash
npm install -g surge
```

Then, from within your project folder:

```bash
npm run build
surge public my-project.surge.sh
```
