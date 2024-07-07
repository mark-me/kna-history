from data_reader import KnaDB

db = KnaDB(debug=True)

lst_leden = db.voorstellingen()
lst_leden