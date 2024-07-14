from data_reader import KnaDB

db = KnaDB(dir_resources="/data/kna_resources/", debug=True)

lst_leden = db.leden() #("Hou toch allemaal ff je kop - 2024") #("Anwer Alhussein") #"Assepoes - 2015") #
lst_leden