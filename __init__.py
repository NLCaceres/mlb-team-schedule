import os
from flask import Flask, render_template
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#? Setting db and migrate here makes exporting them into other pkgs/dirs & modules/files easier
db = SQLAlchemy()
migrate = Migrate()
scheduler = APScheduler()

def create_app(test_config = None):
    #? Adding export FLASK_ENV=development and FLASK_DEBUG=True can improve debugging
    app = Flask(__name__, static_folder='dist')

    configure_app(app, test_config)
    scheduler.init_app(app)

    @app.route('/', defaults={'path': ''}) #* Path for the root Svelte page
    @app.route('/<path:path>') #? '<path' sets the var name. ':path>' type checks for URLs like 'dir/subDir/subSubDir'
    def home(path):
        #? Could use send_from_directory to serve straight from Svelte public dir BUT
        #? Using flask's template engine (Jinja) lets you setup the bundled files AND
        #? serve up that index.html for all requests, letting Svelte do the view routing from there!
        return render_template('index.html')

    db.init_app(app)
    migrate.init_app(app, db)

    from . import scheduled_jobs # noqa: F401
    scheduler.start() #? `import scheduled_jobs` ensures its tasks run after BOTH scheduler.start() and app.run() were called

    from . import api
    app.register_blueprint(api.bp)

    from .commands import bp as command_blueprint
    app.register_blueprint(command_blueprint, cli_group=None) #? No CLI group means no need to use blueprint name in command

    return app

BASE_CONFIG_NAME = 'DodgersPromo.config'
DEV_CONFIG = f"{BASE_CONFIG_NAME}.DevelopmentConfig"
TESTING_CONFIG = f"{BASE_CONFIG_NAME}.TestingConfig"

def configure_app(app, test_config):
    #? APP_SETTINGS should = 'config.ProductionConfig' BUT Python 3 wants explicit relative imports so prepend `DodgersPromo`
    #? In prod, it might be helpful to use `print(os.getcwd().split('/')[-1])` to get the root directory name to prepend
    default_config = DEV_CONFIG if test_config is None else TESTING_CONFIG
    env_config = os.getenv('APP_SETTINGS', default_config) #? Use dev version as a default
    app.config.from_object(env_config)
    #? To get the vars from config.py in-app, use `app.config.get('envVariableName')` or `app.config['envVariableName']`
    if test_config is not None:
        app.config.update(test_config)
