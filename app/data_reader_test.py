from data_reader import KnaDB

db = KnaDB(debug=True)

lst_leden = db.voorstelling_fotos("Assepoes - 2015")
lst_leden