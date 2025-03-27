import React from 'react';

const ExtractionSection = ({
  textInput,
  setTextInput,
  file,
  handleFileChange,
  extractCharacters,
  isLoading
}) => {
  return (
    <section className="extraction-section">
      <h2>Extract Characters</h2>
      <div className="input-group">
        <textarea
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          placeholder="Paste your text here..."
          rows={5}
        />
        <div className="or-divider">OR</div>
        <div className="file-upload">
          <input
            type="file"
            onChange={handleFileChange}
            accept=".txt,.pdf"
            id="file-upload"
          />
          <label htmlFor="file-upload" className="file-upload-label">
            {file ? file.name : 'Choose File'}
          </label>
        </div>
      </div>
      <button
        onClick={extractCharacters}
        disabled={isLoading || (!textInput && !file)}
      >
        {isLoading ? 'Processing...' : 'Extract Characters'}
      </button>
    </section>
  );
};

export default ExtractionSection;