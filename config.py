import os
# basedir = os.path.abspath(os.path.dirname(__file__))

#? Despite dotenv autoloading, this config file is still useful! (since it allows us to easily set and grab a ton of config vars)
#? NOTE: The base Config class can be used to set the basics while the child classes can be used to override/differentiate

class Config(object):
    DEBUG = False
    DEVELOPMENT = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL').replace("://", "ql://", 1) #? Deals with small SQLAlchemy/Heroku incompatibility
    #? Usually would have some sort of prodConfig differentiations/overriden vars BUT heroku handles most of it

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', '') #? Without defaults Heroku release fails

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', '')