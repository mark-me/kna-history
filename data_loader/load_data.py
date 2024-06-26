import pandas as pd

df_leden = pd.read_excel("data_loader/kna_database.xlsx", sheet_name="Leden")
df_media_type = pd.read_excel("data_loader/kna_database.xlsx", sheet_name="Type_Media")
df_uitvoering = pd.read_excel("data_loader/kna_database.xlsx", sheet_name="Uitvoering")
df_files =  pd.read_excel("data_loader/kna_database.xlsx", sheet_name="Bestand")
df_rollen =  pd.read_excel("data_loader/kna_database.xlsx", sheet_name="Rollen")
df_files = df_files.melt(id_vars=['ref_uitvoering', "bestand", "type_media"], var_name='vlnr', value_name='lid').reset_index()
df_files.dropna(subset=["lid"], inplace=True)
df_files.drop(columns=["index"], inplace=True)
df_files.head()