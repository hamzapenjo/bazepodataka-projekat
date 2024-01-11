import configparser
import os
import mysql.connector
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource

app = Flask(__name__)
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
current_directory = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_directory, 'config.ini')
config = configparser.ConfigParser()
config.read(config_path)
dbconfig = config["database"]
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://student2324:11155@bazepodataka.ba:7306/student2324'
db = SQLAlchemy(app)
api = Api(app)


class PrijaveDostavljaca(db.Model):
    __tablename__ = 'PrijaveDostavljaca'
    RedniBrojPrijave = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DostavljacID = db.Column(db.Integer)
    DatumVrijemePrijava = db.Column(db.DateTime, nullable=False)
    PrijavaOdjava = db.Column(db.String(10), nullable=False)


class LogVozila(db.Model):
    __tablename__ = 'LogVozila'
    LogVozilaID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DostavljacID = db.Column(db.Integer)
    VoziloID = db.Column(db.Integer)
    DatumVrijemeZaduzivanje = db.Column(db.DateTime, nullable=False)
    DatumVrijemeRazduzivanje = db.Column(db.DateTime)


class PrijaveDostavljacaResource(Resource):
    def get(self):
        prijave = PrijaveDostavljaca.query.all()
        return {"prijave": [{"RedniBrojPrijave": p.RedniBrojPrijave, "DostavljacID": p.DostavljacID,
                              "DatumVrijemePrijava": p.DatumVrijemePrijava.isoformat(), "PrijavaOdjava": p.PrijavaOdjava}
                             for p in prijave]}


class LogVozilaResource(Resource):
    def get(self):
        logovi = LogVozila.query.all()
        return {"logovi": [{"LogVozilaID": l.LogVozilaID, "DostavljacID": l.DostavljacID, "VoziloID": l.VoziloID,
                            "DatumVrijemeZaduzivanje": l.DatumVrijemeZaduzivanje.isoformat(),
                            "DatumVrijemeRazduzivanje": l.DatumVrijemeRazduzivanje.isoformat() if l.DatumVrijemeRazduzivanje else None}
                           for l in logovi]}


class Narudzba(db.Model):
    __tablename__ = 'Narudzbe'
    NarudzbeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    VrijemeNarudzbe = db.Column(db.DateTime, nullable=False)
    ImePrezime = db.Column(db.String(50), nullable=False)
    Adresa = db.Column(db.String(50), nullable=False)
    Grad = db.Column(db.String(50), nullable=False)
    KontaktTelefon = db.Column(db.String(50), nullable=False)


cnxpool = mysql.connector.pooling.MySQLConnectionPool(
    host=dbconfig["host"],
    user=dbconfig["user"],
    password=dbconfig["password"],
    database=dbconfig["database"],
    port=int(dbconfig["port"]),
    pool_name="pool",
    pool_size=int(dbconfig["pool_size"])
)


class Proizvod(db.Model):
    __tablename__ = 'Proizvodi'
    ProizvodiID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Sifra = db.Column(db.String(50), nullable=False)
    NazivProizvoda = db.Column(db.String(50), nullable=False)
    KategorijaID = db.Column(db.Integer, db.ForeignKey('KategorijaProizvoda.KategorijaProizvodaID'))
    OpisProizvoda = db.Column(db.TEXT)
    Slika = db.Column(db.String(255))
    Cijena = db.Column(db.DECIMAL(10, 2), nullable=False)


def get_lista_dostavljaca_html():
    """ Lista dostavljaca """
    lista_dostavljaca = []
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as d_cur:
            d_cur.execute(
                "SELECT DostavljacID, ImePrezime, TipDostavljaca FROM student2324.Dostavljaci ORDER BY DostavljacID"
            )
            lista_dostavljaca = d_cur.fetchall()
    return render_template("lista_dostavljaca.html", lista=lista_dostavljaca)


@app.route("/")
def index():
    return get_lista_dostavljaca_html()


def query_database_for_narudzbe():
    return Narudzba.query.all()


@app.route("/narudzbe")
def prikazi_narudzbe():
    try:
        narudzbe = query_database_for_narudzbe()
        print(narudzbe)
        return render_template("prikaz_narudzbi.html", narudzbe=narudzbe)
    except Exception as e:
        app.logger.error(f"Greška prilikom prikaza narudžbi: {e}")
        return "Internal Server Error", 500


@app.route("/proizvodi")
def prikazi_proizvode():
    proizvodi = Proizvod.query.all()
    return render_template("prikaz_proizvoda.html", proizvodi=proizvodi)


@app.route("/prijave")
def prikazi_prijave():
    prijave = PrijaveDostavljaca.query.all()
    return render_template("prijave.html", prijave=prijave)


@app.route("/logovi")
def logovi():
    logovi = LogVozila.query.all()
    return render_template("logovi.html", logovi=logovi)


if __name__ == "__main__":
    app.run(debug=True)
