import configparser
import os
import mysql.connector
from flask import Flask, render_template

app = Flask(__name__)

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

current_directory = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_directory, 'config.ini')

config = configparser.ConfigParser()
config.read(config_path)
dbconfig = config["database"]


cnxpool = mysql.connector.pooling.MySQLConnectionPool(
    host=dbconfig["host"],
    user=dbconfig["user"],
    password=dbconfig["password"],
    database=dbconfig["database"],
    port=int(dbconfig["port"]),
    pool_name="pool",
    pool_size=int(dbconfig["pool_size"])
)

try:
    connection = cnxpool.get_connection()
    print("Uspjesno povezan sa bazom podataka.")
    connection.close()
except Exception as e:
    print(f"Greška pri povezivanju sa bazom podataka: {e}")


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



if __name__ == "__main__":
    app.run(debug=True)
