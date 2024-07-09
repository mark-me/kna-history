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


@app.route("/thumbnail/<path:filepath>")
def lid_foto(filepath):
    test = db_reader.decode(filepath)
    logger.info(f"Thumbnail - Path: {test}")
    dir, filename = os.path.split(db_reader.decode(filepath))
    logger.info(f"Thumbnail - Directory: {dir} - File: {filename}")
    return send_from_directory(dir, filename, as_attachment=False)


@app.route("/image/<path:filepath>")
def show_image(filepath):
    dir, filename = os.path.split(db_reader.decode(filepath))
    logger.info(f"Show image - Directory: {dir} - File: {filename}")
    return send_from_directory(dir, filename, as_attachment=False)

@app.route("/pdf/<file_pdf>")
def show_document(file_pdf: str):
    logger.info(f"Show PDF - {file_pdf}")
    return render_template("pdf.html", file_pdf=file_pdf)


@app.route("/video/<file_video>")
def show_movie(file_video: str):
    logger.info(f"Show video - {file_video}")
    return render_template("video.html", file_video=file_video)


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


@app.route("/jaren")
def view_jaren():
    """Page for viewing jaren"""
    lst_jaar = db_reader.jaren()
    return render_template("jaren.html", jaren=lst_jaar)


@app.route("/lid_media/<lid>")
def lid_media(lid: str):
    """Page for member photos"""
    lst_media = db_reader.lid_media(lid=lid)
    return render_template("lid_media.html", lid={"naam": lid}, media=lst_media)


@app.route("/voorstelling_media/<voorstelling>")
def voorstelling_media(voorstelling: str):
    """Page for member media"""
    lst_media = db_reader.voorstelling_media(voorstelling=voorstelling)
    logger.info(f"Get media voor voorstelling {voorstelling}")
    return render_template(
        "voorstelling_media.html", voorstelling=voorstelling, media=lst_media
    )


@app.route("/about")
def about():
    """About page"""
    return render_template("about.html", title="Over")


if __name__ == "__main__":
    app.run(debug=True, port=88)
