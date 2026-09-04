import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';

import { TokenService } from '../../../../core/services/token';
import { RegistrationService } from '../../services/registration';
import { RegistrationListComponent } from './registration-list';

describe('RegistrationListComponent order and search', () => {
  let fixture: ComponentFixture<RegistrationListComponent>;
  let component: RegistrationListComponent;

  beforeEach(async () => {
    const service = jasmine.createSpyObj<RegistrationService>('RegistrationService', [
      'getCompetitions', 'getCompetitionCategories', 'getCategories',
      'getPlayers', 'getRegistrations', 'deleteRegistration',
    ]);
    service.getCompetitions.and.returnValue(of([{
      id: 1, name: 'Copa Central', type: 'ESCALERILLA', start_date: '2026-09-01',
      end_date: '2026-09-10', status: 'ABIERTA', registration_deadline: '2026-08-30',
    }]));
    service.getCompetitionCategories.and.returnValue(of([{
      id: 10, competition: 1, category: 5, max_players: 8, minimum_players: 2,
      occupied_slots: 2, available_slots: 6, registered_players: [],
    }]));
    service.getCategories.and.returnValue(of([{ id: 5, name: 'HONOR' }]));
    service.getPlayers.and.returnValue(of([{
      id: 3, user: 13, username: 'maria', email: 'maria@example.com', category: 5,
      rut: '33.333.333-3', first_name: 'María', last_name: 'Pérez', birth_date: null, phone: '',
    }]));
    service.getRegistrations.and.returnValue(of([
      { id: 1, competition_category: 10, player: 3, registration_date: '2026-08-20T10:00:00Z', status: 'PENDIENTE', seed: null },
      { id: 2, competition_category: 10, player: 3, registration_date: '2026-08-22T10:00:00Z', status: 'CONFIRMADA', seed: null },
    ]));
    service.deleteRegistration.and.returnValue(of(undefined));
    const token = jasmine.createSpyObj<TokenService>('TokenService', ['isAdministrativeUser']);
    token.isAdministrativeUser.and.returnValue(true);
    const router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    await TestBed.configureTestingModule({
      imports: [RegistrationListComponent],
      providers: [
        { provide: RegistrationService, useValue: service },
        { provide: TokenService, useValue: token },
        { provide: Router, useValue: router },
      ],
    }).compileComponents();
    fixture = TestBed.createComponent(RegistrationListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('orders by the real registration_date descending', () => {
    expect(component.filteredRegistrations.map((item) => item.id)).toEqual([2, 1]);
  });

  it('searches contextual data and empty term restores all', () => {
    component.searchTerm = 'marÍA';
    expect(component.filteredRegistrations.length).toBe(2);
    component.searchTerm = 'copa central';
    expect(component.filteredRegistrations.length).toBe(2);
    component.searchTerm = 'confirmada';
    expect(component.filteredRegistrations.map((item) => item.id)).toEqual([2]);
    component.searchTerm = '';
    expect(component.filteredRegistrations.length).toBe(2);
  });

  it('shows no-results feedback', () => {
    component.searchTerm = 'inexistente';
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('No se encontraron inscripciones.');
  });

  it('shows the loaded total and keeps search and table inside the list surface', () => {
    const card = fixture.nativeElement.querySelector('.registration-list-card') as HTMLElement;

    expect(card.textContent).toContain('2 inscripciones registradas');
    expect(card.querySelector('#registration-search')).not.toBeNull();
    expect(card.querySelector('table')).not.toBeNull();
    expect(card.querySelector('tbody .badge.text-bg-secondary')?.textContent).toContain('HONOR');
  });
});
