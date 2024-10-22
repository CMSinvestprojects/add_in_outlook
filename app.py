from flask import Flask
from flask import Flask, request, jsonify, render_template
from flask.helpers import send_file
import os
import dotenv
from devcerts.install import ensure_certificates_are_installed 
from email_relatorio import RelatorioReuniao
from database import engine

dotenv.load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/taskpane.html")
def taskpane():
    return render_template("taskpane.html")

@app.route("/commands.html")
def commands():
    return render_template("commands.html")

@app.route("/assets/icon-16.png")
def icon16():
    return send_file("./static/assets/icon-16.png",mimetype='image/png')

@app.route("/assets/icon-32.png")
def icon32():
    return send_file("./static/assets/icon-32.png",mimetype='image/png')

@app.route("/assets/icon-64.png")
def icon64():
    return send_file("./static/assets/icon-64.png",mimetype='image/png')

@app.route("/assets/icon-80.png")
def icon80():
    return send_file("./static/assets/icon-80.png",mimetype='image/png')

@app.route("/assets/icon-128.png")
def icon128():
    return send_file("./static/assets/icon-128.png",mimetype='image/png')

@app.route("/assets/logo-filled.png")
def iconlogofilled():
    return send_file("./static/assets/logo-filled.png",mimetype='image/png')

@app.route('/favicon.ico')
def favicon():
    return send_file('./static/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/submit-client-code', methods=['POST'])
def submit_client_code():
    data = request.json
    client_code = data.get('client_code')
    email = data.get('userEmail')
    
    rr = RelatorioReuniao(client_code   ,engine)
    rr.destinatario(email)
    rr.estruturar_email()
    
    response = {
        'message': f'Client code {client_code} received successfully'
    }
    
    return jsonify(response)
    
if __name__ == "__main__":
    app.run(debug=True)
