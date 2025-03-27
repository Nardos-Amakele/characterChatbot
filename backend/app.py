from flask import Flask, request, jsonify, session
from flask_cors import CORS
from character_manager import CharacterManager
from emotion_engine import EmotionEngine
import os
import uuid
from werkzeug.utils import secure_filename
import PyPDF2
from io import BytesIO

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-secret-key")

# Initialize components
manager = CharacterManager()
emotion_engine = EmotionEngine()

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file):
    """Extract text from PDF using PyPDF2"""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

@app.route('/extract', methods=['POST'])
def extract():
    """Handle text/PDF extraction and character storage"""
    if 'text' in request.json:
        text = request.json['text']
    elif 'file' in request.files:
        file = request.files['file']
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400
        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        else:
            text = file.read().decode('utf-8')
    else:
        return jsonify({"error": "No text or file provided"}), 400

    user_id = request.json.get('user_id', str(uuid.uuid4()))
    
    try:
        characters = manager.extract_characters(text)
        session[user_id] = {
            "characters": characters,
            "psi_state": emotion_engine.base_state
        }
        return jsonify({
            "characters": characters,
            "user_id": user_id,
            "psi_state": emotion_engine.base_state
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    required = ['character', 'message', 'user_id']
    if not all(k in data for k in required):
        return jsonify({"error": f"Missing fields: {required}"}), 400

    user_id = data['user_id']
    if user_id not in session:
        return jsonify({"error": "User session not found"}), 404

    try:
        message = data['message'].lower()
        
        # Detect any variation of "do you know [user]?" question
        if any([
            'do you know' in message,
            'have you met' in message,
            'have you talked to' in message,
            'recognize' in message,
            'remember' in message
        ]):
            # Extract username using more flexible pattern
            import re
            username_match = re.search(
                r'(know|met|talked to|recognize|remember)\s+(?:user_)?([a-z0-9]+)', 
                message,
                re.IGNORECASE
            )
            
            asked_user = username_match.group(2) if username_match else None
            
            if asked_user:
                # Get current psi state before handling recognition
                current_psi_state = session[user_id]["psi_state"]
                recognition_response = manager.handle_user_recognition(
                    data['character'], 
                    asked_user, 
                    user_id
                )
                return jsonify({
                    "response": recognition_response,
                    "psi_state": current_psi_state,
                    "user_id": user_id
                })

        # Rest of normal chat processing...
        character = next(
            (c for c in session[user_id]["characters"] if c["name"] == data["character"]),
            None
        )
        if not character:
            return jsonify({"error": "Character not found"}), 404

        response, new_psi_state = manager.generate_response(
            character=data['character'],
            message=data['message'],
            user_id=user_id,
            emotion_engine=emotion_engine
        )
        
        session[user_id]["psi_state"] = new_psi_state
        return jsonify({
            "response": response,
            "psi_state": new_psi_state,
            "user_id": user_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@app.route('/get_psi_state/<user_id>', methods=['GET'])
def get_psi_state(user_id):
    """Fetch current Psi state for UI"""
    if user_id in session:
        return jsonify(session[user_id]["psi_state"])
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)