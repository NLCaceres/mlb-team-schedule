from .. import db

#! Convenience methods for saving, deleting, and committing all changes

def saveToDb(new_model):
    print(f"Saving {new_model} to the database")
    db.session.add(new_model) #? This saves a new model
    finalizeDbUpdate()
    #? To update, query using a column like 'name', then using the returned model, set the prop, e.g. row.name = 'newName'
    #? Or, for a more concrete example, `row.wins = row.wins + 1`, and run commit on the db session
    #? For mass updates, import update() from sqlalchemy,
    #? THEN `db.session.execute(update(Model).where(Model.name == 'oldName').values(name = 'newName'))`
    #? Alternatively, a dictionary can be used in .values({'name':'newName', 'age': 42}) for multiple prop/column updates
    print(f"Successfully saved {new_model}!")

def deleteFromDb(model_to_delete):
    print(f"Deleting {model_to_delete} from the database")
    db.session.delete(model_to_delete)
    finalizeDbUpdate()
    print(f"Successfully delete {model_to_delete}")

def finalizeDbUpdate():
    db.session.commit()
