import React, { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import DatePicker from 'react-datepicker';
import { de } from 'date-fns/locale';

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
        showError('Bitte überprüfen Sie Ihre Eingaben und versuchen Sie es erneut');
      } else if (error.status === 404) {
        showError('Diese Opportunity konnte nicht gefunden werden');
      } else {
        showError(error.message || 'Aktion konnte nicht abgeschlossen werden. Bitte versuchen Sie es erneut.');
      }
    },
  });

  const validateForm = (): boolean => {
    const newErrors: { date?: string; details?: string } = {};

    if (!newActionDate) {
      newErrors.date = 'Bitte wählen Sie ein Datum für die nächste Aktion';
    } else {
      // Validate that the date is today or in the future
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const selectedDate = new Date(newActionDate);
      selectedDate.setHours(0, 0, 0, 0);
      
      if (selectedDate < today) {
        newErrors.date = 'Das Datum der nächsten Aktion muss heute oder in der Zukunft liegen';
      }
    }

    if (!newActionDetails.trim()) {
      newErrors.details = 'Bitte beschreiben Sie die nächste Aktion';
    } else if (newActionDetails.trim().length < 5) {
      newErrors.details = 'Die Aktionsbeschreibung muss mindestens 5 Zeichen lang sein';
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
        <h2>Aktion abschließen</h2>
        
        <div className="modal-opportunity-info">
          <h4 className="modal-opportunity-name">{opportunity.name}</h4>
          <p className="modal-opportunity-details">
            Aktuelle Aktion: {opportunity.next_action_details || 'Keine Details'}
          </p>
        </div>

        {mutation.error && (
          <div className="error" style={{ marginBottom: '20px' }}>
            <p>Aktion konnte nicht abgeschlossen werden. Bitte versuchen Sie es erneut.</p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="nextActionDate">
              Wann soll die nächste Aktion abgeschlossen werden? *
            </label>
            <DatePicker
              id="nextActionDate"
              selected={newActionDate}
              onChange={(date: Date | null) => {
                setNewActionDate(date);
                setTouched(prev => ({ ...prev, date: true }));
              }}
              onBlur={() => setTouched(prev => ({ ...prev, date: true }))}
              dateFormat="d. MMMM yyyy"
              minDate={new Date()}
              placeholderText="Datum auswählen"
              locale={de}
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
                className="btn quick-select-button"
                disabled={mutation.isPending}
              >
                +1 Woche
              </button>
              <button
                type="button"
                onClick={() => handleQuickSelect('2weeks')}
                className="btn quick-select-button"
                disabled={mutation.isPending}
              >
                +2 Wochen
              </button>
              <button
                type="button"
                onClick={() => handleQuickSelect('month')}
                className="btn quick-select-button"
                disabled={mutation.isPending}
              >
                +1 Monat
              </button>
            </div>
            
            <FieldError error={errors.date} touched={touched.date} />
          </div>

          <div className="form-group">
            <label htmlFor="nextActionDetails">
              Was ist die nächste Aktion? *
            </label>
            <textarea
              id="nextActionDetails"
              value={newActionDetails}
              onChange={(e) => {
                setNewActionDetails(e.target.value);
                setTouched(prev => ({ ...prev, details: true }));
              }}
              onBlur={() => setTouched(prev => ({ ...prev, details: true }))}
              placeholder="z.B. Individuelles Angebot versenden, Demo-Call vereinbaren, Preisfragen klären..."
              className={errors.details && touched.details ? 'field-error' : ''}
            />
            <FieldError error={errors.details} touched={touched.details} />
          </div>

          <div className="flex justify-between gap-10">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
              disabled={mutation.isPending}
            >
              Abbrechen
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
                  Wird abgeschlossen...
                </span>
              ) : (
                'Abschließen & Nächste Aktion festlegen'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CompleteActionModal;