import binascii
import os

import pandas as pd
from sqlalchemy import create_engine


def encode(x):
    return binascii.hexlify(x.encode("utf-8")).decode()


engine = create_engine("mysql+mysqldb://root:kna-toneel@172.20.0.4/kna")

df_fotos = pd.read_sql(
    sql=f"SELECT * FROM file INNER JOIN uitvoering ON uitvoering.ref_uitvoering = file.ref_uitvoering WHERE lid='Renate Hendriks'",
    con=engine,
)
# print(df_fotos.head())
df_fotos["jaar"] = df_fotos["jaar"].astype("Int64").astype(str)


result = []  # Initialize the result list
grouped_jaar = df_fotos.groupby("jaar")  # Group by 'jaar'
# Iterate over each jaar
for group_jaar, df_jaar in grouped_jaar:
    lst_titel = []
    # Group by 'titel' within each jaar
    grouped_titel = df_jaar.groupby("titel")
    # Iterate over each subgroup
    for group_titel, df_titel in grouped_titel:
        data_list = df_titel.to_dict("records")
        data_list = [
            dict(
                data,
                path=encode(
                    os.path.join(
                        f"/data/resources/{data['folder']}/thumbnails", data["bestand"]
                    )
                ),
            )
            for data in data_list
        ]
        lst_titel.append({"uitvoering": group_titel, "fotos": data_list})
    result.append({"jaar": group_jaar, "uitvoering": lst_titel})

print(result)
