import binascii
import os

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from logging_kna import logger

class KnaDB:
    def __init__(self, debug: bool = False) -> None:
        if not debug:
            self.engine = create_engine("mysql+mysqldb://root:kna-toneel@mariadb/kna")
        else:
            self.engine = create_engine(
                "mysql+mysqldb://root:kna-toneel@127.0.0.1:3306/kna"
            )

    def encode(self, folder, file) -> str:
        logger.info(f"Encode - {folder}, {file}")
        path = os.path.join(folder, file)
        logger.info(f"Encode path - {path}")
        path = binascii.hexlify(path.encode("utf-8")).decode()
        return path

    def decode(self, x) -> str:
        logger.info(f"Decode - {x}")
        return binascii.unhexlify(x.encode("utf-8")).decode()

    def enrich_media(self, df_media: pd.DataFrame) -> pd.DataFrame:
        df_media["dir_thumbnail"] = "/data/resources/" + df_media['folder'] + "/thumbnails"
        df_media["dir_media"] = "/data/resources/" + df_media['folder']
        df_media.loc[df_media["file_ext"].isin(["pdf", "mp4"]), "dir_thumbnail"] = (
            "static/images"
        )
        df_media["file_thumbnail"] = df_media["bestand"]
        df_media.loc[df_media["file_ext"] == "pdf", "file_thumbnail"] = (
            "media_type_booklet.png"
        )
        df_media.loc[df_media["file_ext"] == "mp4", "file_thumbnail"] = (
            "media_type_video.png"
        )
        logger.info("Encoding while enriching dataframe")
        df_media["path_thumbnail"] = df_media.apply(
            lambda x: self.encode(x["dir_thumbnail"], x["file_thumbnail"]), axis=1
        )
        df_media["path_media"] = df_media.apply(
            lambda x: self.encode(x["dir_media"], x["bestand"]), axis=1
        )
        df_media["type_media"] = df_media["type_media"].str.capitalize()
        return df_media

    def leden(self):
        sql_statement = """
        SELECT
            l.id_lid,
            l.Voornaam,
            l.Achternaam,
            l.Geboortedatum,
            l.Startjaar,
            l.achternaam_sort,
            COUNT(fl.bestand) AS qty_media
        FROM lid l
        LEFT JOIN file_leden fl
        ON fl.lid = l.id_lid
        WHERE l.gdpr_permission = 1 AND
            l.Achternaam IS NOT NULL
        GROUP BY
            l.id_lid,
            l.Voornaam,
            l.Achternaam,
            l.Geboortedatum,
            l.Startjaar,
            l.achternaam_sort
        ORDER BY l.achternaam_sort"""
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
        df_lid["profielfoto"] = df_lid.apply(
            lambda x: self.encode(x["dir_photo"], x["file_photo"]), axis=1
        )

        # Has media
        sql_statement = """

        """

        lst_lid = df_lid.to_dict(orient="records")

        # Rollen
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
        df_rol = pd.read_sql(sql=sql_statement, con=self.engine)

        # Integrate into dictionary
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
        # Voorstellingen
        sql_statement = """
        SELECT *
        FROM uitvoering u
        WHERE `type` = 'Uitvoering'
        ORDER BY jaar DESC
        """
        df_voorstelling = pd.read_sql(sql=sql_statement, con=self.engine)
        df_voorstelling["jaar"] = df_voorstelling["jaar"].astype("Int64")
        # Poster
        sql_statement = """
        SELECT u.ref_uitvoering,
            u.folder AS dir_poster,
            MAX(f.bestand) as file_poster
        FROM uitvoering u
        LEFT JOIN file f
        ON f.ref_uitvoering = u.ref_uitvoering
        WHERE f.type_media = 'poster'
        GROUP BY
            u.ref_uitvoering,
            u.folder"""
        df_poster = pd.read_sql(sql=sql_statement, con=self.engine)
        df_poster["dir_poster"] = (
            "/data/resources/" + df_poster["dir_poster"] + "/thumbnails"
        )
        # Add poster to voorstelling
        df_voorstelling = df_voorstelling.merge(
            right=df_poster, how="left", on="ref_uitvoering"
        )
        del df_poster
        df_voorstelling["dir_poster"] = df_voorstelling["dir_poster"].fillna(
            "static/images"
        )
        df_voorstelling["file_poster"] = df_voorstelling["file_poster"].fillna(
            "media_type_poster.png"
        )
        df_voorstelling["path_thumbnail"] = df_voorstelling.apply(
            lambda x: self.encode(x["dir_poster"], x["file_poster"]), axis=1
        )

        # Rollen
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

        # Integrate all data into list of dictionaries
        lst_voorstelling = df_voorstelling.to_dict(orient="records")
        i = 0
        while i < len(lst_voorstelling):
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

    def lid_media(self, lid: str) -> list:
        logger.info(f"Lid media voor {lid}")
        sql_statement = f"""
        SELECT
        	f.ref_uitvoering,
        	f.bestand,
        	f.type_media,
        	f.file_ext,
        	f.vlnr,
        	f.lid,
        	u.titel,
        	u.jaar,
			u.folder,
			u.type,
			u.auteur
        FROM file_leden f
        INNER JOIN uitvoering u
            ON u.ref_uitvoering = f.ref_uitvoering
        WHERE lid='{lid}'
        """
        df_media = pd.read_sql(
            sql=sql_statement,
            con=self.engine,
        )
        df_media["jaar"] = df_media["jaar"].astype("Int64")
        logger.info("Lid media - Enrich media data")
        df_media = self.enrich_media(df_media=df_media)
        lst_media = []  # Initialize the result list
        grouped_jaar = df_media.groupby("jaar")  # Group by 'jaar'
        # Iterate over each jaar
        for group_jaar, df_jaar in grouped_jaar:
            lst_titel = []
            # Group by 'titel' within each jaar
            grouped_titel = df_jaar.groupby("titel")
            # Iterate over each subgroup
            for group_titel, df_titel in grouped_titel:
                data_list = df_titel.to_dict("records")
                lst_titel.append({"uitvoering": group_titel, "media": data_list})
            lst_media.append({"jaar": group_jaar, "uitvoering": lst_titel})
        return lst_media

    def voorstelling_media(self, voorstelling: str) -> list:
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
        df_media = pd.read_sql(sql=sql_statement, con=self.engine)
        df_media = self.enrich_media(df_media=df_media)

        lst_voorstelling_media = []  # Initialize the result list
        grouped_media_type = df_media.groupby("type_media")
        # Iterate over each jaar
        for group_media_type, df_media in grouped_media_type:
            lst_media = df_media.to_dict("records")
            lst_voorstelling_media.append(
                {"type_media": group_media_type, "files": lst_media}
            )
        return lst_voorstelling_media

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

    def test_path(self) -> list:
        sql_statement = """
        SELECT f.*, u.folder
        FROM file f
        INNER JOIN uitvoering u
        ON u.ref_uitvoering = f.ref_uitvoering
        """
        df_file = pd.read_sql(sql=sql_statement, con=self.engine)
        df_file["folder"] = "/data/resources/" + df_file["folder"] + "/thumbnails"
        df_file["path"] = df_file.apply(
            lambda x: self.encode_test(x["folder"], x["bestand"]), axis=1
        )

        dict_file = df_file.to_dict("records")
        return dict_file
