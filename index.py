from os import environ
from flask import Flask, request, jsonify
from flask_cors import CORS

import json

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

from hugchat import hugchat
from hugchat.login import Login

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

email = environ.get("EMAIL")
password = environ.get("PASSWORD")

sign = Login(email, password)
cookies = sign.login()

cookie_path_dir = "./cookies_snapshot"
sign.saveCookiesToDir(cookie_path_dir)

chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"

@app.route("/api/resume-speech", methods=['POST'])
def postChat():

    try:
        url = request.json['url']

        transcript_list  = YouTubeTranscriptApi.list_transcripts(url)

        transcript = transcript_list.find_generated_transcript(['en', 'es'])

        translated_transcript = transcript.translate('es')

        spanish = translated_transcript.fetch()

        formatter = JSONFormatter()

        json_formatted = formatter.format_transcript(spanish)

        data = json.loads(json_formatted)

        texto = ""

        for d in data:
            texto = texto + " " + d['text']

        query_info = "Actua como un profesor de ciencias de la computación, tienes mucha experiencia dando clases y redactas informes ordenados con frases sencillas y comprensibles para los estudiantes. Escribe un informe dado el siguiente contexto: " + texto

        query_result = chatbot.chat(query_info)

        return jsonify({'respuesta': str(query_result).encode().decode('utf-8'), 'params' :  url, 'guion' : str(texto).encode().decode('utf-8'), 'codigo': 200})

    except Exception as ex:
        return jsonify({
            'mensaje': 'Ocurrio un error al procesar su peticion',
            'error': ex,
            'codigo' : 500
        })
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)