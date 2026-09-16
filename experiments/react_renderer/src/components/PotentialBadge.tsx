import React from 'react';

interface PotentialBadgeProps {
  value: number;
  assetBaseUrl?: string;
}

export const PotentialBadge: React.FC<PotentialBadgeProps> = ({ value, assetBaseUrl = '' }) => {
  const potVal = Math.max(1, Math.min(6, value ?? 1));
  const src = `${assetBaseUrl}assets/ui/potential_${potVal}.png`;

  return (
    <img 
      src={src} 
      alt={`Potential ${potVal}`} 
      className="badge-icon potential-badge" 
    />
  );
};
