# Dodgers Promotional Schedule
Even though MLB's site can be a great one stop shop for any and all questions about the schedules of every team you can think of, I've found that
it's pretty rare you check any other team but your favorite, in my case the Dodgers. Personally, though the MLB schedule pages are decent, I've found
that the site can be pretty slow, will often stop mid-load, and generally, the list of promotions is not displayed in the prettiest or most logical fashion.
After noticing that the site was actually calling out to an open stats API, I knew exactly what I'd like to do, make my own version of it! Thankfully,
there's a Python wrapper on github ([MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI)) that does a great job of explaining how the API endpoints work.
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

For anyone who finds it, hopefully it helps you as much as it has helped me, and let me know what you think I should add, thanks!

## Recent Changes
- Updated to Python 3.12 and Flask 3.0
  - Also update to Flask-SQLAlchemy 3.1 to improve `models` classes typing, SQL Schema, and SQLAlchemy queries
- Continued Code Splitting via Python Packaging + Flask's Blueprint pattern
  - Split `app.py` into a `create_app()` oriented `__init__.py` file, allowing `app.py` to do the final configuration before launching
  Flask in the `if __name__ == '__main__'` condition
  - API Routes sit in their own file while various helpers sit in the `utility` folder
    - MLB-Stats API fetch methods
    - MLB-Stats API endpoints
    - Generic API fetch methods
  - Database Seed file split into three command method files, namely Seeder, Promotion Updater, and Standings Updater, all run by weekly-scheduled CRON jobs
    - The Seeder now adjusts for the current year, longer season and can adjust schedules in updater mode. Heavily dependent on all `utility` modules
      - Uses the `mlb_api` module to fetch the schedule, then adjusts dates via the `utc_to_pt_converters` and `datetime_helpers` modules
      - Once it has parsed the returned JSON into the classes of the `models` directory, it saves and updates all records via the `database_helpers`
    - The Updater has been split into two files for simplicity sake, one handling the Promotions List for a team, and the other 
    that handles the records of all teams during a given season
      - The Team Records Updater fetches the standings from its URL, parses the JSON into the BaseballTeam model, and saves changes to the DB
      - The Promotion Updater, on the other hand, is slightly more complicated borrowing from some of the Seeder's methods to go
      through the schedule and find changes to each game's Promotions
- Begin adding the ability for a user to change the team from the Los Angeles Dodgers to one of their choice via the `TEAM_FULL_NAME` config var
  - DodgerGames DB Table renamed via migration to BaseballGames to reflect this future change
- BaseballGames and Promos DB Tables updated via migrations to keep track of MLB's primary key for games and offer types for promotions, as well as
to clarify the attributes that track the total number of games in a particular series vs the order of games in the series
- `pyproject.toml` + `pip-tools` added to generate `requirements.txt` via `requirements.in` for better dependency management
- Configured `tests` directory with `Pytest` by adding a fixture to load the `.env` file as well as a set of `create_app()` oriented fixtures
  - Added tests for utility methods, i.e. Database, datetime class, and endpoint URL helpers
  - Added tests for the Updater commands with JSON fixtures monkeypatched in


## Future Changes
- Continue splitting the database seed into smaller helper methods so it becomes more its own single purpose module
  - Extract common Database queries into their own `utility` module
  - Extract basic BaseballGame and Promotion creation and replacement/update logic
  - Add a Playoff Scheduler
- The `MLB_API` module should also have a League Standings method
- The Promotions Updater can also use the RemainingSchedule MLB API endpoint
- Tie the `TEAM_FULL_NAME` config var into the Database Seeder so it can fill the MLB API Schedule endpoint with the correct team ID
- Use fixtures to test the database seed
- Provide a simple deploy button? Railway template?
- Drop `requirements.in` in favor of simply embracing `pyproject.toml`
  - Unfortunately, there seems to be some issue with `setuptools`, `wheels`, and `pip-tools` that will hopefully be solved once `pip-tools` switches to
  the `wheels` standard output logger, which should unveil any issues with the `pyproject.toml` file
- Deploy to Railway


### Railway
- Similar to Heroku, it should autodetect both the requirements.txt as well as the package.json, and run the needed buildpacks to setup dependencies
  - If Railway only detects one of the buildpacks (Python or NodeJS), then adding the `providers` config option to your `nixpacks.toml` file should add
  any needed buildpacks for monorepos like this one
    - As a bonus, `nixpacks.toml` can define every step (called phases) of the build process if needed! Which can help replicate Heroku's release phase by
    running `flask db upgrade` and seeding the database
- Unlike Heroku, it'll only use the Procfile's web process, reading it as a start command, so it's probably best to drop `Procfile` in favor of a `railway.toml` file
that contains a start command

## Workflow
- To run the `Flask` server, it's easiest to use `flask run`
  - It is also possible to run `Flask` like a typical Python program via `python app.py` which will run the code in the `if __name__ == "__main__"` block
  - `flask run` alongside with the `python-dotenv` package should load any `.env` files
    - If it doesn't, then adding `load_dotenv=True` to the app.run method in `app.py` fixes this issue
- To run both `Flask` and the `Svelte` app, run `hivemind Procfile.dev`
  - Alternatively, to see Flask serve a production build run `hivemind Procfile.devBuild`
  - In order to run Procfiles and the commands inside them, [`hivemind`](https://github.com/DarthSim/hivemind) is necessary
    - This is a modern and even simpler alternative to [`foreman`](https://github.com/ddollar/foreman)
      - Why not use `foreman`? `hivemind` works even better with `.env` files and accepts additional `.env` vars inline with the command, i.e. `PORT=3000 flask run`
  - Why not just use `flask run & npm run dev`? It seems neither Flask, nor Vite like to run in the background, so one command kills the other unless you open two
  separate terminals. At that point, `hivemind` is a convenient addition for Mac users that use `homebrew` to install packages like `hivemind`

## Created CLI Commands
- Since `Flask` uses Click to make its own commands, it also exposes it for you to use, making it super easy to create your own CLI commands for all kinds of things!
- This app has a few commands built for updating the database
  - `flask seed db` -> Simply inits the database (once Flask-Migrate has done the proper migrations of course)
  - `flask update scheduleDb` -> Updates any games in database with date from now to end of season
  - `flask update teamRecordsDb` -> Updates standings of teams in database using MLB-Stats API
  - `flask update promotionsDb` -> Updates promotions from current date to end of season
  - `flask seed db` and `flask update scheduleDb` are the most used since the first creates the database and schedule while the other updates
  the schedule and runs the team records and promotions updaters

### Flask-Migrate
- A useful extension of Flask-SQLAlchemy that uses Alembic to manage your app's migrations
- Useful Commands
  - `flask db init` -> Creates and sets up the `migrations` directory
    - FLASK_APP, which defaults to app or wsgi, env var needs to be properly set up to be sure work above command works
  - `flask db migrate` -> Create a migration file inside `migrations/versions` that's based on your models
    - Since Alembic isn't perfect, ALWAYS double check the DB changes it generates
  - `flask db upgrade` -> Run any new migrations on your DB
    - `flask db downgrade` -> To rollback the last migration you've run
  - WORKFLOW NOTE: `db init` is only run once! `db migrate` + `db upgrade` is generally run every time you need to make migration changes

### Notes on Seeding & the MLB-Stats API
- Games seem to be most easily identifiable using the API's `gamePk` JSON key BUT the `date` and `promotions` also provide indicators
  - No matter if a game is rescheduled the `gamePk` remains the same, so this is the best target for simplifying the seed command
  - Giveaway and Ticketed Promotions seem to follow their games if they're rescheduled. Other types of promotions, like fireworks 
  or music, can get moved to other games entirely so they're not reliable markers. Leveraging the power of sets should lead to
  an easier way to update the promotions list of each game when the seed command runs in update mode
  - Game dates are good indicators across reschedules in that the date is commonly saved in the rescheduled dates JSON
    - If a game is delayed, then it may get a `description` key noting it or a `statusCode` indicating a delay
    - If a game is suspended across two days (e.g. weather is bad), then the game will remain in the DB but get a `resumeDate`
    meanwhile the next day will get a new game added that has a `resumedFrom` key with the previous day's date inserted.
    - Similarly, if a game is seriously postponed to a later part of the season, then the original game sits in the DB and gets a `rescheduleDate` 
    containing the new date and time while the future game is added into the DB with its new date and a `rescheduledFrom` key noting the original date
      - Games in the series after the postponed one seem to be the only ones that receive updates to the `gamesInSeries` and
      `seriesGameNumber` keys where each drops by 1 meanwhile some other future series will gain 1 in those keys
    - If a game is moved up, like when anticipating rainy weather, then this is usually only reflected in a `description` key as a message
    indicating that `This game was from moved up from another date` citing a specific date
      - This may also cause the `seriesGameNumber` key to change because a game scheduled for a Sunday may become an early Saturday game making
      its value go from '3' to '2' while the original Saturday night game becomes game '3' instead of '2'
- Double headers seem to differ only slightly, namely their `date` JSON updates its `totalGames` key to 2 while their `games` key
becomes a two-item list where the game at index 0 is `gameNumber: 1` while the game at index 1 is `gameNumber: 2`
  - The games in the `games` key may get an update to their `doubleHeader` key from 'N' to 'S' but this doesn't always seem
  to happen, so it's unclear what exactly the letters are supposed to indicate
  - Triple-headers are extremely rare (last one was in 1920) so won't need to worry about it

### Python 3's Virtual Environments
- Enter the directory on the terminal and use `python3 -m venv venv` to create a new `venv` directory where you'll install dependencies via its `pip` install
- `. venv/bin/activate` will switch into that virtual environment, with the proper version of Python as well as `pip`, so you can be in a nicely 
isolated package environment, just like a node_modules folder would provide to a Node project
  - `source venv/bin/activate` also works! See [Real Python](https://realpython.com/python-virtual-environments-a-primer/) or
  [PyPA](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) for more info!
  - Can use `which pip` and `which python` to be sure it's using the `venv` directory versions
    - A triple check would be to run `python3 -m pip list` which should list all packages from your `requirements.txt`
  - If the incorrect `pip` or Python is listed, then it's worth checking the activate script inside of `venv/bin`, especially
  if you've changed the name of your parent folder
    - You can fix this by directly altering the activate script BUT it's much easier to run `python3 -m venv venv --clear` to hard reset the `venv` folder
- If you have a `requirements.txt` file filled with the dependencies for your project, just run `python -m pip install -r requirements.txt`,
and your virtual environment will be all set to use
  - `requirements.txt` acts just like a `package.json` file but without a fancy format, just list the names of packages you want with semantic versioning,
  and `pip` should know what to install with a version that matches the range you listed.
- When updating the Python version, do not use `python -m venv --upgrade venv`. Instead, it's simpler to use the `--clear` flag like shown above once you've
installed the new version of Python you want. The reset venv folder will store a new updated version of Python, and the only package left will be `pip`.
  - Using Pyenv is preferred since it can auto-switch to the updated version of Python via a `.python-version` file placed in the root
  - Using `pip-tools`, it's super easy to use `pip-sync` with your `requirements.txt` file (after a `pip-compile --upgrade` if desired), and you'll be all
  set with your dependencies again!
- When using VirtualEnvs, be sure to change VSCode's Python Interpreter in the bottom bar so it detects the installed dependencies in the `venv` folder.
Changing this setting to `venv/bin/python` will let Pylance provide much better IntelliSense

### Pytest
- To run tests, run `pytest` from the root directory!
  - It also helps to include `-W ignore::DeprecationWarning` to silence warnings commonly out of your control!
    - A `pytest.ini` file can also be used to configure a filter for a number of different warnings by setting the `filterwarnings` key with a list of
    `ignore::someWarning` strings
  - Pytest DOESN'T load env files by default, so it's important to include a fixture that will run before all other fixtures to provide the env
    - Most likely placed in a `conftest.py` file so all tests have your env loaded/included by default
  - For extra debug help, use the '-rP' flag to capture output of all passing tests
    - Conversely, capturing output of failed tests (which `pytest` does by default) would use the '-rx' flag

### Bonus Pip Tips!
- `python -m pip` followed by any `pip` command is considered good usage of `pip` (and any other installed packages in your virtual environment)
  since the `python -m` command runs `pip` in module mode, guaranteeing the correct installation will be used by appending the correct system path,
  which in local development should be your `venv` installed packages
  - `pip list -o` will display all outdated packages and their latest version
  - `pip show 'pypiPkgName'` will display all requirements for that particular package plus the `venv` location and what packages require that package!
  Super helpful if VSCode doesn't recognize imports
  - For even more tips, see [Pip PyPA](https://pip.pypa.io/en/stable/user_guide/) and [Pip CLI](https://pip.pypa.io/en/stable/cli/)
  - `pip-tools` is a super helpful set of command line tools to simplify Python dependency management by providing the `pip-compile` and `pip-sync` commands
    - `pip-compile` takes a list of dependencies and their semantic versioning from a `pyproject.toml` or `requirements.in` file and generates a very clean
    and well-organized `requirements.txt` file
      - `pip-compile --upgrade` checks for the latest version number for all dependencies and sub-dependencies and rewrites the `requirements.txt` file
      based on your `pyproject.toml` or `requirements.in` file's dependency semantic versioning
        - Instead of the `--upgrade` flag, `--upgrade-package` flag (shorthand = `-P`) can be used to individually upgrade packages to your `requirements.txt`, so
        the next `pip-sync` that gets run doesn't install any unwanted updates
      - Currently, using `pip-compile --upgrade requirements.in` for the normal set of dependencies and `pip-compile --upgrade requirements-dev.in` for
      the development only packages (like `pytest`)
        - To install individual packages, run `pip-compile --upgrade-package Flask requirements.in`. If semantic versioning preferred, you can
        use quotation marks in the command, i.e. `pip-compile -P 'Flask>2.3' requirements.in`
    - `pip-sync`, on the other hand, actually runs the dependency installations and updates to match the newly created `requirements.txt`
      - In effect, this does the job of your typical `pip install` command like `python -m pip install SomePackage AnotherPkg SomeOtherPkg` or
      `python -m pip install -r requirements.txt`
    - To handle dev requirements:
      - `pip-compile` uses `requirements-dev.in` instead of `requirements.in`
      - `pip-sync` just uses both files in one command i.e. `pip-sync requirements.txt requirements-dev.txt` installing all dependencies it finds