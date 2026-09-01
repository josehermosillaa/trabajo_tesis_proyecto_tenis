import { MatchScoreSource, formatMatchScore } from './match-score.utils';

describe('formatMatchScore', () => {
  it('formats a normal 2-0 result', () => {
    expect(formatMatchScore(source([
      set(1, 6, 3),
      set(2, 6, 4),
    ]))).toBe('6–3 | 6–4');
  });

  it('distinguishes a Super Tie-Break', () => {
    expect(formatMatchScore(source([
      set(1, 4, 6),
      set(2, 6, 3),
      set(3, 10, 8, true),
    ]))).toBe('4–6 | 6–3 | [10–8]');
  });

  it('formats walkover without inventing sets', () => {
    expect(formatMatchScore(source([], 'WALKOVER'))).toBe('WO');
  });

  it('preserves real retirement sets and incomplete scores', () => {
    expect(formatMatchScore(source([
      set(1, 6, 4),
      { ...set(2, 2, 1), is_incomplete: true },
    ], 'RETIREMENT'))).toBe('6–4 | 2–1 RET');
  });

  it('formats retirement without sets', () => {
    expect(formatMatchScore(source([], 'RETIREMENT'))).toBe('RET');
  });

  it('can present the second player score first without changing set semantics', () => {
    expect(formatMatchScore(source([set(1, 4, 6)]), true)).toBe('6–4');
  });

  function source(
    sets: MatchScoreSource['sets'],
    resolution_type: MatchScoreSource['resolution_type'] = 'NORMAL'
  ): MatchScoreSource {
    return { resolution_type, is_walkover: false, sets };
  }

  function set(
    set_number: number,
    games_player1: number,
    games_player2: number,
    is_super_tie_break = false
  ) {
    return {
      id: set_number,
      set_number,
      games_player1,
      games_player2,
      is_super_tie_break,
    };
  }
});
