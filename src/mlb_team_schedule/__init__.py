from flask import Flask, render_template
from flask_apscheduler import APScheduler
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os


class Base(DeclarativeBase):
    pass

#? Initing db + migrate here helps re-exporting into other pkgs/dirs & modules/files
db = SQLAlchemy(model_class = Base)
migrate = Migrate(directory = "src/mlb_team_schedule/migrations")
scheduler = APScheduler()

def create_app(test_config = None):
    #? Adding export FLASK_ENV=development and FLASK_DEBUG=True can improve debugging
    app = Flask(__name__, static_folder="dist")

    configure_app(app, test_config)
    scheduler.init_app(app)

    @app.route("/", defaults={"path": ""}) #* Path for the root Svelte page
    @app.route("/<path:path>") #? '<path' sets the var name
    def home(path): #? ':path>' type checks for URLs like 'dir/subDir/subSubDir'
        #? Could use `send_from_directory` to serve straight from Svelte public dir
        #? BUT using flask's Jinja template engine lets you setup the bundled files
        #? AND serve index.html to all requests, so Svelte can handle view routing.
        return render_template("index.html")

    db.init_app(app)
    migrate.init_app(app, db)

    from . import scheduled_jobs  #? Importing this ensures its tasks run
    scheduler.start() #? AFTER BOTH scheduler.start() and app.run() were called

    from . import api
    app.register_blueprint(api.bp)

    from .commands import bp as command_blueprint
    #? `cli_group=None` means no blueprint namespacing required when running command
    app.register_blueprint(command_blueprint, cli_group=None)

    return app

BASE_CONFIG_NAME = "mlb_team_schedule.config"
DEV_CONFIG = f"{BASE_CONFIG_NAME}.DevelopmentConfig"
TESTING_CONFIG = f"{BASE_CONFIG_NAME}.TestingConfig"

def configure_app(app, test_config):
    #? APP_SETTINGS should = 'config.ProductionConfig'
    # BUT Python 3 wants explicit relative imports so prepend `DodgersPromo`
    #TODO: In prod, maybe use `print(os.getcwd().split('/')[-1])` to get root dir name
    default_config = DEV_CONFIG if test_config is None else TESTING_CONFIG
    env_config = os.getenv("APP_SETTINGS", default_config) #? Use dev version as a default
    app.config.from_object(env_config)
    #? To get vars from `config.py` in app, use `app.config.get('envVariableName')`
    if test_config is not None: #? OR use `app.config['envVariableName']`
        app.config.update(test_config)

