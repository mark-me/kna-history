import binascii
from logging_kna import logger
import os

import numpy as np
import pandas as pd
from sqlalchemy import create_engine


class KnaDB:
    def __init__(self, debug: bool = False) -> None:
        if not debug:
            self.engine = create_engine("mysql+mysqldb://root:kna-toneel@mariadb/kna")
        else:
            self.engine = create_engine(
                "mysql+mysqldb://root:kna-toneel@127.0.0.1:3306/kna"
            )

    def encode(self, x):
        return binascii.hexlify(x.encode("utf-8")).decode()

    def decode(self, x):
        return binascii.unhexlify(x.encode("utf-8")).decode()

    def leden(self):
        sql_statement = """
        SELECT *
        FROM lid
        WHERE gdpr_permission = 1 AND
            Achternaam IS NOT NULL
        ORDER BY achternaam_sort"""
        df_lid = pd.read_sql(sql=sql_statement, con=self.engine)
        df_lid["Geboortedatum"] = df_lid["Geboortedatum"].dt.date
        df_lid["Startjaar"] = df_lid["Startjaar"].astype("Int64")
        df_lid["dir_photo"] = (
            "/data/resources/Leden/thumbnails/" + df_lid["id_lid"] + ".png"
        )
        df_lid["photo_exists"] = df_lid["dir_photo"].astype(str).map(os.path.exists)
        df_lid["dir_photo"] = np.where(
            df_lid["photo_exists"], "/data/resources/Leden/thumbnails", "static/images"
        )
        df_lid["file_photo"] = np.where(
            df_lid["photo_exists"],
            df_lid["id_lid"] + ".png",
            "member_photo_default2.png",
        )
        lst_lid = df_lid.to_dict(orient="records")
        lst_lid = [
            dict(
                data,
                profielfoto=self.encode(
                    os.path.join(
                        data["dir_photo"],
                        data["file_photo"],
                    )
                ),
            )
            for data in lst_lid
        ]

        # Uitvoeringen
        sql_statement = """
        SELECT DISTINCT
            u.titel,
            u.jaar,
            u.ref_uitvoering,
            u.auteur,
            r.id_lid
        FROM rol r
        INNER JOIN uitvoering u
        ON r.ref_uitvoering = u.ref_uitvoering
        ORDER BY u.jaar
        """

        # Rollen
        df_rol = pd.read_sql(sql=sql_statement, con=self.engine)

        # Combine to dictionary
        lst_lid = [
            dict(
                lid,
                uitvoeringen=df_rol.loc[df_rol["id_lid"] == lid["id_lid"]].to_dict(
                    orient="records"
                ),
            )
            for lid in lst_lid
        ]
        return lst_lid

    def voorstellingen(self) -> list:
        sql_statement = """
        SELECT *
        FROM uitvoering u
        WHERE `type` = 'Uitvoering'
        ORDER BY jaar DESC
        """
        df_voorstelling = pd.read_sql(sql=sql_statement, con=self.engine)
        df_voorstelling["jaar"] = df_voorstelling["jaar"].astype("Int64")
        sql_statement = "SELECT * FROM file WHERE type_media = 'poster'"
        df_poster = pd.read_sql(sql=sql_statement, con=self.engine)
        sql_statement = """
        SELECT
            r.ref_uitvoering,
            r.id_lid,
            r.rol,
            r.rol_bijnaam,
            l.achternaam_sort
        FROM rol r
        INNER JOIN lid l
        ON l.id_lid = r.id_lid
        WHERE l.gdpr_permission = 1
        ORDER BY l.achternaam_sort
        """
        df_rol = pd.read_sql(sql=sql_statement, con=self.engine)
        lst_voorstelling = df_voorstelling.to_dict(orient="records")
        i = 0
        while i < len(lst_voorstelling):
            dict_poster = df_poster.loc[
                df_poster["ref_uitvoering"] == lst_voorstelling[i]["ref_uitvoering"]
            ].to_dict("records")
            dict_poster = [
                dict(
                    data,
                    path_thumbnail=self.encode(
                        os.path.join(
                            f"/data/resources/{lst_voorstelling[i]['folder']}/thumbnails",
                            data["bestand"],
                        )
                    ),
                )
                for data in dict_poster
            ]
            if len(dict_poster) > 0:
                lst_voorstelling[i]["poster"] = dict_poster[0]
            else:
                lst_voorstelling[i]["poster"] = {
                    "path_thumbnail": self.encode(
                        os.path.join("static/images", "media_type_poster.png")
                    )
                }
            dict_rollen = df_rol.loc[
                df_rol["ref_uitvoering"] == lst_voorstelling[i]["ref_uitvoering"]
            ].to_dict("records")
            lst_voorstelling[i]["rollen"] = dict_rollen
            i = i + 1
        return lst_voorstelling

    def jaren(self) -> list:
        sql_statement = "SELECT * FROM uitvoering"
        df_events = pd.read_sql(sql=sql_statement, con=self.engine)
        lst_events = []
        grouped_jaar = df_events.groupby("jaar")
        # Iterate over each jaar
        for group_jaar, df_event in grouped_jaar:
            data_list = df_event.to_dict("records")
            lst_events.append({"jaar": group_jaar, "events": data_list})
        return lst_events

    def lid_fotos(self, lid: str) -> list:
        sql_statement = f"""
        SELECT *
        FROM file_leden
        INNER JOIN uitvoering
            ON uitvoering.ref_uitvoering = file_leden.ref_uitvoering
        WHERE lid='{lid}'
        """
        df_fotos = pd.read_sql(
            sql=sql_statement,
            con=self.engine,
        )
        df_fotos["jaar"] = df_fotos["jaar"].astype("Int64")
        lst_fotos = []  # Initialize the result list
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
                        path_thumbnail=self.encode(
                            os.path.join(
                                f"/data/resources/{data['folder']}/thumbnails",
                                data["bestand"],
                            )
                        ),
                    )
                    for data in data_list
                    if not data["file_ext"].lower() == "pdf"
                ]
                data_list = [
                    dict(
                        data,
                        path_thumbnail=self.encode(
                            os.path.join(
                                "static/images",
                                "media_type_booklet.png",
                            )
                        ),
                    )
                    for data in data_list
                    if not data["file_ext"].lower() == "pdf"
                ]
                data_list = [
                    dict(
                        data,
                        path_photo=self.encode(
                            os.path.join(
                                f"/data/resources/{data['folder']}",
                                data["bestand"],
                            )
                        ),
                    )
                    for data in data_list
                ]
                lst_titel.append({"uitvoering": group_titel, "fotos": data_list})
            lst_fotos.append({"jaar": group_jaar, "uitvoering": lst_titel})
        return lst_fotos

    def voorstelling_fotos(self, voorstelling: str) -> list:
        sql_statement = f"""
        SELECT
            f.ref_uitvoering,
            f.bestand,
            f.type_media,
            u.folder,
            f.file_ext
        FROM file f
        INNER JOIN uitvoering u
        ON u.ref_uitvoering = f.ref_uitvoering
        WHERE f.ref_uitvoering='{voorstelling}'
        """
        df_fotos = pd.read_sql(sql=sql_statement, con=self.engine)
        df_fotos["type_media"] = df_fotos["type_media"].str.capitalize()
        lst_photos = []  # Initialize the result list
        grouped_media_type = df_fotos.groupby("type_media")
        # Iterate over each jaar
        for group_media_type, df_media in grouped_media_type:
            lst_media = df_media.to_dict("records")
            i = 0
            while i < len(lst_media):
                if lst_media[i]["file_ext"].lower() == "pdf":
                    lst_media[i]["path_thumbnail"] = self.encode(
                        os.path.join(
                            "static/images",
                            "media_type_booklet.png",
                        )
                    )
                elif lst_media[i]["file_ext"].lower() == "mp4":
                    lst_media[i]["path_thumbnail"] = self.encode(
                        os.path.join(
                            "static/images",
                            "media_type_movie.png",
                        )
                    )
                else:
                    lst_media[i]["path_thumbnail"] = self.encode(
                        os.path.join(
                            f"/data/resources/{lst_media[i]['folder']}/thumbnails",
                            lst_media[i]["bestand"],
                        )
                    )
                lst_media[i]["path_photo"] = self.encode(
                    os.path.join(
                        f"/data/resources/{lst_media[i]['folder']}",
                        lst_media[i]["bestand"],
                    )
                )
                i = i + 1
            lst_photos.append({"type_media": group_media_type, "bestanden": lst_media})

        return lst_photos

    def medium(self, path: str) -> dict:
        sql_statement = f"""
        SELECT f.*
        FROM file f
        INNER JOIN uitvoering u
        ON u.ref_uitvoering = f.ref_uitvoering
        WHERE CONCAT(u.folder, "/" , f.bestand) = {path}
        """
        df_file = pd.read_sql(sql=sql_statement, con=self.engine)
        dict_file = df_file.to_dict("records")[0]
        sql_statement = f"""
        SELECT u.folder, f.bestand, f.vlnr, f.lid,
        FROM file_leden f
        INNER JOIN uitvoering u
        ON u.ref_uitvoering = f.ref_uitvoering
        WHERE CONCAT(u.folder, "/" , f.bestand) = {path}
        """
        df_file_leden = pd.read_sql(sql=sql_statement, con=self.engine)
        return dict_file
