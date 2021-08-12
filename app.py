import os
import click
from calendar import monthrange
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#? When named app.py, `flask run` can be used in the command line
#? Adding export FLASK_ENV=development can improve debugging
app = Flask(__name__, static_folder="public")

#? APP_SETTINGS should = 'config.ProductionConfig', else following defaults to devConfig
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config) #? To get configs vars from config.py, use `os.config.get('envVariableName')`
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #? Will be disabled by default in the future. Useful only if modding DB frequently

db = SQLAlchemy(app)  
migrate = Migrate(app, db)

#? Seems best to put next 2 lines here to avoid a circular dependency since 'models' file needs 'app' & 'db' ready
from seedDB import seedDB, updateAllTeamRecords, updateAllPromotions #? Similarly, this imports 'models' so plan/place imports wisely!
from models import *

#* Flask Custom Commands

@app.cli.command('seed')
@click.argument('db')
def seedDb(db):
    if (db == 'db'):
        seedDB() #? Seeds AND updates full schedule
    else: print("Not valid argument")

@app.cli.command() #? Could include param like above, but no need unless special casing needed
@click.argument('table')
def update(table): 
    if table == 'teamRecordsDb':
        updateAllTeamRecords()
    elif table == 'promotionsDb':
        updateAllPromotions()
    elif table == 'scheduleDb':
        seedDB(updateMode=True)
    else: print("Not valid argument")

#* Flask Routes

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>") #? 1st 'path' is a var name. 2nd sets type checking for url strings like 'dir/subdir/subsubdir')
def home(path):
    #? Could use send_from_directory to serve straight from svelte public dir BUT
    #? Using flask's template engine (Jinja) lets you setup the bundled files AND
    #? serve up that index.html to all URLs, allowing svelte to do the view routing from there!
    return render_template("index.html")

@app.route('/api/fullSchedule')
def apiFullDodgerSchedule():
    if len(request.accept_mimetypes) > 1 or not request.accept_mimetypes.accept_json: return redirect(url_for('home'))

    allGames = DodgerGame.query.all()
    return jsonify([game.asDict for game in allGames])

monthSwitch = { 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10 }
@app.route('/api/<string:month>')
def apiSingleMonthDodgerSchedule(month):
    if len(request.accept_mimetypes) > 1 or not request.accept_mimetypes.accept_json: return redirect(url_for('home'))

    monthNum = 0
    try: 
        monthNum = monthSwitch[month]
    except KeyError:
        return {'message': 'Invalid Month!'}

    start = date(year=2021, month=monthNum, day=1)
    end = date(year=2021, month=monthNum+1, day=1)

    #* For some reason, can't get games on last day of month! So best solution, set end to 1st day of next month with '<'
    dodgerGames = DodgerGame.query.filter(DodgerGame.readableDateTime < end).filter(DodgerGame.readableDateTime >= start)
    return jsonify([game.asDict for game in dodgerGames])
    
@app.route('/api/<string:month>/<int:day>')
def apiSingleDayDodgerSchedule(month, day):
    if len(request.accept_mimetypes) > 1 or not request.accept_mimetypes.accept_json: return redirect(url_for('home'))

    monthNum = 0
    try: 
        monthNum = monthSwitch[month]
    except KeyError:
        return {'message': 'Invalid Month!'}

    lastDayOfMonth = monthrange(year=2021, month=monthSwitch[month])[1] #? Returns tuple (firstDay, lastDay)
    if (day <= 0 or day > lastDayOfMonth):
        return {'message': 'Invalid Month!'}

    start = date(year=2021, month=monthNum, day=day)
    endMonth = monthNum if (day != lastDayOfMonth) else monthNum + 1
    endDay = day + 1 if (day != lastDayOfMonth) else 1
    end = date(year=2021, month=endMonth, day=endDay)

    dodgerGames = DodgerGame.query.filter(DodgerGame.readableDateTime < end).filter(DodgerGame.readableDateTime >= start)
    return jsonify([game.asDict for game in dodgerGames])


#? If extra config needed, can use factory method like below to create the app and start with run()
# def create_app(): #? Without using blueprints defining app routes from within create_app method is only option
#     app = Flask(__name__)

#?    Place env/app config here, just like above!

#     migrate = Migrate(app, db)
#     db.init_app(app) #? In a factory method like this, would likely be importing a DB created in another file

#?    Without using Flask Blueprints, have to create app routes from within the create_app method
#?    BUT I THINK 'with app.app_context():' can help to inject needed context to create routes from outside of create_app BUT still in this file
#     @app.route("/") #* Path for the root Svelte page
#     def base():
#         return send_from_directory('client/public', 'index.html')

#     return app 

if __name__ == "__main__":
    # app = create_app() #? If was using the above factory to create the Flask app object, we'd need this line!
    app.run(debug=app.config.get("DEBUG"), load_dotenv=True)