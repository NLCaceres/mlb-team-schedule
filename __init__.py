import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#? Setting db and migrate here makes exporting them into other pkgs/dirs & modules/files easier
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    #? Adding export FLASK_ENV=development and FLASK_DEBUG=True can improve debugging
    app = Flask(__name__, static_folder='dist')

    #? APP_SETTINGS should = 'config.ProductionConfig' BUT Python 3 wants explicit relative imports so prepend `DodgersPromo`
    #? In prod, it might be helpful to use `print(os.getcwd().split('/')[-1])` to get the root directory name to prepend
    env_config = os.getenv('APP_SETTINGS', 'DodgersPromo.config.DevelopmentConfig') #? Use dev version as a default
    app.config.from_object(env_config) #? To get configs vars from config.py, use `os.config.get('envVariableName')`

    @app.route('/', defaults={'path': ''}) #* Path for the root Svelte page
    @app.route('/<path:path>') #? '<path' sets the var name. ':path>' type checks for URLs like 'dir/subDir/subSubDir'
    def home(path):
        #? Could use send_from_directory to serve straight from Svelte public dir BUT
        #? Using flask's template engine (Jinja) lets you setup the bundled files AND
        #? serve up that index.html for all requests, letting Svelte do the view routing from there!
        return render_template('index.html')

    db.init_app(app)
    migrate.init_app(app, db)

    return app
