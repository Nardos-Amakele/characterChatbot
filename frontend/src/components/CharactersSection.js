import React from 'react';

const CharactersSection = ({
  characters,
  selectedCharacter,
  setSelectedCharacter,
  setMessages
}) => {
  return (
    <section className="characters-section">
      <h2>Extracted Characters</h2>
      <div className="character-cards">
        {characters.map((char, index) => (
          <div
            key={index}
            className={`character-card ${selectedCharacter === char.name ? 'selected' : ''}`}
            onClick={() => {
              setSelectedCharacter(char.name);
              setMessages([]);
            }}
          >
            <h3>{char.name}</h3>
            <p>{char.description}</p>
            <div className="traits">
              {char.traits.map((trait, i) => (
                <span key={i} className="trait-badge">{trait}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default CharactersSection;