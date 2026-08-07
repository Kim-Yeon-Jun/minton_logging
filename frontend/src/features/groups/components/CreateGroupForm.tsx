import React from 'react';
import { useCreateGroup } from '../hooks/useCreateGroup';

export interface CreateGroupFormProps {
  onCreated?: () => void;
}

export default function CreateGroupForm({ onCreated }: CreateGroupFormProps) {
  const {
    groupName,
    setGroupName,
    description,
    setDescription,
    errorMsg,
    successMsg,
    isLoading,
    createGroup,
  } = useCreateGroup(onCreated);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    createGroup();
  };

  return (
    <div className="mypage-section">
      <h2 className="section-title">새 그룹 만들기</h2>

      {errorMsg && <div className="error-message">{errorMsg}</div>}
      {successMsg && <div className="info-message">{successMsg}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="new-group-name">그룹 이름</label>
          <div className="input-wrapper">
            <input
              id="new-group-name"
              type="text"
              placeholder="동호회/모임 이름을 입력하세요"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="new-group-desc">설명 (선택)</label>
          <div className="input-wrapper">
            <input
              id="new-group-desc"
              type="text"
              placeholder="그룹 소개를 입력하세요"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isLoading}
            />
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? '생성 중...' : '그룹 만들기'}
        </button>
      </form>
    </div>
  );
}
