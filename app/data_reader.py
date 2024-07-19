import binascii
import os

import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from logging_kna import logger


class KnaDB:
    def __init__(self, dir_resources: str, debug: bool = False) -> None:
        self.dir_resources = dir_resources
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

    def __enrich_media(self, df_media: pd.DataFrame) -> pd.DataFrame:
        df_media["dir_thumbnail"] = (
            self.dir_resources + df_media["folder"] + "/thumbnails"
        )
        df_media["dir_media"] = self.dir_resources + df_media["folder"]
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

    def lid_info(self, id_lid: str) -> dict:
        sql_statement = f"""
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
            l.Achternaam IS NOT NULL AND
            l.id_lid = "{id_lid}"
        GROUP BY
            l.id_lid,
            l.Voornaam,
            l.Achternaam,
            l.Geboortedatum,
            l.Startjaar,
            l.achternaam_sort
        """
        df_lid = pd.read_sql(
            sql=sql_statement,
            con=self.engine,
        )
        dict_lid = df_lid.to_dict("records")[0]
        return dict_lid

    def lid_rollen(self, id_lid: str) -> pd.DataFrame:
        sql_statement = f"""
        SELECT
            r.ref_uitvoering,
            r.id_lid,
            r.rol,
            r.rol_bijnaam,
            l.achternaam_sort
        FROM rol r
        INNER JOIN lid l
        ON l.id_lid = r.id_lid
        WHERE
            l.gdpr_permission = 1 AND
            r.id_lid = "{id_lid}"
        """
        df_rol = pd.read_sql(sql=sql_statement, con=self.engine)
        if df_rol.shape[0] > 0:
            df_rol = (
                df_rol.groupby(["ref_uitvoering", "id_lid", "achternaam_sort"])
                .agg(list)
                .reset_index()
            )
        return df_rol

    def lid_media(self, id_lid: str) -> list:
        logger.info(f"Lid media voor {id_lid}")
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
        WHERE lid="{id_lid}"
        """
        df_media = pd.read_sql(
            sql=sql_statement,
            con=self.engine,
        )
        df_media["jaar"] = df_media["jaar"].astype("Int64")
        df_media = self.__enrich_media(df_media=df_media)
        df_rollen = self.lid_rollen(id_lid=id_lid)
        lst_media = []  # Initialize the result list
        grouped_jaar = df_media.groupby("jaar")  # Group by 'jaar'
        # Iterate over each jaar
        for group_jaar, df_jaar in grouped_jaar:
            lst_titel = []
            # Group by 'titel' within each jaar
            grouped_titel = df_jaar.groupby(["ref_uitvoering", "titel"])
            # Iterate over each subgroup
            for group_titel, df_titel in grouped_titel:
                data_list = df_titel.to_dict("records")
                df_rol = df_rollen.loc[df_rollen["ref_uitvoering"] == group_titel[0]]
                if df_rol.shape[0] > 0:
                    dict_rol = df_rol.to_dict("records")[0]
                else:
                    dict_rol = {"rol": [None], "rol_bijnaam": [None]}
                lst_titel.append(
                    {
                        "ref_uitvoering": group_titel[0],
                        "uitvoering": group_titel[1],
                        "rol": dict_rol["rol"],
                        "rol_bijnaam": dict_rol["rol_bijnaam"],
                        "media": data_list,
                    }
                )
            lst_media.append({"jaar": group_jaar, "uitvoering": lst_titel})
        lst_media = sorted(lst_media, key=lambda d: d["jaar"], reverse=True)
        return lst_media

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
        lst_lid = df_lid.to_dict(orient="records")

        # Rollen
        sql_statement = """
        SELECT DISTINCT
            u.titel,
            u.jaar,
            u.ref_uitvoering,
            u.auteur,
            r.id_lid,
            r.qty_media
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

    def voorstelling_info(self, voorstelling: str) -> dict:
        sql_statement = f"""
        SELECT *
        FROM uitvoering
        WHERE ref_uitvoering = "{voorstelling}"
        """
        df_voorstelling = pd.read_sql(sql=sql_statement, con=self.engine)
        df_voorstelling["datum_van"] = pd.to_datetime(df_voorstelling["datum_van"])
        df_voorstelling["datum_tot"] = pd.to_datetime(df_voorstelling["datum_tot"])
        df_voorstelling.loc[df_voorstelling["datum_van"].notnull(), "datum_van"] = (
            df_voorstelling.loc[
                df_voorstelling["datum_van"].notnull(), "datum_van"
            ].dt.date
        )
        df_voorstelling.loc[df_voorstelling["datum_tot"].notnull(), "datum_tot"] = (
            df_voorstelling.loc[
                df_voorstelling["datum_tot"].notnull(), "datum_tot"
            ].dt.date
        )
        dict_voorstelling = df_voorstelling.to_dict("records")[0]
        dict_voorstelling["rollen"] = self.voorstelling_rollen(
            voorstelling=voorstelling
        )
        return dict_voorstelling

    def voorstelling_rollen(self, voorstelling: str) -> list:
        # Rollen
        sql_statement = f"""
        SELECT
            r.ref_uitvoering,
            r.id_lid,
            r.rol,
            r.rol_bijnaam,
            l.achternaam_sort,
            COUNT(fl.bestand) AS qty_media
        FROM rol r
        INNER JOIN lid l
        ON l.id_lid = r.id_lid
        LEFT JOIN file_leden fl
        ON  fl.ref_uitvoering = r.ref_uitvoering AND
            fl.lid = r.id_lid
        WHERE
            l.gdpr_permission = 1 AND
            r.ref_uitvoering = "{voorstelling}"
        GROUP BY
            r.ref_uitvoering,
            r.id_lid,
            r.rol,
            r.rol_bijnaam,
            l.achternaam_sort
        ORDER BY l.achternaam_sort
        """
        df_rol = pd.read_sql(sql=sql_statement, con=self.engine)
        if df_rol.shape[0] > 0:
            df_rol = (
                df_rol.groupby(
                    ["ref_uitvoering", "id_lid", "achternaam_sort", "qty_media"]
                )
                .agg(list)
                .reset_index()
            )
        return df_rol.to_dict("records")

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
        WHERE f.ref_uitvoering="{voorstelling}"
        """
        df_media = pd.read_sql(sql=sql_statement, con=self.engine)
        df_media = self.__enrich_media(df_media=df_media)

        lst_voorstelling_media = []  # Initialize the result list
        grouped_media_type = df_media.groupby("type_media")
        # Iterate over each media type
        for group_media_type, df_media in grouped_media_type:
            lst_media = df_media.to_dict("records")
            lst_voorstelling_media.append(
                {"type_media": group_media_type, "files": lst_media}
            )
        return lst_voorstelling_media

    def voorstelling_thumbnail(self, voorstelling: str) -> str:
        # Poster
        sql_statement = f"""
        SELECT u.ref_uitvoering,
            u.folder AS dir_thumbnail,
            f.type_media,
            MIN(f.bestand) as file_poster
        FROM uitvoering u
        LEFT JOIN file f
        ON f.ref_uitvoering = u.ref_uitvoering
        WHERE u.ref_uitvoering = "{voorstelling}" AND
            ( f.type_media = 'poster' OR f.type_media = 'kaartje')
        GROUP BY
            u.ref_uitvoering,
            u.folder,
            f.type_media"""
        df_thumbnail = pd.read_sql(sql=sql_statement, con=self.engine)
        df_thumbnail = df_thumbnail.pivot(
            index=["ref_uitvoering", "dir_thumbnail"],
            columns="type_media",
            values="file_poster",
        ).reset_index()

        if df_thumbnail.shape[0] > 0:
            dict_thumbnail = df_thumbnail.to_dict("records")[0]
            dir_thumbnail = (
                self.dir_resources + dict_thumbnail["dir_thumbnail"] + "/thumbnails"
            )
            if "poster" in dict_thumbnail:
                file_thumbnail = dict_thumbnail["poster"]
            elif "kaartje" in dict_thumbnail:
                file_thumbnail = dict_thumbnail["kaartje"]
            else:
                dir_thumbnail = "static/images"
                file_thumbnail = "media_type_poster.png"
        else:
            dir_thumbnail = "static/images"
            file_thumbnail = "media_type_poster.png"
        path_thumbnail = self.encode(folder=dir_thumbnail, file=file_thumbnail)
        return path_thumbnail

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
        df_voorstelling["qty_media"] = df_voorstelling["qty_media"].astype("Int64")
        df_voorstelling["datum_van"] = pd.to_datetime(df_voorstelling["datum_van"])
        df_voorstelling["datum_tot"] = pd.to_datetime(df_voorstelling["datum_tot"])
        df_voorstelling.loc[df_voorstelling["datum_van"].notnull(), "datum_van"] = (
            df_voorstelling.loc[
                df_voorstelling["datum_van"].notnull(), "datum_van"
            ].dt.date
        )
        df_voorstelling.loc[df_voorstelling["datum_tot"].notnull(), "datum_tot"] = (
            df_voorstelling.loc[
                df_voorstelling["datum_tot"].notnull(), "datum_tot"
            ].dt.date
        )

        # Integrate all data into list of dictionaries
        lst_voorstelling = df_voorstelling.to_dict(orient="records")
        i = 0
        while i < len(lst_voorstelling):
            voorstelling = lst_voorstelling[i]["ref_uitvoering"]
            # Add rollen
            dict_rollen = self.voorstelling_rollen(voorstelling=voorstelling)
            lst_voorstelling[i]["rollen"] = dict_rollen
            lst_voorstelling[i]["path_thumbnail"] = self.voorstelling_thumbnail(
                voorstelling=voorstelling
            )
            i = i + 1
        return lst_voorstelling

    def voorstelling_lid_media(self, voorstelling: str, lid: str) -> list:
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
        WHERE lid="{lid}" AND
            f.ref_uitvoering = "{voorstelling}"
        """
        df_media = pd.read_sql(
            sql=sql_statement,
            con=self.engine,
        )
        logger.info("Lid media - Enrich media data")
        df_media = self.__enrich_media(df_media=df_media)
        lst_voorstelling_media = []  # Initialize the result list
        grouped_media_type = df_media.groupby("type_media")
        # Iterate over each media type
        for group_media_type, df_media in grouped_media_type:
            lst_media = df_media.to_dict("records")
            lst_voorstelling_media.append(
                {"type_media": group_media_type, "files": lst_media}
            )
        return lst_voorstelling_media

    def medium(self, path: str) -> dict:
        dir_medium, file_medium = os.path.split(self.decode(path))
        dir_medium = dir_medium.replace(self.dir_resources, "")
        sql_statement = f"""
        SELECT f.*
        FROM file f
        INNER JOIN uitvoering u
        ON u.ref_uitvoering = f.ref_uitvoering
        WHERE
            u.folder = "{ dir_medium }" AND
            f.bestand = "{ file_medium }"
        """
        df_file = pd.read_sql(sql=sql_statement, con=self.engine)
        dict_file = df_file.to_dict("records")[0]
        dict_file["folder"] = self.dir_resources + dict_file["folder"]
        dict_file["path_medium"] = self.encode(
            folder=dict_file["folder"], file=dict_file["bestand"]
        )
        sql_statement = f"""
        SELECT f.vlnr, f.lid
        FROM file_leden f
        INNER JOIN uitvoering u
        ON u.ref_uitvoering = f.ref_uitvoering
        WHERE
            u.folder = "{ dir_medium }" AND
            f.bestand = "{ file_medium }"
        ORDER BY f.vlnr
        """
        df_file_leden = pd.read_sql(sql=sql_statement, con=self.engine)
        list_file_leden = df_file_leden.to_dict("records")
        dict_file["leden"] = list_file_leden
        return dict_file

    def timeline(self) -> list:
        sql_statement = "SELECT * FROM uitvoering"
        df_event = pd.read_sql(sql=sql_statement, con=self.engine)
        df_event["datum_van"] = df_event["datum_van"].dt.date
        df_event["datum_tot"] = df_event["datum_tot"].dt.date
        sql_statement = "SELECT * FROM lid WHERE gdpr_permission = 1"
        df_lid = pd.read_sql(sql=sql_statement, con=self.engine)

        lst_events = []  # Initialize the result list
        grouped_jaar = df_event.groupby("jaar")  # Group by 'jaar'
        # Iterate over each jaar
        for group_jaar, df_jaar in grouped_jaar:
            dict_leden_nieuw = df_lid.loc[df_lid["Startjaar"] == group_jaar].to_dict(
                "records"
            )
            lst_event_type = []
            # Group by 'titel' within each jaar
            grouped_type_event = df_jaar.groupby("type")
            # Iterate over each subgroup
            for group_event_type, df_event in grouped_type_event:
                data_list = df_event.to_dict("records")
                lst_event_type.append(
                    {"event_type": group_event_type, "events": data_list}
                )
            lst_events.append(
                {
                    "jaar": group_jaar,
                    "nieuwe_leden": dict_leden_nieuw,
                    "events": lst_event_type,
                }
            )
        lst_events = sorted(lst_events, key=lambda d: d["jaar"])
        return lst_events
