import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from PIL import Image

engine = create_engine("mysql+mysqldb://root:kna-toneel@127.0.0.1:3306/kna")

data_root = "/data/kna_resources/"
file_db = data_root + "kna_database.xlsx"

df_leden = pd.read_excel(file_db, sheet_name="Leden")
# Achternaam sortering, verwijderen tussenvoegsels
df_leden["achternaam_sort"] = ""
tussenvoegsels = ["van der", "van den", "van de", "van", "de", "v.d."]
for index, row in df_leden.iterrows():
    found = False
    i = 0
    while i < len(tussenvoegsels) and not found:
        if pd.isnull(row["Achternaam"]):
            df_leden.loc[index, "achternaam_sort"] = "zzzzzzzz"
            break
        if tussenvoegsels[i] in row["Achternaam"][: len(tussenvoegsels[i])]:
            achternaam_sort = row["Achternaam"].replace(tussenvoegsels[i] + " ", "")
            df_leden.loc[index, "achternaam_sort"] = (
                achternaam_sort + ", " + tussenvoegsels[i]
            )
            found = True
        i = i + 1
    if not found:
        df_leden.loc[index, "achternaam_sort"] = df_leden.loc[index, "Achternaam"]
df_leden.to_sql("lid", con=engine, if_exists="replace", index=False)

df_uitvoering = pd.read_excel(file_db, sheet_name="Uitvoering")
df_uitvoering.rename(columns={"uitvoering": "ref_uitvoering"}, inplace=True)


df_uitvoering_folder = df_uitvoering[["ref_uitvoering", "folder"]]

df_rollen = pd.read_excel(file_db, sheet_name="Rollen")


df_media_type = pd.read_excel(file_db, sheet_name="Type_Media")
df_media_type.to_sql("media_type", con=engine, if_exists="replace", index=False)

df_files = pd.read_excel(file_db, sheet_name="Bestand")
df_files = df_files.merge(right=df_uitvoering_folder, how="left", on="ref_uitvoering")
df_files["file_ext"] = df_files["bestand"].str.split('.').str[-1]
df_files["file_ext"] = df_files["file_ext"].str.lower()

df_files_leden = df_files.melt(
    id_vars=["ref_uitvoering", "bestand", "type_media", "file_ext", "folder"],
    var_name="vlnr",
    value_name="lid",
).reset_index()
df_files_leden.dropna(subset=["lid"], inplace=True)
df_files_leden.drop(columns=["index"], inplace=True)
df_files_leden.to_sql("file_leden", con=engine, if_exists="replace", index=False)

df_files = df_files[df_files.columns.drop(list(df_files.filter(regex="lid_")))]
df_files.to_sql("file", con=engine, if_exists="replace", index=False)

df_uitvoering_regie = df_rollen.loc[df_rollen["rol"] == "Regie"].groupby("ref_uitvoering").agg("max").reset_index()
df_uitvoering_regie = df_uitvoering_regie.drop(["rol", "rol_bijnaam"], axis=1)
df_uitvoering_regie.columns = ["ref_uitvoering", "regie"]
df_uitvoering = df_uitvoering.merge(right=df_uitvoering_regie, how="left", on="ref_uitvoering")
df_uitvoering_files = df_files.groupby("ref_uitvoering").size().reset_index()
df_uitvoering_files.columns = ["ref_uitvoering", "qty_media"]
df_uitvoering = df_uitvoering.merge(right=df_uitvoering_files, how="left", on="ref_uitvoering")
df_uitvoering["qty_media"] = df_uitvoering["qty_media"].fillna(0)
df_uitvoering.to_sql("uitvoering", con=engine, if_exists="replace", index=False)

df_rol_files = df_files_leden.groupby(["ref_uitvoering", "lid"]).size().reset_index()
df_rol_files.columns = ["ref_uitvoering", "id_lid", "qty_media"]
df_rollen = df_rollen.merge(right=df_rol_files, how="left", on=["ref_uitvoering", "id_lid"])
df_rollen["qty_media"] = df_rollen["qty_media"].fillna(0)
df_rollen.to_sql("rol", con=engine, if_exists="replace", index=False)

## Creating thumbnails
for root, dirs, files in os.walk("/data/kna_resources"):
    if "thumbnails" not in root:
        Path(root + "/thumbnails").mkdir(parents=True, exist_ok=True)
        for file in files:
            if any(file.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                image = Image.open(root + "/" + file)
                image.thumbnail((300, 300), Image.LANCZOS)
                image.save(root + "/thumbnails/" + file, quality=95)
