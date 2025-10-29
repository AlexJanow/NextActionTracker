import React from 'react';

interface FieldErrorProps {
  error?: string;
  touched?: boolean;
}

const FieldError: React.FC<FieldErrorProps> = ({ error, touched }) => {
  if (!error || !touched) {
    return null;
  }

  return (
    <div className="field-error-message">
      {error}
    </div>
  );
};

export default FieldError;