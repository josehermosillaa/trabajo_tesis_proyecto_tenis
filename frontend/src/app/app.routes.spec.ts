import { routes } from './app.routes';
import { authGuard } from './core/guards/auth-guard';
import { managementGuard } from './core/guards/management-guard';

describe('critical route permissions', () => {
  const managementPaths = [
    'competitions/new',
    'competitions/:id/edit',
    'players/new',
    'players/:id/edit',
    'registrations/new',
    'registrations/:id/edit',
    'matches/new',
    'matches/:id/edit',
    'matches/:id/result',
  ];

  for (const path of managementPaths) {
    it(`protects ${path} as a management route`, () => {
      expect(routes.find((route) => route.path === path)?.canActivate).toEqual([
        managementGuard,
      ]);
    });
  }

  it('keeps competition category detail available to authenticated read-only users', () => {
    expect(routes.find((route) =>
      route.path === 'competitions/:competitionId/categories/:competitionCategoryId'
    )?.canActivate).toEqual([authGuard]);
  });
});
