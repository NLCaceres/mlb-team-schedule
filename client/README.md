# Svelte - A Boilerplate and Virtual-Dom-Free Reactive Front-End Framework!

To start with svelte, use the following command, which will setup and install all dependencies 
```bash
npx degit sveltejs/template svelte-app
cd svelte-app
node scripts/setupTypeScript.js
npm install
npm run dev
```
...if no Typescript needed or wanted, then just remove the setup on line 3 and run
```bash
rm scripts/setupTypeScript.js
```

...then start [Rollup](https://rollupjs.org) from (client directory):

```bash
npm run dev
```

...or from Flask root:
```bash
npm run --prefix client dev
```
  - To change port for Svelte's dev server, include PORT=xxxx before these above commands (e.g. `PORT=5001 npm run dev`)

By default, the server will only respond to requests from localhost. To allow connections from other computers, edit the `sirv` commands in package.json to include the option `--host 0.0.0.0`.

For a production build, simply run the following commands and thanks to sirv, you can actually straight deploy to Heroku!
```bash
npm run build
npm run start
```

## Single-page app mode

By default, sirv will only respond to requests that match files in `public`. This is to maximise compatibility with static fileservers, allowing you to deploy your app anywhere.

If you're building a single-page app (SPA) with multiple routes, sirv needs to be able to respond to requests for *any* path. You can do that by editing the `"start"` command in package.json:

```js
"start": "sirv public --single"
```

## Deploying to the web

### With [Vercel](https://vercel.com)

Install `vercel` if you haven't already:

```bash
npm install -g vercel
```

Then, from within your project folder:

```bash
cd public
vercel deploy --name my-project
```

### With [Surge](https://surge.sh/)

Install `surge` if you haven't already:

```bash
npm install -g surge
```

Then, from within your project folder:

```bash
npm run build
surge public my-project.surge.sh
```
