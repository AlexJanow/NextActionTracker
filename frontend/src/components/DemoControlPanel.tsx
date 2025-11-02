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
      showSuccess('Demo data reset successfully!');
      setShowResetModal(false);
    },
    onError: (error: ApiError) => {
      console.error('Failed to reset demo data:', error);
      showError(error.message || 'Failed to reset demo data. Please try again.');
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
            <h2>Reset Demo Data</h2>
            
            <div className="modal-content">
              <p>This will reset all demo data to its initial state.</p>
              <p className="modal-warning">
                <strong>Warning:</strong> All current opportunities and actions will be replaced with fresh demo data.
              </p>
              <p>Are you sure you want to proceed?</p>
            </div>

            {mutation.error && (
              <div className="error" style={{ marginBottom: '20px' }}>
                <p>Failed to reset demo data. Please try again.</p>
              </div>
            )}

            <div className="flex justify-between gap-10">
              <button
                type="button"
                onClick={handleCancel}
                className="btn btn-secondary"
                disabled={mutation.isPending}
              >
                Cancel
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
                    Resetting...
                  </span>
                ) : (
                  'Reset Demo Data'
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

