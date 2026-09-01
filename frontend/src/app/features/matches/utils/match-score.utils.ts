import { MatchResolutionType, MatchSetSummary } from '../models/match.model';

export interface MatchScoreSource {
  resolution_type: MatchResolutionType;
  is_walkover?: boolean;
  sets?: readonly MatchSetSummary[];
}

export function formatMatchScore(match: MatchScoreSource, reversePlayers = false): string {
  if (match.resolution_type === 'WALKOVER' || match.is_walkover) {
    return 'WO';
  }

  const score = [...(match.sets ?? [])]
    .sort((left, right) => left.set_number - right.set_number)
    .map((set) => {
      const firstScore = reversePlayers ? set.games_player2 : set.games_player1;
      const secondScore = reversePlayers ? set.games_player1 : set.games_player2;
      const setScore = `${firstScore}–${secondScore}`;
      return set.is_super_tie_break ? `[${setScore}]` : setScore;
    })
    .join(' | ');

  if (match.resolution_type === 'RETIREMENT') {
    return score ? `${score} RET` : 'RET';
  }

  return score;
}
