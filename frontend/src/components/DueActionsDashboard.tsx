import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { opportunitiesApi, Opportunity } from '../services/api';
import DueActionCard from './DueActionCard';
import CompleteActionModal from './CompleteActionModal';
import ErrorBoundary from './ErrorBoundary';
import LoadingSkeleton from './LoadingSkeleton';

const DueActionsDashboard: React.FC = () => {
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const {
    data: opportunities = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['dueOpportunities'],
    queryFn: opportunitiesApi.getDueOpportunities,
  });

  const handleCompleteAction = (opportunity: Opportunity) => {
    setSelectedOpportunity(opportunity);
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setSelectedOpportunity(null);
  };

  const handleActionCompleted = () => {
    refetch();
    handleModalClose();
  };

  if (isLoading) {
    return (
      <div>
        <h2 className="mb-20">Due Actions</h2>
        <LoadingSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h2 className="mb-20">Due Actions</h2>
        <div className="error">
          <p>Failed to load due actions. Please try again.</p>
          <button 
            className="btn btn-primary" 
            onClick={() => refetch()}
            style={{ marginTop: '10px' }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (opportunities.length === 0) {
    return (
      <div>
        <h2 className="mb-20">Due Actions</h2>
        <div className="empty-state">
          <h2>All done! 🎉</h2>
          <p>You have no actions due today. Great work staying on top of your pipeline!</p>
        </div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div>
        <h2 className="mb-20">Due Actions ({opportunities.length})</h2>
        
        <div>
          {opportunities.map((opportunity) => (
            <DueActionCard
              key={opportunity.id}
              opportunity={opportunity}
              onCompleteAction={handleCompleteAction}
            />
          ))}
        </div>

        {isModalOpen && selectedOpportunity && (
          <CompleteActionModal
            opportunity={selectedOpportunity}
            onClose={handleModalClose}
            onActionCompleted={handleActionCompleted}
          />
        )}
      </div>
    </ErrorBoundary>
  );
};

export default DueActionsDashboard;