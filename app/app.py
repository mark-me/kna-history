import binascii
import logging
from sys import stdout
import os

from flask import Flask, render_template, send_from_directory
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
    leden = df_lid.to_dict(orient="records")
    # reports = sorted(reports, key=lambda x: x['last_modified'], reverse=True)
    return render_template("leden.html", leden=leden)


@app.route("/lid_fotos/<lid>")
def lid_fotos(lid: str):
    """Page for member photos"""
    df_fotos = pd.read_sql(
        sql=f"SELECT * FROM file INNER JOIN uitvoering ON uitvoering.ref_uitvoering = file.ref_uitvoering WHERE lid='{lid}'",
        con=engine,
    )
    df_fotos["jaar"] = df_fotos["jaar"].astype("Int64")
    fotos = df_fotos.to_dict(orient="records")
    fotos = [
        dict(
            foto,
            path=encode(
                os.path.join("/data/kna_resources/" + foto["folder"], foto["bestand"])
            ),
        )
        for foto in fotos
    ]
    fotos = [
        dict(
            foto,
            path2=os.path.join(
                "/data/kna_resources/" + foto["folder"], foto["bestand"]
            ),
        )
        for foto in fotos
    ]
    lid = {"naam": lid}
    logger.info(f"Loggin")
    return render_template("lid_fotos.html", lid=lid, fotos=fotos)


@app.route("/lid_fotos/cdn/<path:filepath>")
def download_file(filepath):
    dir, filename = os.path.split(decode(filepath))
    logger.info(f"Directory: {dir} - File: {filename}")
    return send_from_directory(dir, filename, as_attachment=False)


if __name__ == "__main__":
    app.run(debug=True, port=88)
