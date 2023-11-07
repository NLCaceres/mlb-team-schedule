from datetime import date
from DodgersPromo import db
from DodgersPromo.utility.database_helpers import saveToDb, finalizeDbUpdate
from DodgersPromo.models import DodgerGame, BaseballTeam


def test_saveToDb(app):
    team1 = BaseballTeam(team_name='Foobar', city_name='Barfoo', team_logo='Foo', abbreviation='BF', wins=2, losses=1)
    team2 = BaseballTeam(team_name='Buzz', city_name='Fizz', team_logo='Bar', abbreviation='FB', wins=1, losses=2)
    game = DodgerGame(gameKey=1, date=date.today(), gameNumInSeries=1, gamesInSeries=3, home_team_id=1, away_team_id=2)

    with app.app_context(): #? App Context required to interact with the DB (session.commit() & queries)
        saveToDb(team1)
        saveToDb(team2)
        saveToDb(game)
        allGames = db.session.scalars(db.select(DodgerGame)).all()
        allTeams = db.session.scalars(db.select(BaseballTeam)).all()
        assert len(allGames) == 1
        assert len(allTeams) == 2

def test_finalizeDbUpdate(app):
    team1 = BaseballTeam(team_name='Foobar', city_name='Barfoo', team_logo='Foo', abbreviation='BF', wins=2, losses=1)

    with app.app_context():
        saveToDb(team1)
        teams = db.session.scalars(db.select(BaseballTeam)).all()
        assert len(teams) == 1
        assert teams[0].team_name == 'Foobar'

        teams[0].team_name = 'Fizz'
        finalizeDbUpdate()

        #? Must use .all() here to complete conversion into BaseballTeam List, not simply the iterable ScalarResult
        teams_found = db.session.scalars(db.select(BaseballTeam).filter_by(team_name = 'Fizz')).all()
        assert len(teams_found) == 1
        assert teams_found[0].team_name == 'Fizz'
