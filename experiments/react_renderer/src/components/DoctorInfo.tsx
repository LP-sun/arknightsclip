import React from 'react';

interface DoctorInfoProps {
  avatarUrl: string;
  name: string;
  level: number;
}

export const DoctorInfo: React.FC<DoctorInfoProps> = ({ avatarUrl, name, level }) => {
  return (
    <div className="doctor-info-panel">
      <div className="doctor-avatar-wrapper">
        <img src={avatarUrl} alt={name} className="doctor-avatar-img" />
      </div>
      <div className="doctor-name-text" title={name}>
        {name}
      </div>
      <div className="doctor-level-text">
        LV. {level}
      </div>
    </div>
  );
};
