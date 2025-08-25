from .database_seed import seedDB
from .update_promotions import updateAllPromotions
from .update_standings import updateAllTeamRecords

import click
from flask import Blueprint

bp = Blueprint("commands", __name__)

@bp.cli.command("seed")
@click.argument("db")
def seedDb(db):
    if (db == "db"):
        seedDB() #? Seeds AND updates full schedule
    else:
        print("Not valid argument")

@bp.cli.command() #? No string param makes the CLI command name == the func name
@click.argument("table") #? Ex: `flask update someArg`
def update(table):
    if table == "teamRecords":
        updateAllTeamRecords()
    elif table == "promotions":
        updateAllPromotions()
    elif table == "schedule":
        seedDB(updateMode=True)
    else:
        print("Not valid argument")

