import os
# basedir = os.path.abspath(os.path.dirname(__file__))

#? Despite dotenv autoloading, this config file is still useful, since it can easily set and grab a ton of config vars
#? The base Config class sets the basics with defaults while the child classes can override/differentiate

class Config(object):
    DEBUG = False
    DEVELOPMENT = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', '').replace("://", "ql://", 1) #todo the replace is probably not necessary for Railway
    #? Usually would have more production specific vars BUT Railway handles most of it

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', '')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', '')