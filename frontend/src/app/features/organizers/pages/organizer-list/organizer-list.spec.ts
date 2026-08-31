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
