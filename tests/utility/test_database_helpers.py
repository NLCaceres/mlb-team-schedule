from datetime import date
from DodgersPromo.utility.database_helpers import saveToDb, finalizeDbUpdate
from DodgersPromo.models import DodgerGame, BaseballTeam

def test_saveToDb(app):
    team1 = BaseballTeam(team_name='Foobar', city_name='Barfoo', team_logo='Foo', abbreviation='BF', wins=2, losses=1)
    team2 = BaseballTeam(team_name='Buzz', city_name='Fizz', team_logo='Bar', abbreviation='FB', wins=1, losses=2)
    game = DodgerGame(date=date.today(), gameNumInSeries=1, gamesInSeries=3, home_team_id=1, away_team_id=2)

    with app.app_context(): #? App Context required to interact with the DB (session.commit() & queries)
        saveToDb(team1)
        saveToDb(team2)
        saveToDb(game)
        allGames = DodgerGame.query.all()
        allTeams = BaseballTeam.query.all()
        assert len(allGames) == 1
        assert len(allTeams) == 2

def test_finalizeDbUpdate(app):
    team1 = BaseballTeam(team_name='Foobar', city_name='Barfoo', team_logo='Foo', abbreviation='BF', wins=2, losses=1)

    with app.app_context():
        saveToDb(team1)
        teams = BaseballTeam.query.all()
        assert len(teams) == 1
        assert teams[0].team_name == 'Foobar'

        teams[0].team_name = 'Fizz'
        finalizeDbUpdate()

        teams_found = BaseballTeam.query.filter_by(team_name = 'Fizz').all()
        assert len(teams_found) == 1
        assert teams_found[0].team_name == 'Fizz'
