from data_reader import KnaDB

db = KnaDB(debug=True)

lst_leden = db.voorstelling_media("Hou toch allemaal ff je kop - 2024") #("Anwer Alhussein") #"Assepoes - 2015") #
lst_leden