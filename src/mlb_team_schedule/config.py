import os

# basedir = os.path.abspath(os.path.dirname(__file__))

#? Despite `dotenv` autoloading Env vars, this config file still helps a ton!
#? It can easily set & get tons of Config Vars that don't necessarily need to be secret
#? The base `Config` class sets common important defaults and the subclasses override them

class Config(object):
    DEBUG = False
    DEVELOPMENT = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ["SECRET_KEY"] # MUST set or app can't run, don't add a default
    TEAM_FULL_NAME = os.getenv("VITE_TEAM_FULL_NAME", "Los Angeles Dodgers")

class ProductionConfig(Config): #TODO: Probably don't need `replace` for Railway
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "").replace("://", "ql://", 1)
    #? Usually would have more production specific vars BUT Railway handles most of it

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL", "")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "")

