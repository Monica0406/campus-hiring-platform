import React from 'react';

const AlertMessage = ({ type = 'danger', message, onClose }) => {
  if (!message) return null;

  return (
    <div className={`alert alert-${type} alert-dismissible fade show my-3`} role="alert">
      <div>{message}</div>
      {onClose && (
        <button
          type="button"
          className="btn-close"
          aria-label="Close"
          onClick={onClose}
        ></button>
      )}
    </div>
  );
};

export default AlertMessage;
