from data_reader import KnaDB

db = KnaDB(dir_resources="/data/kna_resources/", debug=True)

lst_leden = db.medium("/data/kna_resources/2023/Sinefre/330810608_738827544616600_2163554102445074715_n.jpg") #("Hou toch allemaal ff je kop - 2024") #("Anwer Alhussein") #"Assepoes - 2015") #
lst_leden