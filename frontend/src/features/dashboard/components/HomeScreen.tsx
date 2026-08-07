import { User } from '../../auth';
import { Group, GroupCard, useUserGroups } from '../../groups';

export interface HomeScreenProps {
  user: User;
  onSelectGroup: (group: Group) => void;
}

export default function HomeScreen({ user, onSelectGroup }: HomeScreenProps) {
  const { groups, isLoading, errorMsg } = useUserGroups(user.id);

  return (
    <div className="home-screen">
      <div className="user-avatar">👤</div>
      <h1 className="title">
        {user.name ? `${user.name}(${user.username})` : user.username}님, 환영합니다! 🎉
      </h1>
      <p className="subtitle">참여 중인 그룹을 선택해서 경기 이력을 확인해 보세요.</p>

      {isLoading && <p className="subtitle">그룹 목록을 불러오는 중...</p>}
      {!isLoading && errorMsg && <div className="error-message">{errorMsg}</div>}

      {!isLoading && !errorMsg && groups.length === 0 && (
        <p className="subtitle">
          아직 가입한 그룹이 없습니다.
          <br />
          마이페이지에서 그룹을 만들거나 참여해 보세요.
        </p>
      )}

      {!isLoading && !errorMsg && groups.length > 0 && (
        <div className="group-card-grid">
          {groups.map((group) => (
            <GroupCard key={group.group_key} group={group} onClick={() => onSelectGroup(group)} />
          ))}
        </div>
      )}
    </div>
  );
}
