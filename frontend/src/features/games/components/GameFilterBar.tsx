import { Dropdown } from '../../../components';
import { GameFilterState, GameSortOrder } from '../types/game.types';
import MonthPicker from './MonthPicker';

const SORT_OPTIONS: { value: GameSortOrder; label: string }[] = [
  { value: 'desc', label: '최신순' },
  { value: 'asc', label: '오래된순' },
];

export interface GameFilterBarProps {
  filters: GameFilterState;
  onChange: (patch: Partial<GameFilterState>) => void;
}

export default function GameFilterBar({ filters, onChange }: GameFilterBarProps) {
  return (
    <div className="game-filter-bar">
      <div className="game-filter-row">
        <div className="game-filter-left">
          <div className="game-filter-mode">
            <button
              type="button"
              className={`game-filter-mode-btn${filters.mode === 'all' ? ' game-filter-mode-btn-active' : ''}`}
              onClick={() => onChange({ mode: 'all' })}
            >
              전체
            </button>
            <button
              type="button"
              className={`game-filter-mode-btn${filters.mode === 'month' ? ' game-filter-mode-btn-active' : ''}`}
              onClick={() => onChange({ mode: 'month' })}
            >
              월별
            </button>
          </div>

          {filters.mode === 'month' && (
            <MonthPicker value={filters.yearMonth} onChange={(yearMonth) => onChange({ yearMonth })} />
          )}
        </div>

        <Dropdown
          value={filters.sort}
          options={SORT_OPTIONS}
          onChange={(sort) => onChange({ sort })}
          ariaLabel="정렬 방식"
        />
      </div>
    </div>
  );
}
