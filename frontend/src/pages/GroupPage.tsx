import { useState } from 'react';
import {
  DeletedGameList,
  Game,
  GameForm,
  GameHistoryList,
  useGroupGames,
  useTrashedGames,
} from '../features/games';
import { Group } from '../features/groups';
import { GroupStats } from '../features/stats';

export interface GroupPageProps {
  group: Group;
}

type GroupView = 'list' | 'create' | 'edit' | 'trash' | 'stats';

export default function GroupPage({ group }: GroupPageProps) {
  const activeGames = useGroupGames(group.group_key);
  const trashedGames = useTrashedGames(group.group_key);
  const [view, setView] = useState<GroupView>('list');
  const [editingGame, setEditingGame] = useState<Game | null>(null);

  const handleSaved = () => {
    activeGames.refetch();
    setEditingGame(null);
    setView('list');
  };

  const handleEdit = (game: Game) => {
    setEditingGame(game);
    setView('edit');
  };

  const handleTrashChanged = () => {
    trashedGames.refetch();
    activeGames.refetch();
  };

  return (
    <div className="group-page">
      <div className="group-page-header">
        <div>
          <h1 className="title">{group.group_name}</h1>
          {group.description && <p className="subtitle">{group.description}</p>}
        </div>

        {view === 'list' && (
          <button
            type="button"
            className="btn-add-game"
            onClick={() => {
              setEditingGame(null);
              setView('create');
            }}
          >
            + 경기등록
          </button>
        )}
        {(view === 'create' || view === 'edit') && (
          <button type="button" className="btn-back" onClick={() => setView('list')}>
            ← 목록으로
          </button>
        )}
      </div>

      {(view === 'list' || view === 'trash' || view === 'stats') && (
        <div className="group-tabs">
          <button
            type="button"
            className={`group-tab${view === 'list' ? ' group-tab-active' : ''}`}
            onClick={() => setView('list')}
          >
            경기이력
          </button>
          <button
            type="button"
            className={`group-tab${view === 'stats' ? ' group-tab-active' : ''}`}
            onClick={() => setView('stats')}
          >
            통계
          </button>
          <button
            type="button"
            className={`group-tab${view === 'trash' ? ' group-tab-active' : ''}`}
            onClick={() => setView('trash')}
          >
            삭제예정{trashedGames.total > 0 ? ` (${trashedGames.total})` : ''}
          </button>
        </div>
      )}

      {view === 'list' && (
        <GameHistoryList
          games={activeGames.games}
          total={activeGames.total}
          hasMore={activeGames.hasMore}
          isLoading={activeGames.isLoading}
          isLoadingMore={activeGames.isLoadingMore}
          errorMsg={activeGames.errorMsg}
          onLoadMore={activeGames.loadMore}
          onDeleted={handleTrashChanged}
          onEdit={handleEdit}
        />
      )}

      {(view === 'create' || view === 'edit') && (
        <GameForm
          groupKey={group.group_key}
          existingGame={view === 'edit' && editingGame ? editingGame : undefined}
          onSaved={handleSaved}
        />
      )}

      {view === 'stats' && <GroupStats groupKey={group.group_key} />}

      {view === 'trash' && (
        <DeletedGameList
          games={trashedGames.games}
          total={trashedGames.total}
          hasMore={trashedGames.hasMore}
          isLoading={trashedGames.isLoading}
          isLoadingMore={trashedGames.isLoadingMore}
          errorMsg={trashedGames.errorMsg}
          onLoadMore={trashedGames.loadMore}
          onChanged={handleTrashChanged}
        />
      )}
    </div>
  );
}
