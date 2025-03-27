import React from 'react';
import EmotionVisualization from './EmotionVisualization';

const ChatSection = ({
  selectedCharacter,
  messages,
  newMessage,
  setNewMessage,
  sendMessage,
  isLoading,
  psiState,
  getPsiState
}) => {
  return (
    <section className="chat-section">
      <div className="chat-header">
        <h2>Chat with {selectedCharacter}</h2>
        {/* <button
          onClick={getPsiState}
          className="refresh-state"
          disabled={isLoading}
        >
          Refresh Emotion State
        </button> */}
      </div>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.length > 0 ? (
            messages.map((msg, index) => (
              <div
                key={index}
                className={`message ${msg.sender === 'user' ? 'user-message' : 'character-message'}`}
              >
                <div className="message-sender">{msg.sender}:</div>
                <div className="message-text">{msg.text}</div>
              </div>
            ))
          ) : (
            <p className="empty-chat">Start a conversation with {selectedCharacter}</p>
          )}
        </div>

        {psiState && <EmotionVisualization psiState={psiState} />}
      </div>

      <div className="message-input">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder={`Message ${selectedCharacter}...`}
          onKeyPress={(e) => e.key === 'Enter' && !isLoading && sendMessage()}
          disabled={isLoading}
        />
        <button
          onClick={sendMessage}
          disabled={isLoading || !newMessage.trim()}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </section>
  );
};

export default ChatSection;