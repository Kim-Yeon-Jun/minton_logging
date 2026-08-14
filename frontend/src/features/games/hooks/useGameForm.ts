import { useState } from 'react';
import { createGameApi, updateGameApi } from '../services/gamesApi';
import { CreateGameRequest, Game, GameParticipantInput } from '../types/game.types';
import { isoToDatetimeLocalValue, nowAsDatetimeLocalValue } from '../utils/datetimeLocal';

export type Team = 'A' | 'B';
export type TeamAssignment = Team | '';

const MAX_SLOTS = 2;

function emptySlots(): string[] {
  return Array(MAX_SLOTS).fill('');
}

function slotsFromGame(game: Game | undefined, team: Team): string[] {
  const slots = emptySlots();
  if (!game) return slots;

  game.participants
    .filter((p) => p.team_color === team)
    .slice(0, MAX_SLOTS)
    .forEach((p, i) => {
      slots[i] = p.user_id;
    });
  return slots;
}

function scoreFromGame(game: Game | undefined, team: Team): string {
  const participant = game?.participants.find((p) => p.team_color === team);
  return participant ? String(participant.score) : '';
}

export function useGameForm(groupKey: string, existingGame: Game | undefined, onSaved: () => void) {
  const isEditMode = !!existingGame;

  const [gameType, setGameTypeState] = useState<string>(existingGame?.game_type ?? 'doubles');
  const [courtNumber, setCourtNumber] = useState<string>(
    existingGame?.court_number ? String(existingGame.court_number) : ''
  );
  const [videoUrl, setVideoUrl] = useState<string>(existingGame?.video_url ?? '');
  const [playedAt, setPlayedAt] = useState<string>(
    existingGame ? isoToDatetimeLocalValue(existingGame.played_at) : nowAsDatetimeLocalValue()
  );
  const [teamASlots, setTeamASlots] = useState<string[]>(slotsFromGame(existingGame, 'A'));
  const [teamBSlots, setTeamBSlots] = useState<string[]>(slotsFromGame(existingGame, 'B'));
  const [teamAScore, setTeamAScore] = useState<string>(scoreFromGame(existingGame, 'A'));
  const [teamBScore, setTeamBScore] = useState<string>(scoreFromGame(existingGame, 'B'));
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const slotsPerTeam = gameType === 'singles' ? 1 : 2;

  const setGameType = (type: string) => {
    setGameTypeState(type);
    setTeamASlots(emptySlots());
    setTeamBSlots(emptySlots());
  };

  const setSlot = (team: Team, index: number, userId: string) => {
    const setter = team === 'A' ? setTeamASlots : setTeamBSlots;
    setter((prev) => {
      const next = [...prev];
      next[index] = userId;
      return next;
    });
  };

  const save = async () => {
    setErrorMsg('');

    const teamAIds = teamASlots.slice(0, slotsPerTeam).filter(Boolean);
    const teamBIds = teamBSlots.slice(0, slotsPerTeam).filter(Boolean);

    if (teamAIds.length < slotsPerTeam || teamBIds.length < slotsPerTeam) {
      setErrorMsg(
        gameType === 'singles'
          ? 'A팀과 B팀에 각각 1명씩 선택해 주세요.'
          : 'A팀과 B팀에 각각 2명씩 선택해 주세요.'
      );
      return;
    }

    const allIds = [...teamAIds, ...teamBIds];
    if (new Set(allIds).size !== allIds.length) {
      setErrorMsg('같은 사람을 여러 칸에 중복 선택할 수 없습니다.');
      return;
    }

    if (!playedAt) {
      setErrorMsg('경기 일시를 입력해 주세요.');
      return;
    }

    const participants: GameParticipantInput[] = [
      ...teamAIds.map((user_id) => ({ user_id, team_color: 'A', score: Number(teamAScore) || 0 })),
      ...teamBIds.map((user_id) => ({ user_id, team_color: 'B', score: Number(teamBScore) || 0 })),
    ];

    setIsLoading(true);

    try {
      if (existingGame) {
        await updateGameApi(existingGame.game_id, {
          game_type: gameType,
          court_number: courtNumber ? Number(courtNumber) : null,
          video_url: videoUrl.trim() || null,
          played_at: playedAt,
          participants,
        });
      } else {
        const request: CreateGameRequest = {
          group_key: groupKey,
          game_type: gameType,
          court_number: courtNumber ? Number(courtNumber) : null,
          video_url: videoUrl.trim() || null,
          played_at: playedAt,
          participants,
        };
        await createGameApi(request);

        setTeamASlots(emptySlots());
        setTeamBSlots(emptySlots());
        setTeamAScore('');
        setTeamBScore('');
        setCourtNumber('');
        setVideoUrl('');
        setPlayedAt(nowAsDatetimeLocalValue());
      }

      onSaved();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg('경기 저장 중 오류가 발생했습니다.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return {
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
  };
}
