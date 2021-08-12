# Dodgers Promo Schedule 2021
Even though MLB's site can be a great one stop shop for any and all questions about the schedules of every team you can think of, I've found that
it's pretty rare you check any other team but your favorite, in my case the Dodgers. Personally, though the MLB schedule pages are decent, I've found
that the site can be pretty slow, will often stop midload, and generally, the list of promotions is not displayed in the prettiest or most logical fashion.
After noticing that the site was actually calling out to an open stats API, I knew exactly what I'd like to do, make my own version of it! Thankfully,
there's a python wrapper on github ([MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI)) that does a great job of explaining how the API endpoints work.
Using it as my guide, I did my best to craft parsing functions and endpoints that would give me exactly what I needed and nothing else. Once the Flask backend 
was mostly structured and laid out, I set myself on learning Svelte for the frontend, which I'd say was quite the success. 

Svelte is an amazing up-and-coming front-end framework that really delivers on the oh-so-common promise of 'It just works.' Though I did find a few quirks
such as the handling of API calls and reactivity updates a bit odd compared to my other favorite, Vue, it was absolutely nothing that couldn't be solved with
a few well placed debuggers and console.log, of course. Like any front-end framework, a solid understanding of its lifecycle and tools fixes all problems, and once
I felt comfortable, Svelte didn't just deliver on a simple setup, but on a speedy development process. Putting together the Calendar component was a breeze as any subcomponents or parent components fell right into place without the common React problem of messy and neverending component files. 
Additionally, thanks to Svelte's special components and bindings like 'svelte:window' & 'on:customEvent', it's pretty easy to avoid complicated prop drilling or
event messaging. While I did find myself yearning for helpers like Vue-Router or dynamic slot names, given how much work is going into SvelteKit, I look forward to
the immensely well fleshed out front-end framework that will be here before we know it. Until then, I can imagine updating this project for the coming 2022 baseball season to use Svelte's already excellent store system as a nifty built-in Redux/Vuex replacement. 

This project felt like exactly the injection of fun that I think any developer can use every once and a while, an absolute passion project to get the creative
juices flowing. As with any project, though, every time you reach the expected finish line, you can't help but think of just one more awesome feature to add, and 
that is exactly where I stand today. In the future, I hope not only to add in Svelte's store state feature to the front-end, but I hope to continue to improve the backend, making it more flexible and simple to handle any team that someone who cloned this repo could want. Consequently, I'd also love to create several global.css
files that can be swapped in as a particular team's theme without a single thought, beautifully matching team colors and logos to every component. As the 2021 season
winds down, I'll continue to think up new and fun features that I can add in the offseason, but until then, I'm quite proud of this little Dodger schedule app. 
For anyone who finds it, hopefully it helps you as much as it's helped me, and let me know what you think I should add, thanks! 

## Workflow
- To start
  - Enter the directory on the terminal and use `python3 -m venv venv` if an existing venv directory does not exist
    - Similar to running `npm install` after cloning a new node project
  - `. venv/bin/activate` will switch into that vEnvironment, with the proper
  python version as well as pip version, so you can be in a nicely isolated 
  package environment, just like a package.json would provide a Node project
  - Double check `which pip` & `which python` to be sure it's the venv directory ones and from there install your needed packages via that 'pip'!
- To run server, use python server.py 
  ```
  python server.py & PORT=5001 npm run dev
  ```
  - This should not only serve up the svelte root but autoload changes made to it.
- Flask should autoload .env files but if not include `load_dotenv=True` in the app.run command
  - Also important to have python-dotenv or flask won't have dotenv to load in the .env files

## Created CLI Commands 
- Since Flask uses Click to make its own commands, it also exposes it for you to use, making it very to create your own CLI commands for all kinds of things!
- In the case of this app, the few commands are related to updating the database
  - `flask seed db` -> Simply inits the database (once Flask-migrate has done the proper migrations of course)
  - `flask update scheduleDb` -> Updates any games in database with date from now to end of season
  - `flask update teamRecordsDb` -> Updates standings of teams in database using ESPN stats api
  - `flask update promotionsDb` -> Updates promotions from current date to end of season
  - First two commands, most used since first inits and second update version actually calls the teamRecords and promotions update

### Flask-Migrate
- A useful extension of Flask-SQLAlchemy that uses Alembic to manage your app's migrations
- Useful Commands
  - `flask db init` -> sets up directory of migrations
    - FLASK_APP, which defaults to app or wsgi, env var needs to be properly set up to be sure work above command works 
  - `flask db migrate` -> Quick creation of migrations based on models after above command sets up 
    - May need to do additional work to newly created migrations to get them exactly as desired
  - `flask db upgrade` -> Actually run migrations on DB
  - WORKFLOW NOTE: `db init` is only run once! `db migrate` + `db upgrade` is run every time you need to make migration changes

  Bonus Tip - `pip show 'pypiPkgName'` will display all requirements for that particular package plus the venv location 
  and what packages require that package! Super helpful if VSCode doesn't recognize imports

### Notes on Seeding & the MLB-Stats API
- Main Concern at the moment: How are double headers handled?
  - Typically it seems rain delays get rescheduled next day turning single games into double headers which would make
  the max number of games on a single day, for sure, two. 
    - Mostly remains the same EXCEPT
      - doubleHeader value goes from 'N' to 'S'
      - scheduledInnings value goes from 9 to 7
      - New rescheduledFrom key appears! with original UTC time
    - Important to note that gamesInSeries & seriesGameNumber MAY change but likely will remain the same
      - So if the first game in the series got rained out, the next day will have two games, with the first being the replacement
      for the original first game, making gamesInSeries remain the same AND the seriesGameNumber the same while only the dates changed!