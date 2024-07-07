
import os

from flask import Flask, render_template, send_from_directory

from data_reader import KnaDB
from logging_kna import logger

db_reader = KnaDB()

app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/")
@app.route("/home")
def home():
    """Home page"""
    return render_template("home.html")

@app.route("/foto/<foto>")
def show_photo(foto:str):
    return render_template("foto.html", foto=foto)

@app.route("/leden")
def view_leden():
    """Page for viewing members"""
    lst_leden = db_reader.leden()
    # reports = sorted(reports, key=lambda x: x['last_modified'], reverse=True)
    return render_template("leden.html", leden=lst_leden)

@app.route("/voorstellingen")
def view_voorstellingen():
    """Page for viewing uitvoeringen"""
    lst_voorstelling = db_reader.voorstellingen()
    return render_template("voorstellingen.html", voorstellingen=lst_voorstelling)

@app.route("/lid_fotos/<lid>")
def lid_fotos(lid: str):
    """Page for member photos"""
    lst_fotos = db_reader.lid_fotos(lid=lid)
    return render_template("lid_fotos.html", lid={"naam": lid}, fotos=lst_fotos)

@app.route("/voorstelling_fotos/<voorstelling>")
def voorstelling_fotos(voorstelling: str):
    """Page for member photos"""
    lst_fotos = db_reader.voorstelling_fotos(voorstelling=voorstelling)
    logger.info(voorstelling)
    return render_template(
        "voorstelling_fotos.html", voorstelling=voorstelling, fotos=lst_fotos
    )

@app.route("/cdn/<path:filepath>")
def lid_foto(filepath):
    dir, filename = os.path.split(db_reader.decode(filepath))
    logger.info(f"Directory: {dir} - File: {filename}")
    return send_from_directory(dir, filename, as_attachment=False)

@app.route("/foto/cdn/<path:filepath>")
def show_image(filepath):
    dir, filename = os.path.split(db_reader.decode(filepath))
    logger.info(f"Directory: {dir} - File: {filename}")
    return send_from_directory(dir, filename, as_attachment=False)

@app.route("/lid_fotos/cdn/<path:filepath>")
def download_file(filepath):
    dir, filename = os.path.split(db_reader.decode(filepath))
    logger.info(f"Directory: {dir} - File: {filename}")
    return send_from_directory(dir, filename, as_attachment=False)

@app.route("/about")
def about():
    """About page"""
    return render_template("about.html", title="Over")


if __name__ == "__main__":
    app.run(debug=True, port=88)
