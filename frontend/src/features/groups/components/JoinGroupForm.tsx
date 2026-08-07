import React from 'react';
import { useJoinGroup } from '../hooks/useJoinGroup';

export interface JoinGroupFormProps {
  onJoined?: () => void;
}

export default function JoinGroupForm({ onJoined }: JoinGroupFormProps) {
  const { groupKey, setGroupKey, errorMsg, successMsg, isLoading, joinGroup } = useJoinGroup(onJoined);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    joinGroup();
  };

  return (
    <div className="mypage-section">
      <h2 className="section-title">그룹 참여하기</h2>

      {errorMsg && <div className="error-message">{errorMsg}</div>}
      {successMsg && <div className="info-message">{successMsg}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="join-group-key">그룹 코드</label>
          <div className="input-wrapper">
            <input
              id="join-group-key"
              type="text"
              placeholder="참여할 그룹의 코드를 입력하세요"
              value={groupKey}
              onChange={(e) => setGroupKey(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? '참여 중...' : '그룹 참여하기'}
        </button>
      </form>
    </div>
  );
}
