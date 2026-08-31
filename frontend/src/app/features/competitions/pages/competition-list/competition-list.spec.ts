import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';

import { TokenService, UserRole } from '../../../../core/services/token';
import { CompetitionService } from '../../services/competition';
import { CompetitionListComponent } from './competition-list';

describe('CompetitionListComponent role actions', () => {
  let fixture: ComponentFixture<CompetitionListComponent>;
  let token: jasmine.SpyObj<TokenService>;

  beforeEach(async () => {
    const service = jasmine.createSpyObj<CompetitionService>(
      'CompetitionService', ['getCompetitions', 'deleteCompetition']
    );
    service.getCompetitions.and.returnValue(of([{
      id: 1, name: 'Copa', type: 'ESCALERILLA', start_date: '2026-09-01',
      end_date: '2026-09-10', status: 'ABIERTA', registration_deadline: '2026-08-30',
    }]));
    service.deleteCompetition.and.returnValue(of(undefined));
    token = jasmine.createSpyObj<TokenService>(
      'TokenService', ['isAdministrativeUser', 'isAdminUser']
    );
    const router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    await TestBed.configureTestingModule({
      imports: [CompetitionListComponent],
      providers: [
        { provide: CompetitionService, useValue: service },
        { provide: TokenService, useValue: token },
        { provide: Router, useValue: router },
      ],
    }).compileComponents();
  });

  it('shows delete only to Administrador while keeping edit for Organizador', () => {
    createForRole('Administrador');
    expect(buttonTexts()).toContain('Eliminar');
    expect(buttonTexts()).toContain('Editar');
    fixture.destroy();
    createForRole('Organizador');
    expect(buttonTexts()).not.toContain('Eliminar');
    expect(buttonTexts()).toContain('Editar');
    expect(buttonTexts()).toContain('Categorías');
  });

  function createForRole(role: UserRole): void {
    token.isAdministrativeUser.and.returnValue(true);
    token.isAdminUser.and.returnValue(role === 'Administrador');
    fixture = TestBed.createComponent(CompetitionListComponent);
    fixture.detectChanges();
  }

  function buttonTexts(): string[] {
    return Array.from(fixture.nativeElement.querySelectorAll('button'))
      .map((item: unknown) => (item as HTMLButtonElement).textContent?.trim() ?? '');
  }
});
