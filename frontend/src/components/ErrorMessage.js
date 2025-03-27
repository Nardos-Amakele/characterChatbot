import React from 'react';

const ErrorMessage = ({ error, setError }) => {
  return (
    <div className="error-message">
      {error}
      <button onClick={() => setError('')} className="dismiss-error">
        ×
      </button>
    </div>
  );
};

export default ErrorMessage;