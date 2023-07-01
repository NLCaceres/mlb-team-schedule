from . import create_app

#? When named app.py, a simple `flask run` will start up the app using this file

if __name__ == '__main__':
    app = create_app() #? Configure and construct the app
    app.run(debug=app.config.get('DEBUG'), load_dotenv=True) #? And run it with a few extra param options
