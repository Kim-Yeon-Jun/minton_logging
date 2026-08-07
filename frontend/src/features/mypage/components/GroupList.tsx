import { CopyButton } from '../../../components';
import { useUserGroups } from '../../groups';

export interface GroupListProps {
  userId: string;
}

export default function GroupList({ userId }: GroupListProps) {
  const { groups, isLoading, errorMsg } = useUserGroups(userId);

  return (
    <div className="mypage-section">
      <h2 className="section-title">등록된 그룹</h2>

      {isLoading && <p className="subtitle">그룹 목록을 불러오는 중...</p>}
      {!isLoading && errorMsg && <div className="error-message">{errorMsg}</div>}

      {!isLoading && !errorMsg && groups.length === 0 && (
        <p className="subtitle">아직 가입한 그룹이 없습니다.</p>
      )}

      {!isLoading && !errorMsg && groups.length > 0 && (
        <ul className="group-list">
          {groups.map((group) => (
            <li key={group.group_key} className="group-item">
              <div className="group-item-name">{group.group_name}</div>
              {group.description && (
                <div className="group-item-desc">{group.description}</div>
              )}
              <div className="group-item-code">
                <span className="group-item-code-label">그룹 코드</span>
                <span className="group-item-code-value">{group.group_key}</span>
                <CopyButton value={group.group_key} label="그룹 코드 복사하기" />
              </div>
              <div className="group-item-meta">멤버 {group.member_count}명</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
