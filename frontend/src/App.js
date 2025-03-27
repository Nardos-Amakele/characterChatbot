import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import ExtractionSection from './components/ExtractionSection';
import CharactersSection from './components/CharactersSection';
import ChatSection from './components/ChatSection';
import ErrorMessage from './components/ErrorMessage';

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:5000';
axios.defaults.withCredentials = true;

function App() {
  const [textInput, setTextInput] = useState('');
  const [file, setFile] = useState(null);
  const [characters, setCharacters] = useState([]);
  const [selectedCharacter, setSelectedCharacter] = useState('');
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [userId, setUserId] = useState('');
  const [psiState, setPsiState] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Initialize user session
  useEffect(() => {
    const initializeSession = async () => {
      const storedUserId = localStorage.getItem('userId');
      if (storedUserId) {
        try {
          const response = await axios.get(`/get_psi_state/${storedUserId}`);
          setUserId(storedUserId);
          setPsiState(response.data);
        } catch (err) {
          createNewSession();
        }
      } else {
        createNewSession();
      }
    };

    const createNewSession = () => {
      const newUserId = `user_${Date.now()}`;
      setUserId(newUserId);
      localStorage.setItem('userId', newUserId);
    };

    initializeSession();
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const extractCharacters = async () => {
    setIsLoading(true);
    setError('');
    try {
      let response;

      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', userId);

        response = await axios.post('/extract', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      } else if (textInput) {
        response = await axios.post('/extract', {
          text: textInput,
          user_id: userId
        });
      } else {
        throw new Error('Please provide either text or a file');
      }

      setCharacters(response.data.characters);
      setPsiState(response.data.psi_state);

      if (response.data.user_id) {
        setUserId(response.data.user_id);
        localStorage.setItem('userId', response.data.user_id);
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);

      if (err.response?.status === 404 || err.response?.data?.error?.includes('session')) {
        localStorage.removeItem('userId');
        const newUserId = `user_${Date.now()}`;
        setUserId(newUserId);
        localStorage.setItem('userId', newUserId);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!selectedCharacter || !newMessage.trim()) return;

    setIsLoading(true);
    setError('');
    try {
      const response = await axios.post('/chat', {
        character: selectedCharacter,
        message: newMessage,
        user_id: userId
      });

      setMessages(prev => [
        ...prev,
        { sender: 'user', text: newMessage },
        { sender: selectedCharacter, text: response.data.response }
      ]);

      setPsiState({
        ...response.data.psi_state,
        updated: Date.now()
      });

      setNewMessage('');
    } catch (err) {
      setError(err.response?.data?.error || err.message);

      if (err.response?.status === 404) {
        const newUserId = `user_${Date.now()}`;
        setUserId(newUserId);
        localStorage.setItem('userId', newUserId);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getPsiState = async () => {
    try {
      const response = await axios.get(`/get_psi_state/${userId}`);
      setPsiState(response.data);
    } catch (err) {
      console.error('Error fetching Psi state:', err);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>Character Emotion Chat System</h1>
        {/* {userId && <p className="user-id">User ID: {userId}</p>} */}
      </header>

      <div className="main-content">
        <ExtractionSection 
          textInput={textInput}
          setTextInput={setTextInput}
          file={file}
          handleFileChange={handleFileChange}
          extractCharacters={extractCharacters}
          isLoading={isLoading}
        />

        {characters.length > 0 && (
          <CharactersSection 
            characters={characters}
            selectedCharacter={selectedCharacter}
            setSelectedCharacter={setSelectedCharacter}
            setMessages={setMessages}
          />
        )}

        {selectedCharacter && (
          <ChatSection 
            selectedCharacter={selectedCharacter}
            messages={messages}
            newMessage={newMessage}
            setNewMessage={setNewMessage}
            sendMessage={sendMessage}
            isLoading={isLoading}
            psiState={psiState}
            getPsiState={getPsiState}
          />
        )}

        {error && (
          <ErrorMessage error={error} setError={setError} />
        )}
      </div>
    </div>
  );
}

export default App;