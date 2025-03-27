import React from 'react';

const EmotionVisualization = ({ psiState }) => {
  const emotionColors = {
    anger: '#ff0000',
    sadness: '#0000ff',
    joy: '#ffff00',
    bliss: '#00ff00',
    pride: '#ff00ff',
    neutral: '#cccccc'
  };

  const emotionSize = {
    anger: 120,
    sadness: 100,
    joy: 110,
    bliss: 90,
    pride: 80,
    neutral: 70
  };

  return (
    <div className="emotion-visualization">
      <h3>Character Emotional State</h3>
      {/* <div
        className="emotion-circle"
        style={{
          backgroundColor: emotionColors[psiState.emotion],
          width: `${emotionSize[psiState.emotion]}px`,
          height: `${emotionSize[psiState.emotion]}px`
        }}
      >
        {psiState.emotion}
      </div> */}
      <div className="psi-parameters">
        <h4>Psi Parameters:</h4>
        <ul>
          {Object.entries(psiState).map(([key, value]) => {
            if (key === 'emotion') return null;
            return (
              <li key={key}>
                <strong>{key}:</strong> {typeof value === 'number' ? value.toFixed(2) : value}
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
};

export default EmotionVisualization;