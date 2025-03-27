Emotion-Based Character Chat System
Overview
A conversational AI system that lets you:

Extract characters from text/PDFs

Chat with characters that remember past conversations

See real-time emotional responses visualized

Ask about other users' interactions

Quick Start
Install Requirements

bash
Copy
# Backend (Python 3.8+)
pip install -r requirements.txt

# Frontend (Node.js 16+)
npm install
Set Up Environment
Create .env file:

Copy
GOOGLE_API_KEY=your_key_here
FLASK_SECRET_KEY=any_random_string
Run the System

bash
Copy
# Start backend
python app.py

# In another terminal
npm start

How to Use
Extract Characters

Paste text or upload a PDF

Click "Extract" to identify characters

Chat with Characters

Select a character

Type messages and watch their emotions change

Ask things like "Do you remember user_123?"

View Emotions

Real-time emotion circle visualization

Detailed Psi Theory parameters

Key Features
✨ Smart Character Extraction - Pulls characters from any text
💬 Adaptive Conversations - Responses change based on emotional state
🧠 Cross-User Memory - Remembers past interactions with other users
📊 Emotion Visualization - See feelings evolve during chats

Troubleshooting
"Session not found" → Refresh the page

Emotion not updating → Try more emotional language

Extraction fails → Check file is PDF/TXT format

Note: Requires Google API key for Gemini AI functionality