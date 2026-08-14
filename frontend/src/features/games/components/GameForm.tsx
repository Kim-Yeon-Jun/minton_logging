import React from 'react';
import { GroupMember, useGroupMembers } from '../../groups';
import { Team, useGameForm } from '../hooks/useGameForm';
import { Game } from '../types/game.types';

export interface GameFormProps {
  groupKey: string;
  existingGame?: Game;
  onSaved: () => void;
}

export default function GameForm({ groupKey, existingGame, onSaved }: GameFormProps) {
  const { members, isLoading: membersLoading, errorMsg: membersError } = useGroupMembers(groupKey);
  const {
    gameType,
    setGameType,
    slotsPerTeam,
    courtNumber,
    setCourtNumber,
    videoUrl,
    setVideoUrl,
    playedAt,
    setPlayedAt,
    teamASlots,
    teamBSlots,
    setSlot,
    teamAScore,
    setTeamAScore,
    teamBScore,
    setTeamBScore,
    errorMsg,
    isLoading,
    isEditMode,
    save,
  } = useGameForm(groupKey, existingGame, onSaved);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    save();
  };

  const selectedIds = new Set([...teamASlots, ...teamBSlots].filter(Boolean));

  const renderSlot = (team: Team, index: number, value: string) => {
    const availableMembers = members.filter(
      (m: GroupMember) => m.user_id === value || !selectedIds.has(m.user_id)
    );

    return (
      <div className="form-group" key={`${team}-${index}`}>
        <label htmlFor={`${team}-slot-${index}`}>
          {team}팀{slotsPerTeam > 1 ? ` ${index + 1}` : ''}
        </label>
        <div className="input-wrapper">
          <select
            id={`${team}-slot-${index}`}
            value={value}
            onChange={(e) => setSlot(team, index, e.target.value)}
            disabled={isLoading}
          >
            <option value="">선택 안 함</option>
            {availableMembers.map((member) => (
              <option key={member.user_id} value={member.user_id}>
                {member.name ? `${member.name}(${member.username})` : member.username}
              </option>
            ))}
          </select>
        </div>
      </div>
    );
  };

  return (
    <div className="mypage-section">
      <h2 className="section-title">{isEditMode ? '경기 수정' : '경기 등록'}</h2>

      {membersError && <div className="error-message">{membersError}</div>}
      {errorMsg && <div className="error-message">{errorMsg}</div>}

      {membersLoading ? (
        <p className="subtitle">그룹 멤버를 불러오는 중...</p>
      ) : members.length === 0 ? (
        <p className="subtitle">그룹에 멤버가 없습니다.</p>
      ) : (
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="played-at">경기 일시</label>
            <div className="input-wrapper">
              <input
                id="played-at"
                type="datetime-local"
                value={playedAt}
                onChange={(e) => setPlayedAt(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="game-type">경기 종류</label>
            <div className="input-wrapper">
              <select
                id="game-type"
                value={gameType}
                onChange={(e) => setGameType(e.target.value)}
                disabled={isLoading}
              >
                <option value="singles">단식</option>
                <option value="doubles">복식</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="court-number">코트 번호 (선택)</label>
            <div className="input-wrapper">
              <input
                id="court-number"
                type="number"
                min="1"
                placeholder="코트 번호"
                value={courtNumber}
                onChange={(e) => setCourtNumber(e.target.value)}
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="video-url">경기 영상 링크 (선택)</label>
            <div className="input-wrapper">
              <input
                id="video-url"
                type="url"
                placeholder="https://www.youtube.com/watch?v=..."
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="team-slot-columns">
            <div className="team-slot-column">
              <div className="team-slot-column-title">A팀</div>
              {teamASlots.slice(0, slotsPerTeam).map((value, index) => renderSlot('A', index, value))}
              <div className="form-group">
                <label htmlFor="team-a-score">A팀 점수</label>
                <div className="input-wrapper">
                  <input
                    id="team-a-score"
                    type="number"
                    min="0"
                    value={teamAScore}
                    onChange={(e) => setTeamAScore(e.target.value)}
                    disabled={isLoading}
                  />
                </div>
              </div>
            </div>

            <div className="team-slot-column">
              <div className="team-slot-column-title">B팀</div>
              {teamBSlots.slice(0, slotsPerTeam).map((value, index) => renderSlot('B', index, value))}
              <div className="form-group">
                <label htmlFor="team-b-score">B팀 점수</label>
                <div className="input-wrapper">
                  <input
                    id="team-b-score"
                    type="number"
                    min="0"
                    value={teamBScore}
                    onChange={(e) => setTeamBScore(e.target.value)}
                    disabled={isLoading}
                  />
                </div>
              </div>
            </div>
          </div>

          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? '저장 중...' : isEditMode ? '수정 사항 저장' : '경기 등록'}
          </button>
        </form>
      )}
    </div>
  );
}
