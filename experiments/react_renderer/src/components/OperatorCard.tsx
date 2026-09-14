import React from 'react';
import { EliteBadge } from './EliteBadge.js';
import { PotentialBadge } from './PotentialBadge.js';

interface OperatorCardProps {
  cardCropUrl: string;
  level: number;
  elite: number;
  potential: number;
  assetBaseUrl?: string;
}

export const OperatorCard: React.FC<OperatorCardProps> = ({
  cardCropUrl,
  level,
  elite,
  potential,
  assetBaseUrl = '',
}) => {
  return (
    <div className="operator-card-panel">
      {/* 干员半身卡面裁切图 */}
      <div className="operator-crop-wrapper">
        <img src={cardCropUrl} alt="Operator Card" className="operator-crop-img" />
      </div>

      {/* 渐变遮罩保护可读性 */}
      <div className="operator-card-overlay" />

      {/* 右上角状态徽章 */}
      <div className="badges-container">
        <EliteBadge value={elite} assetBaseUrl={assetBaseUrl} />
        <PotentialBadge value={potential} assetBaseUrl={assetBaseUrl} />
      </div>

      {/* 左下角等级 */}
      <div className="level-info-container">
        <span className="level-label">LV.</span>
        <span className="level-number">{level}</span>
      </div>
    </div>
  );
};
