import React from 'react';
import { PlayerCard, PlayerData, CardLayout } from './PlayerCard.js';

export interface OperatorData {
  id: string;
  name: string;
  full_art: string;
  card_crop?: string;
  art_transform?: {
    scale?: number;
    x?: number;
    y?: number;
  };
}

export interface SceneManifest {
  canvas?: {
    width: number;
    height: number;
  };
  operator: OperatorData;
  players: Record<string, PlayerData>;
}

export interface LayoutSpec {
  canvas: { width: number; height: number };
  title: CardLayout;
  P1: CardLayout;
  P2: CardLayout;
  P3: CardLayout;
  P4: CardLayout;
  P5: CardLayout;
  operator: CardLayout;
}

interface ReportSceneProps {
  manifest: SceneManifest;
  layout: LayoutSpec;
  assetBaseUrl?: string;
}

export const ReportScene: React.FC<ReportSceneProps> = ({
  manifest,
  layout,
  assetBaseUrl = '',
}) => {
  const op = manifest.operator;
  const fullArtUrl = op.full_art.startsWith('http') || op.full_art.startsWith('file://')
    ? op.full_art
    : `${assetBaseUrl}${op.full_art.replace(/^\.\.\//, '')}`;

  const cardCropUrl = op.card_crop
    ? (op.card_crop.startsWith('http') || op.card_crop.startsWith('file://')
        ? op.card_crop
        : `${assetBaseUrl}${op.card_crop.replace(/^\.\.\//, '')}`)
    : fullArtUrl;

  const playerKeys = ['P1', 'P2', 'P3', 'P4', 'P5'] as const;

  // 干员立绘微调变换 (共享规范)
  const transform = op.art_transform;
  const artStyle: React.CSSProperties = transform ? {
    transform: `translate(${transform.x ?? 0}px, ${transform.y ?? 0}px) scale(${transform.scale ?? 1})`,
  } : {};

  return (
    <div className="report-scene" id="ROOT_REPORT_SCENE">
      {/* 战术网格背景 */}
      <div className="tactical-grid" />

      {/* 顶部战术标题栏 */}
      <div className="scene-header">
        <div className="header-main-title">ARKNIGHTS OPERATOR REPORT</div>
        <div className="header-sub-title">明日方舟六星干员报菜名 · 五人战术核验系统</div>
      </div>

      {/* 中央干员全画幅立绘 */}
      <div className="operator-full-art-container">
        <img
          src={fullArtUrl}
          alt={op.name}
          className="operator-full-art"
          style={artStyle}
        />
      </div>

      {/* 五位玩家信息卡片 (复用单一 PlayerCard 组件) */}
      {playerKeys.map((pKey) => {
        const playerData = manifest.players[pKey];
        const playerLayout = layout[pKey];
        if (!playerData || !playerLayout) return null;

        return (
          <PlayerCard
            key={pKey}
            playerKey={pKey}
            player={playerData}
            layout={playerLayout}
            operatorCardCrop={cardCropUrl}
            assetBaseUrl={assetBaseUrl}
          />
        );
      })}
    </div>
  );
};
