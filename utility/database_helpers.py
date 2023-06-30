from ..app import db

#? Just a slightly simpler db save method (delete could and does look similar)
def saveToDb(newModel):
    print(f"Saving {newModel} to the database")
    db.session.add(newModel) #? This saves a new model
    finalizeDbUpdate()
    #? To update, query using a column like 'name', then using the returned model, set the prop, e.g. row.name = 'newName'
    #? Or, for a more concrete example, `row.wins = row.wins + 1`, and run commit on the db session
    #? Could also use `Model.query.filter_by(name='oldName').update({ name='newName' })` which helps for mass updates
    print(f"Successfully saved {newModel}!")

def finalizeDbUpdate():
    db.session.commit()
