import { useEffect, useRef, useState } from 'react';

export interface MonthPickerProps {
  value: string; // "YYYY-MM"
  onChange: (value: string) => void;
}

const MONTHS = Array.from({ length: 12 }, (_, i) => i + 1);

function parseYearMonth(value: string): { year: number; month: number } {
  const [year, month] = value.split('-').map(Number);
  return { year, month };
}

function formatYearMonth(value: string): string {
  const { year, month } = parseYearMonth(value);
  return `${year}년 ${month}월`;
}

export default function MonthPicker({ value, onChange }: MonthPickerProps) {
  const { year, month } = parseYearMonth(value);
  const [isOpen, setIsOpen] = useState(false);
  const [viewYear, setViewYear] = useState(year);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) setViewYear(year);
  }, [isOpen, year]);

  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen]);

  const handleSelectMonth = (m: number) => {
    onChange(`${viewYear}-${String(m).padStart(2, '0')}`);
    setIsOpen(false);
  };

  return (
    <div className="month-picker" ref={containerRef}>
      <button
        type="button"
        className="month-picker-trigger"
        aria-haspopup="dialog"
        aria-expanded={isOpen}
        onClick={() => setIsOpen((prev) => !prev)}
      >
        <span>{formatYearMonth(value)}</span>
        <span className={`dropdown-chevron${isOpen ? ' dropdown-chevron-open' : ''}`}>▾</span>
      </button>

      {isOpen && (
        <div className="month-picker-popover">
          <div className="month-picker-year-nav">
            <button
              type="button"
              className="month-picker-year-btn"
              onClick={() => setViewYear((y) => y - 1)}
              aria-label="이전 해"
            >
              ‹
            </button>
            <span className="month-picker-year-label">{viewYear}년</span>
            <button
              type="button"
              className="month-picker-year-btn"
              onClick={() => setViewYear((y) => y + 1)}
              aria-label="다음 해"
            >
              ›
            </button>
          </div>

          <div className="month-picker-grid">
            {MONTHS.map((m) => (
              <button
                key={m}
                type="button"
                className={`month-picker-cell${
                  viewYear === year && m === month ? ' month-picker-cell-active' : ''
                }`}
                onClick={() => handleSelectMonth(m)}
              >
                {m}월
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
