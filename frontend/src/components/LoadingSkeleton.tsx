import React from 'react';

const LoadingSkeleton: React.FC = () => {
  return (
    <div>
      {[1, 2, 3].map((index) => (
        <div key={index} className="card" style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ flex: 1 }}>
              {/* Opportunity name skeleton */}
              <div 
                style={{
                  height: '20px',
                  backgroundColor: '#ecf0f1',
                  borderRadius: '4px',
                  marginBottom: '12px',
                  width: '60%',
                  animation: 'pulse 1.5s ease-in-out infinite alternate'
                }}
              />
              
              {/* Value and stage skeleton */}
              <div style={{ display: 'flex', gap: '20px', marginBottom: '12px' }}>
                <div 
                  style={{
                    height: '16px',
                    backgroundColor: '#ecf0f1',
                    borderRadius: '4px',
                    width: '80px',
                    animation: 'pulse 1.5s ease-in-out infinite alternate'
                  }}
                />
                <div 
                  style={{
                    height: '16px',
                    backgroundColor: '#ecf0f1',
                    borderRadius: '4px',
                    width: '100px',
                    animation: 'pulse 1.5s ease-in-out infinite alternate'
                  }}
                />
              </div>
              
              {/* Next action skeleton */}
              <div 
                style={{
                  height: '16px',
                  backgroundColor: '#ecf0f1',
                  borderRadius: '4px',
                  width: '80%',
                  animation: 'pulse 1.5s ease-in-out infinite alternate'
                }}
              />
            </div>
            
            {/* Button skeleton */}
            <div 
              style={{
                height: '36px',
                width: '120px',
                backgroundColor: '#ecf0f1',
                borderRadius: '6px',
                animation: 'pulse 1.5s ease-in-out infinite alternate'
              }}
            />
          </div>
        </div>
      ))}
      
      <style>{`
        @keyframes pulse {
          0% {
            opacity: 1;
          }
          100% {
            opacity: 0.4;
          }
        }
      `}</style>
    </div>
  );
};

export default LoadingSkeleton;