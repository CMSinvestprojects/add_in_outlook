from flask import Flask
from flask import Flask, request, jsonify, render_template
from flask.helpers import send_file
import os
import dotenv
from devcerts.install import ensure_certificates_are_installed 
from email_relatorio import RelatorioReuniao
from database import engine
import requests 
from api_functions import upload_file_to_s3, notify_webhook, call_process_transcription
import threading

dotenv.load_dotenv()

FASTAPI_URL = os.getenv('FASTAPI_URL')

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload_audio")
def upload_page():
    return render_template('upload_video.html')



@app.route("/upload", methods=['POST', 'GET'])
def upload():
    # Verifica se o arquivo foi enviado corretamente
    if 'files' not in request.files:
        return jsonify({"error": "Nenhum arquivo encontrado"}), 400
    
    file = request.files['files']
    rawFile = request.files.get('files')
    
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    

    file_content = file.read()
    file_name = file.filename
    content_type = file.content_type
    
    # Iniciar o upload do arquivo para o S3 em segundo plano
    print("Iniciando upload em segundo plano")
    threading.Thread(target=upload_file_to_s3, args=(file_name, file_content, content_type)).start()

    # Liberar o usuário imediatamente
    return jsonify({"message": f"Arquivo {file.filename} está sendo enviado. O upload e o processamento ocorrerão em segundo plano."}), 200



@app.route("/taskpane")
def taskpane():
    return render_template("taskpane.html")

@app.route("/commands")
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
    return send_file("./static/assets/logo-header.svg",mimetype='image/svg')

@app.route('/favicon.ico')
def favicon():
    return send_file('./static/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/submit-client-code', methods=['POST'])
def submit_client_code():
    data = request.json
    client_code = data.get('client_code')
    email = data.get('userEmail')
    
    rr = RelatorioReuniao(client_code   ,engine)
    rr._ec.destinatario(email)
    rr.estruturar_email()
    
    response = {
        'message': f'Client code {client_code} received successfully'
    }
    
    return jsonify(response)
    
if __name__ == "__main__":
    if os.environ.get("APP_MODE") == "DEV":
        print("Running in DEV mode")
        # Call the function to ensure certificates are installed and valid
        ensure_certificates_are_installed()

        # Assuming the ensure_certificates_are_installed function updates the default paths as needed
        from devcerts.defaults import localhost_certificate_path, localhost_key_path
        ssl_context = (localhost_certificate_path, localhost_key_path)
        
        app.run(debug=True, ssl_context=ssl_context)
    else:
        app.run(debug=True)
