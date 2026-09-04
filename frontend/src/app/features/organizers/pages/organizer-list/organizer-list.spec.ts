import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of } from 'rxjs';

import { OrganizerService } from '../../services/organizer';
import { OrganizerListComponent } from './organizer-list';

describe('OrganizerListComponent', () => {
  let component: OrganizerListComponent;
  let fixture: ComponentFixture<OrganizerListComponent>;
  let service: jasmine.SpyObj<OrganizerService>;
  let router: jasmine.SpyObj<Router>;

  const organizer = {
    id: 7,
    username: 'organizer',
    first_name: 'Organizador',
    last_name: 'Prueba',
    email: 'organizer@example.com',
    is_active: true,
    role: 'Organizador' as const,
  };

  beforeEach(async () => {
    service = jasmine.createSpyObj<OrganizerService>(
      'OrganizerService',
      ['getOrganizers', 'setOrganizerActive']
    );
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    service.getOrganizers.and.returnValue(of([organizer]));
    service.setOrganizerActive.and.returnValue(of({ ...organizer, is_active: false }));

    await TestBed.configureTestingModule({
      imports: [OrganizerListComponent],
      providers: [
        { provide: OrganizerService, useValue: service },
        { provide: Router, useValue: router },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(OrganizerListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('lists organizer data without sensitive information', () => {
    const text = fixture.nativeElement.textContent;
    expect(text).toContain('Organizador Prueba');
    expect(text).toContain('organizer@example.com');
    expect(text).toContain('Activo');
    expect(text).not.toContain('password');
  });

  it('searches organizers by name, username and email', () => {
    const secondOrganizer = {
      ...organizer,
      id: 8,
      username: 'mlopez',
      first_name: 'María',
      last_name: 'López',
      email: 'maria@example.com',
    };
    component.organizers = [organizer, secondOrganizer];

    component.searchTerm = 'maría';
    expect(component.filteredOrganizers).toEqual([secondOrganizer]);

    component.searchTerm = 'organizer';
    expect(component.filteredOrganizers).toEqual([organizer]);

    component.searchTerm = 'maria@example.com';
    expect(component.filteredOrganizers).toEqual([secondOrganizer]);
  });

  it('keeps the total, search and table inside the list surface', () => {
    const card = fixture.nativeElement.querySelector('.organizer-list-card') as HTMLElement;

    expect(card.textContent).toContain('1 organizador registrado');
    expect(card.querySelector('#organizer-search')).not.toBeNull();
    expect(card.querySelector('table')).not.toBeNull();
  });

  it('shows a dash when name or email is empty', () => {
    component.organizers = [{ ...organizer, first_name: '', last_name: '', email: '' }];
    fixture.detectChanges();

    const cells = Array.from<HTMLElement>(fixture.nativeElement.querySelectorAll('tbody td'));
    expect(cells[0].textContent?.trim()).toBe('—');
    expect(cells[2].textContent?.trim()).toBe('—');
  });

  it('opens the state modal and deactivates through the explicit endpoint', () => {
    component.openStateModal(organizer);
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain(
      'La cuenta no podrá iniciar sesión mientras permanezca desactivada.'
    );

    component.confirmStateChange();

    expect(service.setOrganizerActive).toHaveBeenCalledWith(7, false);
    expect(service.getOrganizers).toHaveBeenCalledTimes(2);
    expect(component.organizerToChange).toBeNull();
  });

  it('navigates to creation and edition', () => {
    component.goToCreate();
    component.goToEdit(7);
    expect(router.navigate).toHaveBeenCalledWith(['/organizers/new']);
    expect(router.navigate).toHaveBeenCalledWith(['/organizers', 7, 'edit']);
  });
});
