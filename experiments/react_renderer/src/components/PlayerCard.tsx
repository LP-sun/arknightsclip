import React from 'react';
import { DoctorInfo } from './DoctorInfo.js';
import { OperatorCard } from './OperatorCard.js';
import { NoInfo } from './NoInfo.js';

export interface PlayerData {
  display_name: string;
  doctor_title?: string;
  doctor_level: number;
  avatar: string;
  own: boolean;
  elite?: number;
  level?: number;
  potential?: number;
}

export interface CardLayout {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface PlayerCardProps {
  playerKey: string;
  player: PlayerData;
  layout: CardLayout;
  operatorCardCrop: string;
  assetBaseUrl?: string;
}

export const PlayerCard: React.FC<PlayerCardProps> = ({
  playerKey,
  player,
  layout,
  operatorCardCrop,
  assetBaseUrl = '',
}) => {
  const avatarUrl = player.avatar.startsWith('http') || player.avatar.startsWith('file://')
    ? player.avatar
    : `${assetBaseUrl}${player.avatar.replace(/^\.\.\//, '')}`;

  const cropUrl = operatorCardCrop.startsWith('http') || operatorCardCrop.startsWith('file://')
    ? operatorCardCrop
    : `${assetBaseUrl}${operatorCardCrop.replace(/^\.\.\//, '')}`;

  const style: React.CSSProperties = {
    left: `${layout.x}px`,
    top: `${layout.y}px`,
    width: `${layout.width}px`,
    height: `${layout.height}px`,
  };

  return (
    <div className={`player-card player-card-${playerKey}`} style={style} id={playerKey}>
      {/* 博士通用信息栏 */}
      <DoctorInfo
        avatarUrl={avatarUrl}
        name={player.display_name}
        level={player.doctor_level}
      />

      {/* 状态条件渲染 */}
      {player.own ? (
        <OperatorCard
          cardCropUrl={cropUrl}
          level={player.level ?? 90}
          elite={player.elite ?? 2}
          potential={player.potential ?? 1}
          assetBaseUrl={assetBaseUrl}
        />
      ) : (
        <NoInfo />
      )}
    </div>
  );
};
