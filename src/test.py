import binascii

import pandas as pd
from sqlalchemy import create_engine


def encode(x):
    return binascii.hexlify(x.encode("utf-8")).decode()


engine = create_engine("mysql+mysqldb://root:kna-toneel@172.22.0.6/kna")

sql_statement = "SELECT * FROM file"
df_fotos = pd.read_sql(sql=sql_statement,con=engine)

result = []  # Initialize the result list
grouped_media_type = df_fotos.groupby("type_media")
# Iterate over each jaar
for group_media_type, df_media in grouped_media_type:
    data_list = df_media.to_dict("records")
    # Iterate over each subgroup
    result.append({"type_media": group_media_type, "bestanden": data_list})

print(result)
