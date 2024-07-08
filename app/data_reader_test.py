from data_reader import KnaDB

db = KnaDB(debug=True)

lst_leden = db.lid_media("Mark Zwart") #("Assepoes - 2015")
lst_leden