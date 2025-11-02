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

  const getUrgencyColor = (nextActionAt: string): string => {
    const actionDate = new Date(nextActionAt);
    const today = new Date();
    
    // Reset time to midnight for accurate day comparison
    today.setHours(0, 0, 0, 0);
    actionDate.setHours(0, 0, 0, 0);
    
    const daysOverdue = Math.floor((today.getTime() - actionDate.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysOverdue > 3) return 'var(--overdue-red)'; // red - high urgency
    if (daysOverdue >= 1) return 'var(--medium-urgency-yellow)'; // yellow - medium urgency
    return 'var(--today-blue)'; // blue - due today
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
  const urgencyColor = getUrgencyColor(opportunity.next_action_at);

  return (
    <div className="card" style={{ borderLeft: `4px solid ${urgencyColor}` }}>
      <div className="flex justify-between align-center">
        <div style={{ flex: 1 }}>
          {/* Opportunity header */}
          <div className="flex align-center gap-10" style={{ marginBottom: '12px' }}>
            <h3 className="action-card-title">
              {opportunity.name}
            </h3>
            {dueInfo.isOverdue && (
              <span className="overdue-badge">
                OVERDUE
              </span>
            )}
          </div>

          {/* Opportunity details */}
          <div className="flex gap-10" style={{ marginBottom: '12px' }}>
            <div>
              <span className="action-label">Value: </span>
              <span className="action-value">
                {formatCurrency(opportunity.value)}
              </span>
            </div>
            <div>
              <span className="action-label">Stage: </span>
              <span className="action-value">
                {opportunity.stage}
              </span>
            </div>
          </div>

          {/* Due date */}
          <div style={{ marginBottom: '12px' }}>
            <span className="action-label">Due: </span>
            <span className={dueInfo.isOverdue ? 'action-due-overdue' : 'action-due-normal'}>
              {dueInfo.text}
            </span>
          </div>

          {/* Next action details */}
          <div>
            <span className="action-label">Next Action: </span>
            <span className="action-value">
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