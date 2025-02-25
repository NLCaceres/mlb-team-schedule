# Dodgers Promotional Schedule

Even though MLB's site can be a great one stop shop for any and all questions about
the schedules of every team you can think of, I've found that it's pretty rare you
check any other team but your favorite, in my case the Dodgers. Personally, though
the MLB schedule pages are decent, I've found that the site can be pretty slow, will
often stop mid-load, and generally, the list of promotions is not displayed in the
prettiest or most logical fashion. After noticing that the site was actually calling
out to an open stats API, I knew exactly what I'd like to do, make my own version
of it! Thankfully, there's a Python wrapper on Github ([MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI))
that does a great job of explaining how the API endpoints work. Using it as my guide,
I did my best to craft parsing functions and endpoints that would give me exactly
what I needed and nothing else. Once the Flask backend was mostly structured and
laid out, I set myself on learning Svelte for the frontend, which I'd say was quite
the success.

Svelte is an amazing up-and-coming front-end framework that really delivers on the
oh-so-common promise of 'It just works.' Though I did find a few quirks such as the
handling of API calls and reactivity updates a bit odd compared to my other favorite,
Vue, it was absolutely nothing that couldn't be solved with a few well placed debuggers
and console.log, of course. Like any front-end framework, a solid understanding of
its lifecycle and tools fixes all problems, and once I felt comfortable, Svelte didn't
just deliver on a simple setup, but on a speedy development process. Putting together
the Calendar component was a breeze as any sub-components or parent components fell
right into place without the common React problem of messy and never-ending component
files. Additionally, thanks to Svelte's special components and bindings like 'svelte:window'
& 'on:customEvent', it's pretty easy to avoid complicated prop drilling or event
messaging. While I did find myself yearning for helpers like Vue-Router, thanks to
development on SvelteKit, Svelte, itself, will only continue to grow. In the meantime,
I can imagine updating this project for coming baseball seasons to use Svelte's already
excellent store system as a nifty built-in Redux/Vuex replacement.

This project felt like exactly the injection of fun that I think any developer can
use every once and a while, an absolute passion project to get the creative juices
flowing. As with any project, though, every time you reach the expected finish line,
you can't help but think of just one more awesome feature to add, and that is exactly
where I stand today. In the future, I hope not only to add in Svelte's store state
feature to the front-end, but I hope to continue to improve the backend, making it
more flexible and simple to handle any team that someone who cloned this repo could
want. Consequently, I'd also love to create several global.css files that can be
swapped in as a particular team's theme without a single thought, beautifully matching
team colors and logos to every component. Until then, I'm quite proud of this little
Dodger schedule app.

For anyone who finds it, hopefully it helps you as much as it has helped me, and
let me know what you think I should add, thanks!

## Recent Changes

- Updated to Python 3.12 and Flask 3.0
  - Flask-SQLAlchemy to 3.1 improving `models` typing, SQL Schema, & SQLAlchemy queries
- Continued Code Splitting via Python Packaging + Flask's Blueprint pattern
  - Split `app.py` into a `create_app()` focused `__init__.py` file to let `app.py`
  do the final config before launching Flask in the `if __name__ == '__main__'` condition
  - API Routes sit in their own file while various helpers sit in the `utility` folder
    - MLB-Stats API fetch methods
    - MLB-Stats API endpoints
    - Generic API fetch methods
  - Database Seed file split into three command method files, namely Seeder, Promotion
  Updater, and Standings Updater, all run by weekly-scheduled CRON jobs
    - The Seeder now adjusts for the current year, longer season and can adjust schedules
    in updater mode mostly via the `utility` modules
      - Uses the `mlb_api` module to fetch the schedule, then adjusts dates via the
      `utc_to_pt_converters` and `datetime_helpers` modules
      - Once it has parsed the returned JSON into the classes of the `models` directory,
      it saves and updates all records via the `database_helpers`
    - The Updater now split into 2 files for simplicity sake. One handles the Promotions
    List for a team, and the other handles the records of all teams for a given season
      - The Team Records Updater fetches the standings from its URL, parses the JSON
      into the BaseballTeam model, and saves changes to the DB
      - The Promotion Updater, on the other hand, is slightly more complex, borrowing
      from the Seeder to scan the schedule to find changes in a game's Promotions
- Begin adding the ability for a user to change the team from the Los Angeles Dodgers
to one of their choice via the `TEAM_FULL_NAME` config var
  - DodgerGames DB table renamed to BaseballGames reflecting this future change
- BaseballGames & Promos DB tables migrated to track MLB's primary key for games
and offer types for promotions, as well as to clarify the attributes that track the
total number of games in a particular series vs the order of games in the series
- `pip-tools` now ONLY uses `pyproject.toml` for dependency management in `requirements.txt`
- Configured `tests` directory with `Pytest` by adding a fixture to load the `.env`
file as well as a set of `create_app()` oriented fixtures
  - Testing utility methods, i.e. Database, datetime class, and endpoint URL helpers
  - Testing the Updater commands with JSON fixtures monkeypatched in

## Future Changes

- Split the DB seed further into small helper funcs as a part of whole "Seeder" pkg
  - Extract common Database queries into their own `utility` module
  - Extract basic BaseballGame and Promotion creation and replacement/update logic
  - Add a Playoff Scheduler
- The `MLB_API` module should also have a League Standings method
- The Promotions Updater can also use the RemainingSchedule MLB API endpoint
- Use `TEAM_FULL_NAME` env var in the Seeder to fill the Schedule endpoint team ID
- Use fixtures to test the database seed
- Provide a simple deploy button? Railway template?
- Deploy to Railway

### Railway

- Similar to Heroku, it should autodetect both the requirements.txt as well as the
package.json, and run the needed buildpacks to setup dependencies
  - If Railway only detects one buildpack (Python OR NodeJS), then add the `providers`
  option to `nixpacks.toml` to add the needed buildpack if in a monorepo like this
    - ALSO `nixpacks.toml` can define every step AKA phase of your build if needed,
    helping to mimic Heroku's release step to seed the DB via `flask db upgrade`
- Unlike Heroku, Railway ONLY uses the Procfile web process, reading it as the start
command, so best to drop the `Procfile` for a `railway.toml` with a start command

## Workflow

- To run the `Flask` server, it's easiest to use `flask run`
  - It's also possible to run `Flask` like a typical Python program via `python app.py`
  which will run the code in the `if __name__ == "__main__"` block
  - `flask run` with the `python-dotenv` package should load any `.env` files
    - If not, then add `load_dotenv=True` to `app.run()` in `app.py` to fix the issue
- To run both `Flask` and the `Svelte` app, run `hivemind Procfile.dev`
  - Alternatively, to see Flask serve a production build run `hivemind Procfile.devBuild`
  - To run Procfile commands, use [`hivemind`](https://github.com/DarthSim/hivemind)
    - This is a modern and even simpler alternative to [`foreman`](https://github.com/ddollar/foreman)
      - Why not use `foreman`? `hivemind` works even better with `.env` files and
      accepts additional `.env` vars inline, i.e. `PORT=3000 flask run`
  - Why not just use `flask run & npm run dev`? It seems neither Flask, nor Vite
  like to run in the background, so one command kills the other unless you open two
  separate terminals. At that point, `hivemind` is a convenient addition for Mac
  users that use `homebrew` to install packages like `hivemind`

## Created CLI Commands

- Since `Flask` uses Click to make its own commands, it also exposes it for you to
use, making it super easy to create your own CLI commands for all kinds of things!
- This app has a few commands built for updating the database
  - `flask seed db` - Init the DB after Flask-Migrate runs the migrations
  - `flask update scheduleDb` - Update games in DB from today until season end
  - `flask update teamRecordsDb` - Updates standings of teams in DB
  - `flask update promotionsDb` - Updates promotions from today until season end
  - `flask seed db` and `flask update scheduleDb` are most common since the first
  inits the DB + schedule, and the other updates the schedule + team records + promos

### Flask-Migrate

- A useful extension of Flask-SQLAlchemy that uses Alembic to manage your app's migrations
- Useful Commands - MUST set `FLASK_APP` or "--app" to work
  - `flask db init` - Inits + sets up the `migrations` directory
  - `flask db migrate` - Add migration to `migrations/versions` with model changes
    - Since Alembic isn't perfect, ALWAYS double check the DB changes it generates
  - `flask db upgrade` - Run any new migrations on your DB
    - `flask db downgrade` - Rollback the last migration you've run
  - WORKFLOW: Run `db init` once! Run `db migrate` + `db upgrade` every new migration
  - If using "src-layout", MUST set `Migrate(directory='src/<project-name>/migrations')`
  for any commands to work. Can use `flask db check` to be sure everything is correct

### Notes on Seeding & the MLB-Stats API

- Games seem easiest to identify with the API `gamePk` JSON key BUT the `date` and
`promotions` also act as good markers
  - If game rescheduled `gamePk` stays the same, so good target to simplify the Seeder
  - Giveaway + ticket promos seem to follow their games if rescheduled
    - Other promos like fireworks move entirely, so not reliable markers
    - Using `set` helps update unique promos in the DB during Seeder update mode
  - Dates are good markers to track rescheduling since the 1st date is saved in JSON
    - If delayed, the API may add a `description` or `statusCode` to note it
    - If suspended across 2 days (e.g. rained out), the game gets a `resumeDate`
    while the next day adds a game with a `resumeFrom` key with yesterday's date
    - Similarly, if fully postponed to later in the season, the game adds a  `rescheduleDate`
    and the DB adds a new game with a `rescheduledFrom` key noting the 1st date
      - Any normal games after the postponed one decrement `gamesInSeries` & `seriesGameNumber`
      by 1, and some future series increments those keys by 1
    - Moving up a game may occur if anticipating rain, and updates the `description`
      - ALSO `seriesGameNumber` may change between games, i.e. 2 to 3 and vice versa
- Double headers change `totalGames` to 2 for a given `date` with the `games` list
adding a game with `gameNumber: 1` at index 0, and `gameNumber: 2` at index 1
  - Games in `games` key MAY update `doubleHeader` from 'N' to 'S' but unclear why
  - Triple-headers NEVER happen (last in 1920), so no worries

### Python 3's Virtual Environments

- `python3 -m venv venv` creates a new `venv` directory where `pip` installs dependencies
- `. venv/bin/activate` enters the virtual env with its isolated Python & `pip`
  - `source venv/bin/activate` works as well
    - See [Real Python](https://realpython.com/python-virtual-environments-a-primer/)
    or [Pip & Venvs](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
  - `which pip` and `which python` SHOULD point to the `venv` directory if active
  - `venv` hardcodes your project location, so re-build it if needed for any change
    - Ex: Moving your project location or updating the Python version via `pyenv`
- `python -m pip install -r requirements.txt` gets all dependencies if setup properly
  - `requirements.txt` is like `package.json` BUT a simple list of pkgs with versioning
  - `pip-tools` makes this even easier via `pip-sync` with `requirements.txt`
- If using VSCode, change its Python Interpreter in the bottom bar to match the `venv`

### Pytest

- To run tests, run `python -m pytest` from the root directory!
  - Append `tests/<sub-pkg>` to run only specific test files
    - Appending `<file_name.py>` runs a specific file
    - Appending `<file_name.py::test_func_name>` runs a specific test in a file
  - Include `-W ignore::DeprecationWarning` to silence warnings
    - OR add a list of `ignore::someWarning` strings `filterwarnings` to `tool.pytest.ini_options`
    in `pyproject.toml` to add filters for any warning types
  - MUST run in `-m` module mode to properly test with the new "src-layout" & "importlib"
    - Also MUST have main pkg installed editably, i.e. `pip install -e .`
      - ONLY need to be re-installed if metadata changes, i.e. versioning or generated-scrips
  - DOESN'T load env files, so MUST add a fixture before all others to get env vars
    - Should put into `conftest.py` so all tests load env by default
  - For extra debug help, use the `-rP` flag to capture output of all passing tests
    - Conversely, the `-rx` flag captures output of failed tests (the `pytest` default)

### Bonus Pip Tips

- `python -m pip` followed by any `pip` command is considered good usage of `pip`
  (and any other venv-installed packages) because `python -m` runs `pip` in module
  mode, guaranteeing the correct installation will be used by appending the correct
  system path, which in local development should be your `venv` installed packages
  - `pip list -o` - Display all outdated packages and their latest version
  - `pip show 'pypiPkgName'` - Display all of this package's dependencies + its location
  in `venv` + what packages require this package
  - For more info, see [Pip PyPA](https://pip.pypa.io/en/stable/user_guide/)
  and [Pip CLI](https://pip.pypa.io/en/stable/cli/)
  - `pip-tools` provides `pip-compile` & `pip-sync` for easier dependency management
    - `pip-compile` takes a dependency list with semantic versioning from a `pyproject.toml`
    or `requirements.in` file to generate a well-organized `requirements.txt`
      - `pip-compile --upgrade` CHECKS for the latest version of all dependencies,
      then updates the `requirements.txt` based on their semantic versioning
        - Instead of `--upgrade`, `--upgrade-package` or `-P` can be used to individually
        upgrade dependencies in `requirements.txt` for fine-grained control of `pip-sync`
          - Ex: `pip-compile --upgrade-package 'Flask>2.5'`
    - `pip-sync` runs the actual new version installations from `requirements.txt`
      - In effect, it works as `pip install`, like `python3 -m pip install SomePkg`
    - For dev dependencies:
      - `pip-compile --extra dev -o requirements-dev.txt`, i.e. appends dev dependencies
      - `pip-sync requirements.txt requirements-dev.txt`, i.e. need both files
