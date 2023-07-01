from flask import Blueprint
import click
from .database_seed import seedDB
from .database_update import updateAllTeamRecords, updateAllPromotions

bp = Blueprint('commands', __name__)

@bp.cli.command('seed')
@click.argument('db')
def seedDb(db):
    if (db == 'db'):
        seedDB() #? Seeds AND updates full schedule
    else: 
        print('Not valid argument')

@bp.cli.command() #? No string param means function name used to call the command function, i.e. 'flask update someArg'
@click.argument('table')
def update(table):
    if table == 'teamRecords':
        updateAllTeamRecords()
    elif table == 'promotions':
        updateAllPromotions()
    elif table == 'schedule':
        seedDB(updateMode=True)
    else: 
        print('Not valid argument')
