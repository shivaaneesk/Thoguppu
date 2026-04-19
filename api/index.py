from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Serve static files from the parent directory for local development
app = Flask(__name__, static_folder='../', static_url_path='')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Ensure upload folder exists for Vercel Serverless environment
UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/process', methods=['POST'])
def process_audio():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['audio_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        
        try:
            # Check for API key
            groq_api_key = os.environ.get("GROQ_API_KEY")
            if not groq_api_key:
                return jsonify({'error': 'GROQ_API_KEY environment variable is not set.'}), 500
                
            client = Groq(api_key=groq_api_key)
            
            # Save file temporarily
            file.save(filepath)

            # Step 1: Transcribe via Groq (Whisper)
            with open(filepath, "rb") as audio_file:
                transcription_response = client.audio.transcriptions.create(
                  file=(file.filename, audio_file.read()),
                  model="whisper-large-v3"
                )
            transcription = transcription_response.text

            # Step 2: Summarize via Groq (Llama 3)
            # The original app targeted ~30-150 words depending on input
            sys_prompt = "You are a helpful assistant. Provide a concise summary of the provided text. Limit your summary to around 30 to 150 words."
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": sys_prompt
                    },
                    {
                        "role": "user",
                        "content": "Summarize this: " + transcription
                    }
                ],
                model="llama-3.1-8b-instant",
            )
            summary = chat_completion.choices[0].message.content

            return jsonify({
                'transcript': transcription,
                'summary': summary
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Cleanup TMP directory
            if os.path.exists(filepath):
                os.remove(filepath)
                
    return jsonify({'error': 'Unknown error occurred'}), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
