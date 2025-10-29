import React from 'react';
import { format, parseISO, isToday, isPast } from 'date-fns';
import { Opportunity } from '../services/api';

interface DueActionCardProps {
  opportunity: Opportunity;
  onCompleteAction: (opportunity: Opportunity) => void;
}

const DueActionCard: React.FC<DueActionCardProps> = ({ 
  opportunity, 
  onCompleteAction 
}) => {
  const formatCurrency = (value: number | null): string => {
    if (value === null) return 'No value set';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatDueDate = (dateString: string): { text: string; isOverdue: boolean } => {
    const date = parseISO(dateString);
    const isOverdue = isPast(date) && !isToday(date);
    
    if (isToday(date)) {
      return { text: 'Due today', isOverdue: false };
    } else if (isOverdue) {
      const daysOverdue = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24));
      return { 
        text: `${daysOverdue} day${daysOverdue === 1 ? '' : 's'} overdue`, 
        isOverdue: true 
      };
    } else {
      return { text: format(date, 'MMM d, yyyy'), isOverdue: false };
    }
  };

  const dueInfo = formatDueDate(opportunity.next_action_at);

  return (
    <div className="card">
      <div className="flex justify-between align-center">
        <div style={{ flex: 1 }}>
          {/* Opportunity header */}
          <div className="flex align-center gap-10" style={{ marginBottom: '12px' }}>
            <h3 style={{ 
              fontSize: '1.2rem', 
              fontWeight: '600', 
              color: '#2c3e50',
              margin: 0 
            }}>
              {opportunity.name}
            </h3>
            {dueInfo.isOverdue && (
              <span style={{
                backgroundColor: '#e74c3c',
                color: 'white',
                padding: '2px 8px',
                borderRadius: '12px',
                fontSize: '12px',
                fontWeight: '500'
              }}>
                OVERDUE
              </span>
            )}
          </div>

          {/* Opportunity details */}
          <div className="flex gap-10" style={{ marginBottom: '12px' }}>
            <div>
              <span style={{ color: '#7f8c8d', fontSize: '14px' }}>Value: </span>
              <span style={{ fontWeight: '500', color: '#2c3e50' }}>
                {formatCurrency(opportunity.value)}
              </span>
            </div>
            <div>
              <span style={{ color: '#7f8c8d', fontSize: '14px' }}>Stage: </span>
              <span style={{ fontWeight: '500', color: '#2c3e50' }}>
                {opportunity.stage}
              </span>
            </div>
          </div>

          {/* Due date */}
          <div style={{ marginBottom: '12px' }}>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>Due: </span>
            <span style={{ 
              fontWeight: '500', 
              color: dueInfo.isOverdue ? '#e74c3c' : '#2c3e50' 
            }}>
              {dueInfo.text}
            </span>
          </div>

          {/* Next action details */}
          <div>
            <span style={{ color: '#7f8c8d', fontSize: '14px' }}>Next Action: </span>
            <span style={{ fontWeight: '500', color: '#2c3e50' }}>
              {opportunity.next_action_details || 'No details provided'}
            </span>
          </div>
        </div>

        {/* Complete Action button */}
        <button
          className="btn btn-primary"
          onClick={() => onCompleteAction(opportunity)}
          style={{ marginLeft: '20px' }}
        >
          Complete Action
        </button>
      </div>
    </div>
  );
};

export default DueActionCard;