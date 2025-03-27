import os
from dotenv import load_dotenv
import chromadb
import google.generativeai as genai
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple

load_dotenv()

class CharacterManager:
    def __init__(self):
        self.chroma = chromadb.PersistentClient(path=".chromadb")
        # Main collection for character data
        self.char_collection = self.chroma.get_or_create_collection("characters")
        # Separate collection for conversation history
        self.conv_collection = self.chroma.get_or_create_collection("conversations")
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract_characters(self, text: str) -> List[Dict]:
        """Extract characters from text using Gemini"""
        prompt = f"""Extract main characters as JSON with:
        - name
        - description
        - 3 personality traits
        
        Example Output: {{
            "characters": [{{
                "name": "Sherlock Holmes",
                "description": "Brilliant detective",
                "traits": ["observant", "logical", "eccentric"]
            }}]
        }}
        
        Text: {text[:2000]}"""
        
        response = self.model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        data = json.loads(response.text)
        for char in data['characters']:
            self._store_character(char)
        return data['characters']

    def _store_character(self, character: Dict) -> None:
        """Store character in ChromaDB"""
        self.char_collection.add(
            documents=[character['description']],
            metadatas=[{
                "name": character['name'],
                "traits": json.dumps(character['traits'])
            }],
            ids=[f"char_{character['name'].lower().replace(' ', '_')}"]
        )

    def generate_response(self, character: str, message: str, user_id: str, 
                         emotion_engine) -> Tuple[str, Optional[Dict]]:
        """
        Generate response with cross-user memory
        Returns: (response_text, psi_state)
        """
        # Normalize inputs
        character = character.strip()
        message = message.strip().lower()
        
        # Check for user recognition queries
        if message.startswith("do you know"):
            asked_user = message[11:].strip().rstrip('?')
            if asked_user:
                return self._handle_user_recognition(character, asked_user, user_id), None
        
        # Get character traits
        traits = self._get_character_traits(character)
        if not traits:
            return f"Sorry, I don't know who {character} is.", None
        
        # Get conversation history (last 3 messages)
        history = self._get_conversation_history(character, user_id, limit=3)
        
        # Generate response
        prompt = self._build_prompt(character, traits, message, history, emotion_engine)
        response = self.model.generate_content(prompt).text
        
        # Update emotional state
        new_psi_state = emotion_engine.update_state(message, traits, history)
        
        # Store conversation
        self._store_conversation(character, user_id, message, response)
        
        return response, new_psi_state

    def _handle_user_recognition(self, character: str, asked_user: str, current_user: str) -> str:
        """Handle 'do you know [user]' queries"""
        # Don't return info about the current user
        if asked_user.lower() == current_user.lower():
            return "That's you! Of course I know you."
            
        # Search for conversations between the character and asked_user
        results = self.conv_collection.query(
            query_texts=[character],
            where={"$and": [
                {"character": {"$eq": character}},
                {"user_id": {"$eq": asked_user}}
            ]},
            n_results=1
        )
        
        if results and results['documents']:
            last_message = str(results['documents'][0]).split("User: ")[-1].split("\n")[0]
            return f"Yes, {asked_user} asked me: '{last_message}'"
        return f"I don't recall talking to {asked_user}."

    def _build_prompt(self, character: str, traits: List[str], message: str, 
                     history: List, emotion_engine) -> str:
        """Construct the LLM prompt"""
        # Safely process history items
        cleaned_history = []
        for item in history:
            if isinstance(item, str):
                cleaned_history.append(item)
            elif isinstance(item, list):
                cleaned_history.extend([str(i) for i in item if i is not None])
        
        history_str = "\n".join(cleaned_history[-3:]) if cleaned_history else "No previous chats"
        
        return f"""As {character} ({', '.join(traits)}), respond to:
Current emotional state: {emotion_engine.base_state['emotion']}
Previous conversation history:
{history_str}

User: {message}
{character}:"""

    def _get_character_traits(self, character_name: str) -> List[str]:
        """Retrieve traits from ChromaDB"""
        result = self.char_collection.get(
            where={"name": {"$eq": character_name}},
            include=["metadatas"]
        )
        if not result['metadatas']:
            return []
        return json.loads(result['metadatas'][0]['traits'])

    def _get_conversation_history(self, character: str, user_id: str, 
                                limit: int = 3) -> List[str]:
        """Fetch past conversations between user and character"""
        results = self.conv_collection.query(
            query_texts=[character],
            where={"$and": [
                {"character": {"$eq": character}},
                {"user_id": {"$eq": user_id}}
            ]},
            n_results=limit
        )
        return [str(doc) for doc in results['documents']] if results and 'documents' in results else []

    def _store_conversation(self, character: str, user_id: str, 
                          message: str, response: str) -> None:
        """Store conversation in ChromaDB"""
        self.conv_collection.add(
            documents=[f"User: {message}\n{character}: {response}"],
            metadatas=[{
                "user_id": user_id,
                "character": character,
                "timestamp": datetime.now().isoformat(),
                "traits": json.dumps(self._get_character_traits(character))
            }],
            ids=[f"conv_{user_id}_{datetime.now().timestamp()}"]
        )

    def get_all_characters(self) -> List[Dict]:
        """Get list of all known characters"""
        chars = self.char_collection.get(include=["metadatas"])
        return [{
            "name": m['name'],
            "traits": json.loads(m['traits'])
        } for m in chars['metadatas'] if 'name' in m and 'traits' in m]