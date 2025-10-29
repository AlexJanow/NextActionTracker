import React, { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import DatePicker from 'react-datepicker';

import { opportunitiesApi, Opportunity, CompleteActionRequest, ApiError } from '../services/api';
import { useToast } from '../contexts/ToastContext';
import FieldError from './FieldError';
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
  const [touched, setTouched] = useState<{ date?: boolean; details?: boolean }>({});
  const { showError } = useToast();

  // Set default date to tomorrow
  useEffect(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setNewActionDate(tomorrow);
  }, []);

  const handleQuickSelect = (interval: 'week' | '2weeks' | 'month') => {
    const today = new Date();
    let futureDate: Date;

    switch (interval) {
      case 'week':
        futureDate = new Date(today);
        futureDate.setDate(today.getDate() + 7);
        break;
      case '2weeks':
        futureDate = new Date(today);
        futureDate.setDate(today.getDate() + 14);
        break;
      case 'month':
        futureDate = new Date(today);
        futureDate.setMonth(today.getMonth() + 1);
        break;
    }

    setNewActionDate(futureDate);
    setTouched(prev => ({ ...prev, date: true }));
  };

  const mutation = useMutation({
    mutationFn: (data: CompleteActionRequest) =>
      opportunitiesApi.completeAction(opportunity.id, data),
    onSuccess: () => {
      onActionCompleted();
    },
    onError: (error: ApiError) => {
      console.error('Failed to complete action:', error);
      
      // Show specific error message based on error type
      if (error.status === 422) {
        showError('Please check your input and try again');
      } else if (error.status === 404) {
        showError('This opportunity could not be found');
      } else {
        showError(error.message || 'Failed to complete action. Please try again.');
      }
    },
  });

  const validateForm = (): boolean => {
    const newErrors: { date?: string; details?: string } = {};

    if (!newActionDate) {
      newErrors.date = 'Please select a date for the next action';
    } else {
      // Validate that the date is today or in the future
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const selectedDate = new Date(newActionDate);
      selectedDate.setHours(0, 0, 0, 0);
      
      if (selectedDate < today) {
        newErrors.date = 'Next action date must be today or in the future';
      }
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
              onChange={(date: Date | null) => {
                setNewActionDate(date);
                setTouched(prev => ({ ...prev, date: true }));
              }}
              onBlur={() => setTouched(prev => ({ ...prev, date: true }))}
              dateFormat="MMMM d, yyyy"
              minDate={new Date()}
              placeholderText="Select a date"
              className={errors.date && touched.date ? 'field-error' : ''}
            />
            
            {/* Quick-select buttons */}
            <div style={{ 
              display: 'flex', 
              gap: '8px', 
              marginTop: '10px' 
            }}>
              <button
                type="button"
                onClick={() => handleQuickSelect('week')}
                className="btn"
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  fontSize: '14px',
                  backgroundColor: '#ecf0f1',
                  color: '#2c3e50',
                  border: '1px solid #bdc3c7',
                }}
                disabled={mutation.isPending}
              >
                +1 Week
              </button>
              <button
                type="button"
                onClick={() => handleQuickSelect('2weeks')}
                className="btn"
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  fontSize: '14px',
                  backgroundColor: '#ecf0f1',
                  color: '#2c3e50',
                  border: '1px solid #bdc3c7',
                }}
                disabled={mutation.isPending}
              >
                +2 Weeks
              </button>
              <button
                type="button"
                onClick={() => handleQuickSelect('month')}
                className="btn"
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  fontSize: '14px',
                  backgroundColor: '#ecf0f1',
                  color: '#2c3e50',
                  border: '1px solid #bdc3c7',
                }}
                disabled={mutation.isPending}
              >
                +1 Month
              </button>
            </div>
            
            <FieldError error={errors.date} touched={touched.date} />
          </div>

          <div className="form-group">
            <label htmlFor="nextActionDetails">
              What is the next action to take? *
            </label>
            <textarea
              id="nextActionDetails"
              value={newActionDetails}
              onChange={(e) => {
                setNewActionDetails(e.target.value);
                setTouched(prev => ({ ...prev, details: true }));
              }}
              onBlur={() => setTouched(prev => ({ ...prev, details: true }))}
              placeholder="e.g., Send customized proposal, Schedule demo call, Follow up on pricing questions..."
              className={errors.details && touched.details ? 'field-error' : ''}
            />
            <FieldError error={errors.details} touched={touched.details} />
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