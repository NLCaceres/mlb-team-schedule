from .. import db

#! Convenience methods for saving, deleting, and committing all changes

def saveToDb(new_model):
    print(f"Saving {new_model} to the database")
    db.session.add(new_model) #? This saves a new model
    finalizeDbUpdate()
    #? To update DB rows, 1st: query using a column like 'name'
    #? THEN using the returned model, set the prop, e.g. row.name = 'newName'
    #? OR, more typically: `row.wins = row.wins + 1`, and run commit on the db session
    #? For mass updates, import update() from sqlalchemy, THEN run `db.session.execute()`
    #? inputting `update(Model).where(Model.name == 'oldName').values(name = 'newName')`
    #? ALSO, `.values({'name':'newName', 'age': 42})` accepts a dict for multiple updates
    print(f"Successfully saved {new_model}!")

def deleteFromDb(model_to_delete):
    print(f"Deleting {model_to_delete} from the database")
    db.session.delete(model_to_delete)
    finalizeDbUpdate()
    print(f"Successfully delete {model_to_delete}")

def finalizeDbUpdate():
    db.session.commit()

