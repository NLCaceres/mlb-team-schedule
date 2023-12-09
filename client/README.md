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
- Upgraded to Svelte 4 with Typescript 5.3 and Node 20.9
  - Also replaced Svelte-Navigator with Svelte-Routing, in particular, `<Link>` replaced simple `<a>` tags for better testability
- Added Vitest 1.0! Alongside `testing-library/Svelte`, `testing-library/jest-dom`, and `testing-library/user-event` for easy component testing
- Added ESLint plus the Typescript and Svelte plugins to speed up linting and get novel recommendations
- Improved Data Fetching process
  - Now handling GET requests with generic method plus custom Error typing
  - Adapted API fetch methods + models to API's latest changes to the JSON structure
  - Main View pages optimized fetching to run only once, preventing extra requests
  - `<Image>` now catches `undefined` URLs to prevent extra requests
- Updated Calendar props to adapt to a normal/generalized Baseball season each year
  - Faster rendering with less prop-drilling, simpler algorithm, quick dependencies like date-fns, and more edge-cases considered
  - Dropped TS enums + unnecessary Month interface
  - Updated Calendar creation methods to accept params more specific to their responsibilities
  - Renamed and improved reusability of dispatched Calendar click events
- Added type guards to simplify complicated but common type checking
  - Includes String, Array, and Object `isEmpty()` checker
- The schedule year now dynamically sets itself to the current year
  - Added hoverable Tooltip + Subtitle which uses both Tooltip and dynamic year
  - Simplified date getter methods
- `Client/Utility` directory reorganized across the `Client` folder into `Common` components, `CSS` style files, and `HelperFuncs` directories
  - `CreateCalendar.ts` moved into `Calendar`
  - `CreateSvgElement` added an `unescape()` function
  - Lodash dropped entirely
  - `<Navbar>` moved into `Common` after dropping Bootstrap data attributes in favor of Svelte control
- `<Navbar>`, `<Alert>`, and `<Modal>` no longer use Bootstrap Javascript to function. Now fully Svelte controlled and animated
  - `<Modal>` added [A11y-Dialog](https://github.com/KittyGiraudel/a11y-dialog) to remain accessible
  - `<Navbar>` added a reusable Expandable Action to animate height resizes on mobile viewports when `<Navbar>` opens to show links
- `<CalendarDay>` moved clickListener from the `<div>` to the `<td>` to improve accessibility and increase the touch target size


## Future Changes
- If Flask changes the selected team, use the new team to theme the app, i.e. instead of Dodger blue, use Yankee blue, etc.
  - Dynamically update the favicon? Use `<svelte:head />`?
  - Similarly, can the individual detail view of a game be better themed based partly on the opposing team?
- Provide a view that shows the box score of a game in progress AND completed games
  - Best to directly call the MLB stats API to limit work of Flask server and reduce storage cost in DB
    - Update in real time? setInterval API call? websocket?
- Update calendar view
  - Add `role="grid"` to improve click interactions with the Calendar views
    - Add `tabindex=-1` to actual days in a Calendar month enabling interactivity once the Calendar view is `TAB` selected
  - Double header -> Diagonally or horizontally split box?
  - Simplify conditional rendering of the Game/Promo section, so CalendarDayDetail can be used on big and small screens
- Update Image Component to not only provide a placeholder but lazy load only when on-screen
- Update Alert to allow the component itself to control its visibility e.g. enable auto-fading
- Drop Bootstrap in favor of TailwindCSS to make the design more custom, less Bootstrap-y, and to handle cases where only simple CSS styling is needed
- `DynamicEventBinding` is an incredibly powerful option for Components BUT completely unused at the moment so it may be a case of
optimizing too early, and better to drop rather than work out the testing
- String helper method that trims concatenated `string` props as well as CSS & Style strings

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
