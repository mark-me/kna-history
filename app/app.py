import os

from flask import Flask, render_template, send_from_directory

from data_reader import KnaDB
from logging_kna import logger

db_reader = KnaDB(dir_resources="/data/resources/")

app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/")
@app.route("/home")
def home():
    """Home page"""
    return render_template("home.html")


@app.route("/cdn/<path:filepath>")
def cdn(filepath):
    dir, filename = os.path.split(db_reader.decode(filepath))
    logger.info(f"Serve media CDN - Directory: {dir} - File: {filename}")
    return send_from_directory(dir, filename, as_attachment=False)


@app.route("/image/<path_image>")
def show_image(path_image: str):
    logger.info(f"Show image - filepath: {path_image}")
    dict_image = db_reader.medium(path=path_image)
    return render_template("image.html", image=dict_image)

@app.route("/pdf/<path_pdf>")
def show_document(path_pdf: str):
    logger.info(f"Show PDF - {path_pdf}")
    return render_template("pdf.html", file_pdf=path_pdf)


@app.route("/video/<path_video>")
def show_movie(path_video: str):
    logger.info(f"Show video - {path_video}")
    dict_video = db_reader.medium(path=path_video)
    return render_template("video.html", video=dict_video)


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


@app.route("/tijdslijn")
def view_tijdslijn():
    """Page for viewing jaren"""
    lst_timeline = db_reader.timeline()
    return render_template("tijdslijn.html", tijdslijn=lst_timeline)


@app.route("/lid_media/<lid>")
def lid_media(lid: str):
    """Page for member photos"""
    logger.info(f"Leden media voor {lid}")
    lst_media = db_reader.lid_media(lid=lid)
    dict_lid = db_reader.lid_info(id_lid=lid)
    return render_template("lid_media.html", lid=dict_lid, media=lst_media)


@app.route("/voorstelling_media/<voorstelling>")
def voorstelling_media(voorstelling: str):
    """Page for member media"""
    dict_voorstelling = db_reader.voorstelling_info(voorstelling=voorstelling)
    lst_media = db_reader.voorstelling_media(voorstelling=voorstelling)
    logger.info(f"Get media voor voorstelling {voorstelling}")

    return render_template(
        "voorstelling_media.html", voorstelling=dict_voorstelling, media=lst_media
    )

@app.route("/voorstelling_lid_media/<voorstelling>/<lid>")
def voorstelling_lid_media(voorstelling: str, lid: str):
    """Page for member media for a voorstelling"""
    dict_voorstelling = db_reader.voorstelling_info(voorstelling=voorstelling)
    lst_media = db_reader.voorstelling_lid_media(voorstelling=voorstelling, lid=lid)
    logger.info(f"Get media voor voorstelling {voorstelling} van {lid}")
    return render_template(
        "voorstelling_media.html", voorstelling=dict_voorstelling, media=lst_media
    )

@app.route("/about")
def about():
    """About page"""
    return render_template("about.html", title="Over")


if __name__ == "__main__":
    app.run(debug=True, port=88)
