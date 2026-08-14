import { useState } from 'react';
import { User } from '../../auth';
import { CreateGroupForm, JoinGroupForm } from '../../groups';
import ChangePasswordForm from './ChangePasswordForm';
import GroupList from './GroupList';

type MyPageView = 'menu' | 'groups' | 'create-group' | 'join-group' | 'password';

interface MenuItem {
  view: Exclude<MyPageView, 'menu'>;
  icon: string;
  label: string;
  desc: string;
}

const MENU_ITEMS: MenuItem[] = [
  { view: 'groups', icon: '👥', label: '등록된 그룹', desc: '가입한 그룹 목록과 그룹 코드를 확인해요.' },
  { view: 'create-group', icon: '➕', label: '새 그룹 만들기', desc: '새로운 동호회/모임을 만들어요.' },
  { view: 'join-group', icon: '🔑', label: '그룹 참여하기', desc: '코드를 입력해 기존 그룹에 참여해요.' },
  { view: 'password', icon: '🔒', label: '비밀번호 변경', desc: '계정 비밀번호를 변경해요.' },
];

export interface MyPageProps {
  user: User;
}

export default function MyPage({ user }: MyPageProps) {
  const [view, setView] = useState<MyPageView>('menu');
  const [groupsVersion, setGroupsVersion] = useState<number>(0);
  const refreshGroups = () => setGroupsVersion((v) => v + 1);

  return (
    <div className="mypage-screen">
      <div className="user-avatar">👤</div>
      <h1 className="title">{user.name ? `${user.name}(${user.username})` : user.username}</h1>
      <p className="subtitle">내 정보와 가입한 그룹을 관리하세요.</p>

      {view !== 'menu' && (
        <button type="button" className="btn-back mypage-back" onClick={() => setView('menu')}>
          ← 메뉴로
        </button>
      )}

      {view === 'menu' && (
        <ul className="mypage-menu">
          {MENU_ITEMS.map((item) => (
            <li key={item.view}>
              <button type="button" className="mypage-menu-item" onClick={() => setView(item.view)}>
                <span className="mypage-menu-item-icon">{item.icon}</span>
                <span className="mypage-menu-item-text">
                  <span className="mypage-menu-item-label">{item.label}</span>
                  <span className="mypage-menu-item-desc">{item.desc}</span>
                </span>
                <span className="mypage-menu-item-arrow">›</span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {view === 'groups' && <GroupList key={groupsVersion} userId={user.id} />}
      {view === 'create-group' && <CreateGroupForm onCreated={refreshGroups} />}
      {view === 'join-group' && <JoinGroupForm onJoined={refreshGroups} />}
      {view === 'password' && <ChangePasswordForm />}
    </div>
  );
}
