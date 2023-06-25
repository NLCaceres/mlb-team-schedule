# Dodgers Promotional Schedule
Even though MLB's site can be a great one stop shop for any and all questions about the schedules of every team you can think of, I've found that
it's pretty rare you check any other team but your favorite, in my case the Dodgers. Personally, though the MLB schedule pages are decent, I've found
that the site can be pretty slow, will often stop mid-load, and generally, the list of promotions is not displayed in the prettiest or most logical fashion.
After noticing that the site was actually calling out to an open stats API, I knew exactly what I'd like to do, make my own version of it! Thankfully,
there's a python wrapper on github ([MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI)) that does a great job of explaining how the API endpoints work.
Using it as my guide, I did my best to craft parsing functions and endpoints that would give me exactly what I needed and nothing else. Once the Flask backend 
was mostly structured and laid out, I set myself on learning Svelte for the frontend, which I'd say was quite the success. 

Svelte is an amazing up-and-coming front-end framework that really delivers on the oh-so-common promise of 'It just works.' Though I did find a few quirks
such as the handling of API calls and reactivity updates a bit odd compared to my other favorite, Vue, it was absolutely nothing that couldn't be solved with
a few well placed debuggers and console.log, of course. Like any front-end framework, a solid understanding of its lifecycle and tools fixes all problems, and once
I felt comfortable, Svelte didn't just deliver on a simple setup, but on a speedy development process. Putting together the Calendar component was a breeze as any sub-components or parent components fell right into place without the common React problem of messy and never-ending component files. 
Additionally, thanks to Svelte's special components and bindings like 'svelte:window' & 'on:customEvent', it's pretty easy to avoid complicated prop drilling or
event messaging. While I did find myself yearning for helpers like Vue-Router, thanks to development on Sveltekit, Svelte, itself, will only continue to grow. In meantime, I can imagine updating this project for coming baseball seasons to use Svelte's already excellent store system as a nifty built-in Redux/Vuex replacement.

This project felt like exactly the injection of fun that I think any developer can use every once and a while, an absolute passion project to get the creative
juices flowing. As with any project, though, every time you reach the expected finish line, you can't help but think of just one more awesome feature to add, and 
that is exactly where I stand today. In the future, I hope not only to add in Svelte's store state feature to the front-end, but I hope to continue to improve the backend, making it more flexible and simple to handle any team that someone who cloned this repo could want. Consequently, I'd also love to create several global.css
files that can be swapped in as a particular team's theme without a single thought, beautifully matching team colors and logos to every component. Until then, I'm quite proud of this little Dodger schedule app. 

For anyone who finds it, hopefully it helps you as much as it's helped me, and let me know what you think I should add, thanks! 

## Workflow
- To start
  - Enter the directory on the terminal and use `python3 -m venv venv` if an existing venv directory does not exist
    - Similar to running `npm install` after cloning a new node project
  - `. venv/bin/activate` will switch into that virtual environment, with the proper python version as well as `pip` version, so you can be in a nicely isolated 
  package environment, just like a package.json would provide to a Node project
    - `source venv/bin/activate` also works! See [Real Python](https://realpython.com/python-virtual-environments-a-primer/) or 
    [PyPA](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) for more info!
    - Double check via `which pip` and `which python` to be sure it's the venv directory ones and from there install your needed packages via `pip`!
      - A triple check would be to run `python3 -m pip list` which should list all packages from your requirements.txt
    - If the incorrect `pip` or python is listed, then it's worth checking the activate script inside of `venv/bin`, especially if any parent directories have
    had their names changed.
      - Directly altering the activate script works but you can also run `python3 -m venv venv --clear` followed by `python -m pip install -r requirements.txt` like
      you'd do after a fresh git clone was made
        - Adding the `--clear` flag resets the venv folder, completely fresh and ready to restart!
- To run the `Flask` server, it's easiest to use `flask run`
  - It is also possible to run `Flask` like a typical python program via `python app.py` which will run the code in the `if __name__ == "__main__"` block
  - This along with `python-dotenv` should load any `.env` files 
    - If it doesn't, then adding `load_dotenv=True` to the app.run command fixes this issue
- With the addition of `Vite`, it is useful to have [`foreman`](https://github.com/ddollar/foreman), so it can run `Vite` in dev mode while `Flask` acts as a 
simple API server.
  - The start command would be `foreman local -f Procfile.dev`
    - HOWEVER, due to issues with Mac's system version of Ruby, I found it simplest to use the Go Port of `Foreman`, i.e. `ForeGo`
  - In `Forego`, the command is `forego start -f Procfile.dev`
  - Why though? `Flask`, nor `Vite` seem to like to be run in the background, so using Foreman makes separating the processes easy
  - BUT since `Vite` does not produce a build in dev mode, Vite must use a proxy to send Axios requests to the `Flask` API in dev
    - See `vite.config.js` for an example
    - Alternatively, running `vite build -w` may work since it'll produce a build to a `dist` folder that `Flask` can serve by changing line 11 in `app.py`
    from `Flask(__name__, static_folder="public")` to `Flask(__name__, static_folder="dist")`
      - This method SHOULD eliminate the need for `foreman` since `Flask` could just serve Svelte index.html from the `templates` directory as long as 
      all of the url_for('static') calls are updated properly in `templates/index.html`
- Bonus Pip Tip - `pip show 'pypiPkgName'` will display all requirements for that particular package plus the venv location 
and what packages require that package! Super helpful if VSCode doesn't recognize imports
  - For even more tips, see [Pip PyPA](https://pip.pypa.io/en/latest/user_guide/)

## Future Changes
### Flask
- Migrate from Heroku to Railway
  - Since Railway deployments are always online, cron jobs are much easier! The APScheduler package's BackgroundScheduler() should do the trick, so the Flask app can 
  update the database if there are changes to the schedule week to week.
- Provide an Env var that can change the selected team
  - Likely best to map the name to the MLB stats API's team ID
  - Provide a simple deploy button? Railway template?
- Make DB seed commands a bit more flexible, in particular so the date adjusts yearly and accounts for fluctuations in each season's schedule (i.e. shortened seasons
and longer playoffs that may take the schedule from early March to early November!)
- Separate API routes into an API Blueprint that the main Flask app accepts in `app.py`, enabling the API routes to be split into their own file
  - Similarly, split seedDB based on usage, since some functions are helpers/utility, while others are main functions that are directly run by CLI commands
### Svelte
- Svelte 4 is now an option! BUT it has quite a few breaking changes, notably Node 16+ and Typescript 5 required
  - Overall, a full upgrade to the latest versions of npm packages is needed
- If Flask changes the selected team, use the new team to theme the app, i.e. instead of Dodger blue, use Yankee blue, etc.
  - Is it possible to dynamically update the favicon? Can a favicon be downloaded during DB seeding?
  - Similarly, can the individual detail view of a game be better themed based partly on the opposing team?
- Provide a view that shows the box score of a game in progress AND completed games
  - Best to directly call the MLB stats API to limit work of Flask server and reduce storage cost in DB
    - Update in real time? setInterval API call?
- Double header calendar view
  - Diagonally or horizontally split box?

### Railway
- Similar to Heroku, it should autodetect both the requirements.txt as well as the package.json, and run the needed buildpacks to setup dependencies
  - If Railway only detects one of the buildpacks (Python or NodeJS), then adding the `providers` config option to your `nixpacks.toml` file should add
  any needed buildpacks for monorepos like this one
    - As a bonus, `nixpacks.toml` can define every step (called phases) of the build process if needed! Which can help replicate Heroku's release phase by
    running `flask db upgrade` and seeding the database
- Unlike Heroku, it'll only use the Procfile's web process, reading it as a start command, so it's probably best to drop `Procfile` in favor of a `railway.toml` file
that contains a start command

## Created CLI Commands 
- Since `Flask` uses Click to make its own commands, it also exposes it for you to use, making it very to create your own CLI commands for all kinds of things!
- In the case of this app, the few commands are related to updating the database
  - `flask seed db` -> Simply inits the database (once Flask-Migrate has done the proper migrations of course)
  - `flask update scheduleDb` -> Updates any games in database with date from now to end of season
  - `flask update teamRecordsDb` -> Updates standings of teams in database using ESPN stats api
  - `flask update promotionsDb` -> Updates promotions from current date to end of season
  - First two commands, most used since first inits and second update version actually calls the teamRecords and promotions update

### Flask-Migrate
- A useful extension of Flask-SQLAlchemy that uses Alembic to manage your app's migrations
- Useful Commands
  - `flask db init` -> Creates and sets up the `migrations` directory
    - FLASK_APP, which defaults to app or wsgi, env var needs to be properly set up to be sure work above command works 
  - `flask db migrate` -> Create a migration file inside `migrations/versions` that's based on your models
    - Since Alembic isn't perfect, ALWAYS double check the DB changes it generates
  - `flask db upgrade` -> Run any new migrations on your DB
  - WORKFLOW NOTE: `db init` is only run once! `db migrate` + `db upgrade` is generally run every time you need to make migration changes

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