from data_reader import KnaDB

db = KnaDB(dir_resources="/data/kna_resources/", debug=True)

lst_leden = db.lid_media("Mark Zwart") #("Kinderen van ons Volk - 1938") # #"Assepoes - 2015") #
lst_leden