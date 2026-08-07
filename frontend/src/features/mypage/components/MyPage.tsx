import { useState } from 'react';
import { User } from '../../auth';
import { CreateGroupForm, JoinGroupForm } from '../../groups';
import ChangePasswordForm from './ChangePasswordForm';
import GroupList from './GroupList';

export interface MyPageProps {
  user: User;
}

export default function MyPage({ user }: MyPageProps) {
  const [groupsVersion, setGroupsVersion] = useState<number>(0);
  const refreshGroups = () => setGroupsVersion((v) => v + 1);

  return (
    <div className="mypage-screen">
      <div className="user-avatar">👤</div>
      <h1 className="title">{user.name ? `${user.name}(${user.username})` : user.username}</h1>
      <p className="subtitle">내 정보와 가입한 그룹을 관리하세요.</p>

      <GroupList key={groupsVersion} userId={user.id} />
      <CreateGroupForm onCreated={refreshGroups} />
      <JoinGroupForm onJoined={refreshGroups} />
      <ChangePasswordForm />
    </div>
  );
}
