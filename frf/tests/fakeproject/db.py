from frf import db


database = db.Database('sqlite://')
database.connect()
session = database.session
