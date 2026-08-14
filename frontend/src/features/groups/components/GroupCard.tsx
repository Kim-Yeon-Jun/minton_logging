import React from 'react';
import { CopyButton } from '../../../components';
import { Group } from '../types/group.types';

export interface GroupCardProps {
  group: Group;
  onClick: () => void;
}

export default function GroupCard({ group, onClick }: GroupCardProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick();
    }
  };

  return (
    <div className="group-card" role="button" tabIndex={0} onClick={onClick} onKeyDown={handleKeyDown}>
      <div className="group-card-name">{group.group_name}</div>
      {group.description && <div className="group-card-desc">{group.description}</div>}
      <div className="group-card-code" onClick={(e) => e.stopPropagation()}>
        <CopyButton value={group.group_key} label="그룹 코드 복사" variant="text" />
      </div>
      <div className="group-card-meta">멤버 {group.member_count}명</div>
    </div>
  );
}
