from mlb_team_schedule import db
from mlb_team_schedule.models import BaseballGame, BaseballTeam
from mlb_team_schedule.utility.database_helpers import finalizeDbUpdate, saveToDb

from datetime import date


def test_saveToDb(app):
    team1 = BaseballTeam(team_name="Foobar", city_name="Barfoo", team_logo="Foo",
                         abbreviation="BF", wins=2, losses=1)
    team2 = BaseballTeam(team_name="Buzz", city_name="Fizz", team_logo="Bar",
                         abbreviation="FB", wins=1, losses=2)
    game = BaseballGame(gameKey=1, date=date.today(), seriesGameNumber=1,
                        seriesGameCount=3, home_team_id=1, away_team_id=2)

    with app.app_context(): #? App Context needed to use the DB for queries + updates
        saveToDb(team1)
        saveToDb(team2)
        saveToDb(game)
        allGames = db.session.scalars(db.select(BaseballGame)).all()
        allTeams = db.session.scalars(db.select(BaseballTeam)).all()
        assert len(allGames) == 1
        assert len(allTeams) == 2


def test_finalizeDbUpdate(app):
    team1 = BaseballTeam(team_name="Foobar", city_name="Barfoo", team_logo="Foo",
                         abbreviation="BF", wins=2, losses=1)

    with app.app_context():
        saveToDb(team1)
        teams = db.session.scalars(db.select(BaseballTeam)).all()
        assert len(teams) == 1
        assert teams[0].team_name == "Foobar"

        teams[0].team_name = "Fizz"
        finalizeDbUpdate()

        #? Need `all()` to convert into list[BaseballTeam] & not an iterable ScalarResult
        teams_found = db.session \
            .scalars(db.select(BaseballTeam).filter_by(team_name = "Fizz")).all()
        assert len(teams_found) == 1
        assert teams_found[0].team_name == "Fizz"
