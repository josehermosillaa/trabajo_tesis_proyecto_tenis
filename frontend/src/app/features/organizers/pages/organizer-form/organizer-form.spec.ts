import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, Router } from '@angular/router';
import { of, throwError } from 'rxjs';

import { OrganizerService } from '../../services/organizer';
import { OrganizerFormComponent } from './organizer-form';

describe('OrganizerFormComponent', () => {
  let component: OrganizerFormComponent;
  let fixture: ComponentFixture<OrganizerFormComponent>;
  let service: jasmine.SpyObj<OrganizerService>;
  let router: jasmine.SpyObj<Router>;
  let routeId: string | null;

  beforeEach(async () => {
    routeId = null;
    service = jasmine.createSpyObj<OrganizerService>(
      'OrganizerService',
      ['getOrganizer', 'createOrganizer', 'updateOrganizer']
    );
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);
    const organizer = {
      id: 7,
      username: 'organizer',
      first_name: 'Organizador',
      last_name: 'Prueba',
      email: 'organizer@example.com',
      is_active: true,
      role: 'Organizador' as const,
    };
    service.getOrganizer.and.returnValue(of(organizer));
    service.createOrganizer.and.returnValue(of(organizer));
    service.updateOrganizer.and.returnValue(of(organizer));

    await TestBed.configureTestingModule({
      imports: [OrganizerFormComponent],
      providers: [
        { provide: OrganizerService, useValue: service },
        { provide: Router, useValue: router },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              paramMap: { get: () => routeId },
            },
          },
        },
      ],
    }).compileComponents();
  });

  it('creates an organizer without exposing a role selector', () => {
    createComponent(null);
    component.organizerForm.setValue({
      first_name: 'Nuevo',
      last_name: 'Organizador',
      username: 'new.organizer',
      email: 'new@example.com',
      password: 'SecurePassword-2026',
      password_confirmation: 'SecurePassword-2026',
    });

    component.save();

    expect(service.createOrganizer).toHaveBeenCalledWith({
      first_name: 'Nuevo',
      last_name: 'Organizador',
      username: 'new.organizer',
      email: 'new@example.com',
      password: 'SecurePassword-2026',
      password_confirmation: 'SecurePassword-2026',
    });
    expect(fixture.nativeElement.querySelector('[formControlName="role"]')).toBeNull();
  });

  it('rejects mismatched password confirmation locally', () => {
    createComponent(null);
    component.organizerForm.setValue({
      first_name: 'Nuevo', last_name: 'Organizador', username: 'new.organizer',
      email: 'new@example.com', password: 'SecurePassword-2026',
      password_confirmation: 'DifferentPassword-2026',
    });

    component.save();

    expect(service.createOrganizer).not.toHaveBeenCalled();
    expect(component.errorFor('password_confirmation')).toBe('Las contraseñas no coinciden.');
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('Las contraseñas no coinciden.');
  });

  it('shows required and invalid email errors after submit', () => {
    createComponent(null);
    component.organizerForm.controls.email.setValue('correo-invalido');

    component.save();
    fixture.detectChanges();

    expect(service.createOrganizer).not.toHaveBeenCalled();
    expect(component.hasError('first_name')).toBeTrue();
    expect(component.errorFor('email')).toBe('Ingresa un correo electrónico válido.');
    expect(component.hasError('password')).toBeTrue();
    expect(fixture.nativeElement.querySelectorAll('.is-invalid').length).toBeGreaterThan(0);
  });

  it('associates backend validation errors with their field', () => {
    service.createOrganizer.and.returnValue(throwError(() => ({
      error: { username: ['Este nombre de usuario ya existe.'] },
    })));
    createComponent(null);
    component.organizerForm.setValue({
      first_name: 'Nuevo', last_name: 'Organizador', username: 'duplicado',
      email: 'new@example.com', password: 'SecurePassword-2026',
      password_confirmation: 'SecurePassword-2026',
    });

    component.save();
    fixture.detectChanges();

    expect(component.errorFor('username')).toBe('Este nombre de usuario ya existe.');
    const username = fixture.nativeElement.querySelector('#organizer-username');
    expect(username.classList).toContain('is-invalid');
  });

  it('edits only basic fields and does not render passwords', () => {
    createComponent('7');
    component.organizerForm.patchValue({ first_name: 'Editado' });
    component.save();

    expect(service.updateOrganizer).toHaveBeenCalledWith(7, {
      first_name: 'Editado',
      last_name: 'Prueba',
      username: 'organizer',
      email: 'organizer@example.com',
    });
    expect(fixture.nativeElement.querySelector('[formControlName="password"]')).toBeNull();
  });

  function createComponent(id: string | null): void {
    routeId = id;
    fixture = TestBed.createComponent(OrganizerFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }
});
