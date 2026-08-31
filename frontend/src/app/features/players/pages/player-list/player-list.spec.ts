import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';

import { TokenService, UserRole } from '../../../../core/services/token';
import { PlayerService } from '../../services/player';
import { PlayerListComponent } from './player-list';

describe('PlayerListComponent role and search', () => {
  let fixture: ComponentFixture<PlayerListComponent>;
  let component: PlayerListComponent;
  let tokenService: jasmine.SpyObj<TokenService>;
  const players = [
    { id: 2, user: 12, username: 'ana', email: 'ana@example.com', category: 2,
      rut: '22.222.222-2', first_name: 'Ana', last_name: 'Zulueta', birth_date: null, phone: '' },
    { id: 1, user: 11, username: 'jose', email: 'jose@example.com', category: 1,
      rut: '11.111.111-1', first_name: 'José', last_name: 'Álvarez', birth_date: null, phone: '' },
  ];

  beforeEach(async () => {
    const service = jasmine.createSpyObj<PlayerService>(
      'PlayerService', ['getCategories', 'getPlayers', 'deletePlayer']
    );
    service.getCategories.and.returnValue(of([
      { id: 1, name: 'PRIMERA' }, { id: 2, name: 'SEGUNDA' },
    ]));
    service.getPlayers.and.returnValue(of(players));
    service.deletePlayer.and.returnValue(of(undefined));
    tokenService = jasmine.createSpyObj<TokenService>(
      'TokenService', ['isAdministrativeUser', 'isAdminUser']
    );
    const router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    await TestBed.configureTestingModule({
      imports: [PlayerListComponent],
      providers: [
        { provide: PlayerService, useValue: service },
        { provide: TokenService, useValue: tokenService },
        { provide: Router, useValue: router },
      ],
    }).compileComponents();
  });

  it('searches by name and RUT case-insensitively and clears to all', () => {
    createForRole('Administrador');
    component.searchTerm = 'JOSÉ';
    expect(component.filteredPlayers.map((item) => item.id)).toEqual([1]);
    component.searchTerm = '22.222';
    expect(component.filteredPlayers.map((item) => item.id)).toEqual([2]);
    component.searchTerm = '  ';
    expect(component.filteredPlayers.map((item) => item.id)).toEqual([1, 2]);
  });

  it('shows delete to Administrador and edit to both administrative roles', () => {
    createForRole('Administrador');
    expect(buttonTexts()).toContain('Eliminar');
    expect(buttonTexts()).toContain('Editar');
    fixture.destroy();
    createForRole('Organizador');
    expect(buttonTexts()).not.toContain('Eliminar');
    expect(buttonTexts()).toContain('Editar');
  });

  it('shows an explicit no-results message', () => {
    createForRole('Administrador');
    component.searchTerm = 'nadie';
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('No se encontraron jugadores.');
  });

  function createForRole(role: UserRole): void {
    tokenService.isAdministrativeUser.and.returnValue(true);
    tokenService.isAdminUser.and.returnValue(role === 'Administrador');
    fixture = TestBed.createComponent(PlayerListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }

  function buttonTexts(): string[] {
    return Array.from(fixture.nativeElement.querySelectorAll('button'))
      .map((item: unknown) => (item as HTMLButtonElement).textContent?.trim() ?? '');
  }
});
