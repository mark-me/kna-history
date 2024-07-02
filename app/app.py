import binascii
import logging
from sys import stdout
import os

from flask import Flask, render_template, send_from_directory
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+mysqldb://root:kna-toneel@mariadb/kna")
app = Flask(__name__)

# Define logger
logger = logging.getLogger("mylogger")

logger.setLevel(logging.INFO)  # set logger level
logFormatter = logging.Formatter(
    "%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s"
)
consoleHandler = logging.StreamHandler(stdout)  # set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

if __name__ == "__main__":
    app.run(debug=True)


def encode(x):
    return binascii.hexlify(x.encode("utf-8")).decode()


def decode(x):
    return binascii.unhexlify(x.encode("utf-8")).decode()


@app.route("/")
@app.route("/home")
def home():
    """Home page"""
    return render_template("home.html")


@app.route("/leden")
def view_leden():
    """Page for viewing members"""
    df_lid = pd.read_sql_table(table_name="lid", con=engine)
    df_lid["Geboortedatum"] = df_lid["Geboortedatum"].dt.date
    df_lid["Startjaar"] = df_lid["Startjaar"].astype("Int64")
    df_lid['dir_photo'] = "/data/resources/Leden/" + df_lid["id_lid"] + ".png"
    df_lid['photo_exists'] = df_lid['dir_photo'].astype(str).map(os.path.exists)
    df_lid['dir_photo'] = np.where(df_lid['photo_exists'], "/data/resources/Leden", "static/images")
    df_lid['file_photo'] = np.where(df_lid['photo_exists'], df_lid["id_lid"] + ".png", "member_photo_default2.png")
    lst_leden = df_lid.to_dict(orient="records")
    lst_leden = [
                dict(
                    data,
                    profielfoto=encode(
                        os.path.join(
                            data["dir_photo"],
                            data["file_photo"],
                        )
                    ),
                )
                for data in lst_leden #if data["photo_exists"]
            ]
    logger.info(lst_leden)
    # reports = sorted(reports, key=lambda x: x['last_modified'], reverse=True)
    return render_template("leden.html", leden=lst_leden)

@app.route("/voorstellingen")
def view_voorstellingen():
    """Page for viewing uitvoeringen"""
    sql_statement = """
    SELECT
        uitvoering.titel,
        uitvoering.jaar,
        uitvoering.folder,
        file.type_media,
        MIN(file.bestand) AS file_photo
    FROM uitvoering
    LEFT JOIN file
    ON uitvoering.ref_uitvoering = file.ref_uitvoering
    WHERE uitvoering.`type` = 'Uitvoering' AND
        (file.type_media = 'foto' OR file.type_media IS NULL)
    GROUP BY
        uitvoering.titel,
        uitvoering.jaar,
        uitvoering.folder,
        file.type_media
    """
    df_voorstelling = pd.read_sql(sql=sql_statement, con=engine)
    df_voorstelling["jaar"] = df_voorstelling["jaar"].astype("Int64")
    logger.info(df_voorstelling.head())
    lst_voorstelling = df_voorstelling.to_dict(orient="records")
    lst_voorstelling = [
                dict(
                    data,
                    foto=encode(
                        os.path.join(
                            "/data/resources/" + data['folder'] + "/thumbnails",
                            data["file_photo"],
                        )
                    ),
                )
                for data in lst_voorstelling
            ]
    logger.info(lst_voorstelling)
    return render_template("voorstellingen.html", voorstellingen=lst_voorstelling)

@app.route("/lid_fotos/<lid>")
def lid_fotos(lid: str):
    """Page for member photos"""
    df_fotos = pd.read_sql(
        sql=f"SELECT * FROM file INNER JOIN uitvoering ON uitvoering.ref_uitvoering = file.ref_uitvoering WHERE lid='{lid}'",
        con=engine,
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
                    path=encode(
                        os.path.join(
                            f"/data/resources/{data['folder']}/thumbnails",
                            data["bestand"],
                        )
                    ),
                )
                for data in data_list
            ]
            lst_titel.append({"uitvoering": group_titel, "fotos": data_list})
        lst_fotos.append({"jaar": group_jaar, "uitvoering": lst_titel})
    lid = {"naam": lid}
    return render_template("lid_fotos.html", lid=lid, fotos=lst_fotos)


@app.route("/cdn/<path:filepath>")
def lid_foto(filepath):
    dir, filename = os.path.split(decode(filepath))
    logger.info(f"Directory: {dir} - File: {filename}")
    return send_from_directory(dir, filename, as_attachment=False)

@app.route("/lid_fotos/cdn/<path:filepath>")
def download_file(filepath):
    dir, filename = os.path.split(decode(filepath))
    logger.info(f"Directory: {dir} - File: {filename}")
    return send_from_directory(dir, filename, as_attachment=False)


@app.route("/about")
def about():
    """About page"""
    return render_template("about.html", title="Over")


if __name__ == "__main__":
    app.run(debug=True, port=88)
