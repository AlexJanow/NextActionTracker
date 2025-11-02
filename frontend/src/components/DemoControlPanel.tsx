import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { demoApi, ApiError } from '../services/api';
import { useToast } from '../contexts/ToastContext';

interface DemoControlPanelProps {
  // Optional: You can add props later if needed
}

const DemoControlPanel: React.FC<DemoControlPanelProps> = () => {
  const [showResetModal, setShowResetModal] = useState(false);
  const { showError, showSuccess } = useToast();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () => demoApi.resetDemoData(),
    onSuccess: () => {
      // Invalidate and refetch all queries
      queryClient.invalidateQueries({ queryKey: ['dueOpportunities'] });
      showSuccess('Demo-Daten erfolgreich zurückgesetzt!');
      setShowResetModal(false);
    },
    onError: (error: ApiError) => {
      console.error('Failed to reset demo data:', error);
      showError(error.message || 'Demo-Daten konnten nicht zurückgesetzt werden. Bitte versuchen Sie es erneut.');
    },
  });

  const handleResetClick = () => {
    setShowResetModal(true);
  };

  const handleConfirmReset = () => {
    mutation.mutate();
  };

  const handleCancel = () => {
    setShowResetModal(false);
  };

  return (
    <>
      {/* Floating action button */}
      <div className="demo-control-button" onClick={handleResetClick}>
        <span className="demo-control-icon">🎬</span>
        <span className="demo-control-label">Demo</span>
      </div>

      {/* Reset confirmation modal */}
      {showResetModal && (
        <div className="modal-overlay" onClick={handleCancel}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Demo-Daten zurücksetzen</h2>
            
            <div className="modal-content">
              <p>Dies setzt alle Demo-Daten auf den Ausgangszustand zurück.</p>
              <p className="modal-warning">
                <strong>Warnung:</strong> Alle aktuellen Opportunities und Aktionen werden durch neue Demo-Daten ersetzt.
              </p>
              <p>Möchten Sie wirklich fortfahren?</p>
            </div>

            {mutation.error && (
              <div className="error" style={{ marginBottom: '20px' }}>
                <p>Demo-Daten konnten nicht zurückgesetzt werden. Bitte versuchen Sie es erneut.</p>
              </div>
            )}

            <div className="flex justify-between gap-10">
              <button
                type="button"
                onClick={handleCancel}
                className="btn btn-secondary"
                disabled={mutation.isPending}
              >
                Abbrechen
              </button>
              <button
                type="button"
                onClick={handleConfirmReset}
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
                    Wird zurückgesetzt...
                  </span>
                ) : (
                  'Demo-Daten zurücksetzen'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default DemoControlPanel;

