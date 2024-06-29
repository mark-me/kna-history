import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from PIL import Image

""" engine = create_engine("mysql+mysqldb://root:kna-toneel@127.0.0.1:3306/kna")

df_leden = pd.read_excel("data_loader/kna_database.xlsx", sheet_name="Leden")
df_leden.to_sql("lid", con=engine, if_exists="replace", index=False)

df_uitvoering = pd.read_excel("data_loader/kna_database.xlsx", sheet_name="Uitvoering")
df_uitvoering.rename(columns={"uitvoering": "ref_uitvoering"}, inplace=True)
df_uitvoering.to_sql("uitvoering", con=engine, if_exists="replace", index=False)

df_rollen = pd.read_excel("data_loader/kna_database.xlsx", sheet_name="Rollen")
df_rollen.to_sql("rol", con=engine, if_exists="replace", index=False)

df_media_type = pd.read_excel("data_loader/kna_database.xlsx", sheet_name="Type_Media")
df_media_type.to_sql("media_type", con=engine, if_exists="replace", index=False)

df_files = pd.read_excel("data_loader/kna_database.xlsx", sheet_name="Bestand")
df_files = df_files.melt(
    id_vars=["ref_uitvoering", "bestand", "type_media"],
    var_name="vlnr",
    value_name="lid",
).reset_index()
df_files.dropna(subset=["lid"], inplace=True)
df_files.drop(columns=["index"], inplace=True)
df_files.to_sql("file", con=engine, if_exists="replace", index=False) """


## Creating thumbnails

for root,dirs,files in os.walk("/data/kna_resources"):
    if not root.contains("thumbnails"):
        Path(root + "/thumbnails").mkdir(parents=True, exist_ok=True)
        for file in files:
            if any(file.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                image = Image.open(root + "/" + file)
                image.thumbnail((200, 200))
                image.save(root + "/thumbnails/" + file)
