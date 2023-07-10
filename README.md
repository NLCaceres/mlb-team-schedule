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

## Recent Changes
- Split `app.py` into a `create_app()` oriented `__init__.py` file, allowing `app.py` to do the final configuration before launching Flask in the
`if __name__ == '__main__'` condition
- API routes and custom CLI Commands split into their own files via the Flask Blueprint pattern
- Database Seed file split into two command method files as well as three helper method files
  - The Seeder, itself, adjusts for year and now accounts for longer season and adjusted schedules, and heavily depends on all three helper files
    - Contains endpoint generation methods, the main CLI command, and model parse/creation methods
  - The Update file contains 2 CLI commands, BUT depends on all three helper files as well as a few methods from the Seeder
    - Update the promotions, depends on datetimeHelpers and the Seeder's endpoint generation methods as well as Promotion creation method 
    - Update Team records, depends on a specific URL from the endpointHelpers, and its own mapping/parsing method
- Add pyproject.toml + `pip-tools` generated `requirements.txt` via `requirements.in` for better dependency management
- Configured `tests` directory with `Pytest` by adding a fixture to load the `.env` file as well as a set of `create_app()` oriented fixtures
  - Added tests for utility methods, i.e. Database, datetime class, and endpoint URL helpers


## Future Changes
- Migrate from Heroku to Railway
  - Since Railway deployments are always online, cron jobs are much easier! The APScheduler package's BackgroundScheduler() should do the trick, so the Flask app can 
  update the database if there are changes to the schedule week to week.
- Provide an Env var that can change the selected team
  - Likely best to map the name to the MLB stats API's team ID
  - Provide a simple deploy button? Railway template?
- Use fixtures to test the database seed + update commands
  - These fixtures can likely be defined within each test file so they can be specific and only provide necessary info
- Drop `requirements.in` in favor of simply embracing `pyproject.toml`
  - Unfortunately, there seems to be some issue with `setuptools`, `wheels`, and `pip-tools` that will hopefully be solved fairly soon!


### Railway
- Similar to Heroku, it should autodetect both the requirements.txt as well as the package.json, and run the needed buildpacks to setup dependencies
  - If Railway only detects one of the buildpacks (Python or NodeJS), then adding the `providers` config option to your `nixpacks.toml` file should add
  any needed buildpacks for monorepos like this one
    - As a bonus, `nixpacks.toml` can define every step (called phases) of the build process if needed! Which can help replicate Heroku's release phase by
    running `flask db upgrade` and seeding the database
- Unlike Heroku, it'll only use the Procfile's web process, reading it as a start command, so it's probably best to drop `Procfile` in favor of a `railway.toml` file
that contains a start command

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
- To run both `Flask` and the `Svelte` app, run `forego start -f Procfile.dev`
  - Alternatively, to see Flask serve a production build run `forego start -f Procfile.devBuild`
  - In order to run Procfiles and the commands inside them, [`forego`](https://github.com/ddollar/forego) is necessary
    - This is the Golang version of the handy-dandy [`foreman`](https://github.com/ddollar/foreman)
      - Why not use `foreman`? `forego` just seems to play along with Mac's system version of Ruby
    - As a bonus, `forego` will grab any `.env` files for you!
  - Why not just use `flask run & npm run dev`? It seems neither Flask, nor Vite like to run in the background, so one command kills the other unless you open two
  separate terminals. At that point, `forego` is a convenient addition for Mac users that use `homebrew` to install packages like `forego`
- Bonus Pip Tip - `pip show 'pypiPkgName'` will display all requirements for that particular package plus the venv location 
and what packages require that package! Super helpful if VSCode doesn't recognize imports
  - For even more tips, see [Pip PyPA](https://pip.pypa.io/en/latest/user_guide/)

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

### Pytest
- To run tests, run `pytest` from the root directory!
  - It also helps to include `-W ignore::DeprecationWarning` to silence warnings commonly out of your control!
    - A `pytest.ini` file can also be used to configure a filter for a number of different warnings by setting the `filterwarnings` key with a list of
    `ignore::someWarning` strings
  - Pytest DOESN'T load env files by default, so it's important to include a fixture that will run before all other fixtures to provide the env
    - Most likely placed in a `conftest.py` file so all tests have your env loaded/included by default
  