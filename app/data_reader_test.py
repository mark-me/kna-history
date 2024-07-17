from data_reader import KnaDB

db = KnaDB(dir_resources="/data/kna_resources/", debug=True)

lst_leden = db.voorstelling_info("Kinderen van ons Volk - 1938") #("Anwer Alhussein") #"Assepoes - 2015") #
lst_leden