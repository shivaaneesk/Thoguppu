from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import torch
import os

app = Flask(__name__)

# --- Model Loading ---
# We use CPU to ensure it fits in the free tier
device = "cpu"
print(f"Loading models on {device}...")

# 1. Whisper for Speech-to-Text
asr_pipeline = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base",
    device=device
)

# 2. T5 for Summarization
summarizer_pipeline = pipeline(
    "summarization",
    model="t5-base",
    tokenizer="t5-base",
    device=device
)

# Ensure upload folder exists
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_audio():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['audio_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Step 1: Transcribe
            transcription = asr_pipeline(filepath, chunk_length_s=30)["text"]

            # Step 2: Summarize
            input_text = "summarize: " + transcription
            
            # Dynamic length handling
            input_len = len(input_text.split())
            min_len = min(30, input_len // 2)
            max_len = min(150, input_len + 20)

            summary = summarizer_pipeline(
                input_text, 
                max_length=max_len, 
                min_length=min_len, 
                do_sample=False
            )[0]['summary_text']

            # Cleanup
            os.remove(filepath)

            return jsonify({
                'transcript': transcription,
                'summary': summary
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)