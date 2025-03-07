from ..common_assertions import assertHasLengthOf, assertIsNone, assertIsNotNone
from mlb_team_schedule.utility.team_map import (
    TEAM_TO_ID_MAP, getTeamID, getTeamIdFromName
)


def test_team_to_id_map():
    #? Should have 30 team name keys
    assertHasLengthOf(TEAM_TO_ID_MAP.keys(), 30)

    #* American League West
    assertIsNotNone(TEAM_TO_ID_MAP.get("los angeles angels"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("houston astros"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("oakland athletics"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("seattle mariners"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("texas rangers"))

    #* American League Central
    assertIsNotNone(TEAM_TO_ID_MAP.get("minnesota twins"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("kansas city royals"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("chicago white sox"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("detroit tigers"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("cleveland guardians"))

    #* American League East
    assertIsNotNone(TEAM_TO_ID_MAP.get("new york yankees"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("tampa bay rays"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("boston red sox"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("toronto blue jays"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("baltimore orioles"))

    #* National League West
    assertIsNotNone(TEAM_TO_ID_MAP.get("los angeles dodgers"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("san francisco giants"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("san diego padres"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("arizona diamondbacks"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("colorado rockies"))

    #* National League Central
    assertIsNotNone(TEAM_TO_ID_MAP.get("milwaukee brewers"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("pittsburgh pirates"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("st. louis cardinals"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("chicago cubs"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("cincinnati reds"))

    #* National League East
    assertIsNotNone(TEAM_TO_ID_MAP.get("new york mets"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("philadelphia phillies"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("atlanta braves"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("washington nationals"))
    assertIsNotNone(TEAM_TO_ID_MAP.get("miami marlins"))


def test_getTeamIdFromName():
    #* WHEN an unrecognized team is input THEN None is returned
    assertIsNone(getTeamIdFromName("foobar"))
    #* WHEN a recognized team is input THEN the expected team ID is returned
    #* AL West
    assert getTeamIdFromName("los angeles angels") == 108
    #* AL Central
    assert getTeamIdFromName("cleveland guardians") == 114
    #* AL East
    assert getTeamIdFromName("tampa bay rays") == 139

    #* WHEN the team is misspelled THEN None is returned
    #* NL West
    assertIsNone(getTeamIdFromName("arizon diamondbacks"))

    #* WHEN case is mixed, THEN still get the correct team as long as spelling is correct
    #* NL Central
    assert getTeamIdFromName("sT. LouIs cArDiNaLs") == 138
    #* NL East
    assert getTeamIdFromName("Miami Marlins") == 146


def test_getTeamID(app):
     #? Monkeypatch works BUT turns out app.config is just a Python dictionary subclassing
    # monkeypatch.setattr(app.config, "get", lambda x: 'something')
    with app.app_context():
        #* WHEN an unrecognized team is input THEN None is returned
        app.config["TEAM_FULL_NAME"] = "barfoo" #? So you can change it WHENEVER!
        emptyTeamID = getTeamID()
        assertIsNone(emptyTeamID)

        #* WHEN a recognized team is input THEN the expected team ID is returned
        app.config["TEAM_FULL_NAME"] = "seattle mariners"
        arizonaTeamID = getTeamID()
        assert arizonaTeamID == 136

        #* WHEN the team is misspelled THEN None is returned
        app.config["TEAM_FULL_NAME"] = "chiccago White Sox"
        missingChicagoTeamID = getTeamID()
        assertIsNone(missingChicagoTeamID)

        #* WHEN case mixed, THEN still get the correct team as long as spelling is correct
        app.config["TEAM_FULL_NAME"] = "balTimore oRioles"
        baltimoreTeamID = getTeamID()
        assert baltimoreTeamID == 110

        app.config["TEAM_FULL_NAME"] = "sAn FrAnCiSco gIaNts"
        sfTeamID = getTeamID()
        assert sfTeamID == 137

        app.config["TEAM_FULL_NAME"] = "Pittsburgh Pirates"
        piratesTeamID = getTeamID()
        assert piratesTeamID == 134

        app.config["TEAM_FULL_NAME"] = "New York Mets"
        metsTeamID = getTeamID()
        assert metsTeamID == 121
