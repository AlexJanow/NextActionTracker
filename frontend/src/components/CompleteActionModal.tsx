import React, { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import DatePicker from 'react-datepicker';

import { opportunitiesApi, Opportunity, CompleteActionRequest } from '../services/api';
import 'react-datepicker/dist/react-datepicker.css';

interface CompleteActionModalProps {
  opportunity: Opportunity;
  onClose: () => void;
  onActionCompleted: () => void;
}

const CompleteActionModal: React.FC<CompleteActionModalProps> = ({
  opportunity,
  onClose,
  onActionCompleted,
}) => {
  const [newActionDate, setNewActionDate] = useState<Date | null>(null);
  const [newActionDetails, setNewActionDetails] = useState('');
  const [errors, setErrors] = useState<{ date?: string; details?: string }>({});

  // Set default date to tomorrow
  useEffect(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setNewActionDate(tomorrow);
  }, []);

  const mutation = useMutation({
    mutationFn: (data: CompleteActionRequest) =>
      opportunitiesApi.completeAction(opportunity.id, data),
    onSuccess: () => {
      onActionCompleted();
    },
    onError: (error: any) => {
      console.error('Failed to complete action:', error);
    },
  });

  const validateForm = (): boolean => {
    const newErrors: { date?: string; details?: string } = {};

    if (!newActionDate) {
      newErrors.date = 'Please select a date for the next action';
    } else if (newActionDate < new Date()) {
      newErrors.date = 'Next action date cannot be in the past';
    }

    if (!newActionDetails.trim()) {
      newErrors.details = 'Please describe the next action';
    } else if (newActionDetails.trim().length < 5) {
      newErrors.details = 'Action description must be at least 5 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    if (newActionDate) {
      const data: CompleteActionRequest = {
        new_next_action_at: newActionDate.toISOString(),
        new_next_action_details: newActionDetails.trim(),
      };

      mutation.mutate(data);
    }
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal">
        <h2>Complete Action</h2>
        
        <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
          <h4 style={{ margin: '0 0 8px 0', color: '#2c3e50' }}>{opportunity.name}</h4>
          <p style={{ margin: '0', color: '#7f8c8d', fontSize: '14px' }}>
            Current action: {opportunity.next_action_details || 'No details'}
          </p>
        </div>

        {mutation.error && (
          <div className="error" style={{ marginBottom: '20px' }}>
            <p>Failed to complete action. Please try again.</p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="nextActionDate">
              When should the next action be completed? *
            </label>
            <DatePicker
              id="nextActionDate"
              selected={newActionDate}
              onChange={(date: Date | null) => setNewActionDate(date)}
              dateFormat="MMMM d, yyyy"
              minDate={new Date()}
              placeholderText="Select a date"
              className={errors.date ? 'error' : ''}
            />
            {errors.date && <div className="form-error">{errors.date}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="nextActionDetails">
              What is the next action to take? *
            </label>
            <textarea
              id="nextActionDetails"
              value={newActionDetails}
              onChange={(e) => setNewActionDetails(e.target.value)}
              placeholder="e.g., Send customized proposal, Schedule demo call, Follow up on pricing questions..."
              className={errors.details ? 'error' : ''}
              style={{
                border: errors.details ? '2px solid #e74c3c' : undefined,
              }}
            />
            {errors.details && <div className="form-error">{errors.details}</div>}
          </div>

          <div className="flex justify-between gap-10">
            <button
              type="button"
              onClick={onClose}
              className="btn"
              style={{
                backgroundColor: '#95a5a6',
                color: 'white',
                flex: 1,
              }}
              disabled={mutation.isPending}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={mutation.isPending}
              style={{ flex: 1 }}
            >
              {mutation.isPending ? (
                <span className="flex align-center justify-center gap-10">
                  <div 
                    className="spinner" 
                    style={{ 
                      width: '16px', 
                      height: '16px', 
                      borderWidth: '2px' 
                    }}
                  />
                  Completing...
                </span>
              ) : (
                'Complete & Set Next Action'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CompleteActionModal;