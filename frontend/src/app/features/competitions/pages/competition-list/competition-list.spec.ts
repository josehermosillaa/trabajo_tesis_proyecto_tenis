import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';

import { TokenService, UserRole } from '../../../../core/services/token';
import { CompetitionService } from '../../services/competition';
import { CompetitionListComponent } from './competition-list';

describe('CompetitionListComponent role actions', () => {
  let fixture: ComponentFixture<CompetitionListComponent>;
  let token: jasmine.SpyObj<TokenService>;
  let router: jasmine.SpyObj<Router>;

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
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
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

  it('shows friendly competition values without changing the source data', () => {
    createForRole('Administrador');
    const rowText = fixture.nativeElement.querySelector('.competition-row').textContent;

    expect(rowText).toContain('Escalerilla');
    expect(rowText).toContain('Abierta');
    expect(fixture.componentInstance.competitions[0].type).toBe('ESCALERILLA');
    expect(fixture.componentInstance.competitions[0].status).toBe('ABIERTA');
  });

  it('keeps row, edit, delete and categories actions independent', () => {
    createForRole('Administrador');
    const row = fixture.nativeElement.querySelector('.competition-row') as HTMLTableRowElement;

    row.querySelector('td')?.click();
    expect(router.navigate).toHaveBeenCalledOnceWith(['/competitions', 1, 'categories']);

    router.navigate.calls.reset();
    buttonNamed('Editar').click();
    expect(router.navigate).toHaveBeenCalledOnceWith(['/competitions', 1, 'edit']);

    router.navigate.calls.reset();
    buttonNamed('Categorías').click();
    expect(router.navigate).toHaveBeenCalledOnceWith(['/competitions', 1, 'categories']);

    router.navigate.calls.reset();
    buttonNamed('Eliminar').click();
    expect(router.navigate).not.toHaveBeenCalled();
    expect(fixture.componentInstance.showDeleteModal).toBeTrue();
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

  function buttonNamed(label: string): HTMLButtonElement {
    return Array.from<HTMLButtonElement>(fixture.nativeElement.querySelectorAll('button'))
      .find((button) => button.textContent?.trim() === label) as HTMLButtonElement;
  }
});
