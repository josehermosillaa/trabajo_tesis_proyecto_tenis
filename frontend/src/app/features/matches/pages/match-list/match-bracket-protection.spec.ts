import { Match } from '../../models/match.model';
import { MatchListComponent } from './match-list';

describe('MatchListComponent bracket protection', () => {
  let component: MatchListComponent;

  beforeEach(() => {
    component = Object.create(MatchListComponent.prototype);
    component.competitionCategories = [
      {
        id: 10,
        competition: 20,
        category: 30,
        minimum_players: 2,
        max_players: 16,
        occupied_slots: 0,
        available_slots: 16,
        registered_players: [],
      },
      {
        id: 11,
        competition: 21,
        category: 30,
        minimum_players: 2,
        max_players: 16,
        occupied_slots: 0,
        available_slots: 16,
        registered_players: [],
      },
    ];
    component.competitions = [
      {
        id: 20,
        name: 'Eliminación',
        type: 'ELIMINACION_DIRECTA',
        start_date: '2026-09-01',
        end_date: '2026-09-15',
        registration_deadline: '2026-08-28',
        status: 'EN_CURSO',
      },
      {
        id: 21,
        name: 'Escalerilla',
        type: 'ESCALERILLA',
        start_date: '2026-09-01',
        end_date: '2026-09-15',
        registration_deadline: '2026-08-28',
        status: 'EN_CURSO',
      },
    ];
  });

  it('identifies a generated direct-elimination bracket match', () => {
    expect(component.isGeneratedBracketMatch(match(10, 1))).toBeTrue();
  });

  it('does not classify a manual direct-elimination match as generated', () => {
    expect(component.isGeneratedBracketMatch(match(10, null))).toBeFalse();
  });

  it('does not classify a ladder match as a bracket match', () => {
    expect(component.isGeneratedBracketMatch(match(11, 1))).toBeFalse();
  });

  it('identifies a ladder match only from its real competition type', () => {
    expect(component.isLadderMatch(match(11, null))).toBeTrue();
    expect(component.isLadderMatch(match(10, null))).toBeFalse();
    expect(component.isLadderMatch(match(10, 1))).toBeFalse();
  });

  function match(
    competitionCategory: number,
    bracketPosition: number | null
  ): Match {
    return {
      id: 1,
      competition_category: competitionCategory,
      court: null,
      player1: 1,
      player2: 2,
      winner_player: null,
      scheduled_date_time: null,
      status: 'PROGRAMADO',
      round: 1,
      bracket_position: bracketPosition,
      next_match: null,
      next_match_slot: null,
      is_walkover: false,
      resolution_type: 'NORMAL',
      sets: [],
    };
  }
});
