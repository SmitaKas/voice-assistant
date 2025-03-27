from flask import Flask, request, render_template
from flask_cors import CORS
import json
import os
import base64

from worker import speech_to_text, text_to_speech, openai_process_message

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text_route():
    print("processing speech-to-text")
    audio_binary = request.data
    text = speech_to_text(audio_binary)
    response = app.response_class(
        response=json.dumps({'text': text}),
        status=200,
        mimetype='application/json'
    )
    print("recognised text:", text)
    return response

@app.route('/process-message', methods=['POST'])
def process_message_route():
    try:
        user_message = request.json['userMessage']
        print('user_message', user_message)

        voice = request.json['voice']
        print('voice', voice)

        openai_response_text = openai_process_message(user_message)
        print('openai_response_text', openai_response_text)

        openai_response_text = os.linesep.join([s for s in openai_response_text.splitlines() if s])
        openai_response_speech = text_to_speech(openai_response_text, voice)
        print('audio generated')

        openai_response_speech = base64.b64encode(openai_response_speech).decode('utf-8')
        print('audio encoded to base64')

        response = app.response_class(
            response=json.dumps({
                "openaiResponseText": openai_response_text,
                "openaiResponseSpeech": openai_response_speech
            }),
            status=200,
            mimetype='application/json'
        )
        print('response ready')
        return response

    except Exception as e:
        print("❌ ERROR in /process-message route:", e)
        return app.response_class(
            response=json.dumps({"error": str(e)}),
            status=500,
            mimetype='application/json'
        )

if __name__ == '__main__':
    import sys

# Allow optional port override via --port 8001
port = 8000
if len(sys.argv) >= 3 and sys.argv[1] == "--port":
    port = int(sys.argv[2])

app.run(host='0.0.0.0', port=port)
