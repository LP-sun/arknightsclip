import React from 'react';

interface EliteBadgeProps {
  value: number;
  assetBaseUrl?: string;
}

export const EliteBadge: React.FC<EliteBadgeProps> = ({ value, assetBaseUrl = '' }) => {
  const eliteVal = Math.max(0, Math.min(2, value ?? 0));
  const src = `${assetBaseUrl}assets/ui/elite_${eliteVal}.png`;

  return (
    <img 
      src={src} 
      alt={`Elite ${eliteVal}`} 
      className="badge-icon elite-badge" 
    />
  );
};
