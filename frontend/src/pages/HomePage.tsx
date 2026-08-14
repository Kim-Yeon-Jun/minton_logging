import { useState } from 'react';
import { TopBar, TopBarView } from '../components';
import { User } from '../features/auth';
import { HomeScreen } from '../features/dashboard';
import { Group } from '../features/groups';
import { MyPage } from '../features/mypage';
import GroupPage from './GroupPage';

export interface HomePageProps {
  user: User;
  onLogout: () => void;
}

export default function HomePage({ user, onLogout }: HomePageProps) {
  const [view, setView] = useState<TopBarView>('home');
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null);

  const handleNavigate = (nextView: TopBarView) => {
    if (nextView === 'home') {
      setSelectedGroup(null);
    }
    setView(nextView);
  };

  const handleSelectGroup = (group: Group) => {
    setSelectedGroup(group);
    setView('group');
  };

  return (
    <div className="home-page">
      <TopBar activeView={view} onNavigate={handleNavigate} onLogout={onLogout} />
      {view === 'home' && <HomeScreen user={user} onSelectGroup={handleSelectGroup} />}
      {view === 'mypage' && <MyPage user={user} />}
      {view === 'group' && selectedGroup && <GroupPage group={selectedGroup} currentUserId={user.id} />}
    </div>
  );
}
