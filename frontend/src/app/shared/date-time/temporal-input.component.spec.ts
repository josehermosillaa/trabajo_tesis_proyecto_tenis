import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { By } from '@angular/platform-browser';

import { TemporalFormat } from './date-time.utils';
import { TemporalInputComponent } from './temporal-input.component';

@Component({
  imports: [ReactiveFormsModule, TemporalInputComponent],
  template: `<app-temporal-input [format]="format" [formControl]="control" />`,
})
class TestHostComponent {
  format: TemporalFormat = 'date';
  control = new FormControl('');
}

describe('TemporalInputComponent', () => {
  let fixture: ComponentFixture<TestHostComponent>;
  let host: TestHostComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [TestHostComponent] }).compileComponents();
    fixture = TestBed.createComponent(TestHostComponent);
    host = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('keeps DD/MM/YYYY visible while exposing an API date value', () => {
    host.control.setValue('2026-09-05');
    fixture.detectChanges();

    expect(displayInput().value).toBe('05/09/2026');
    expect(host.control.value).toBe('2026-09-05');
  });

  it('updates the FormControl from the native date picker', () => {
    pickerInput().value = '2028-02-29';
    pickerInput().dispatchEvent(new Event('change'));

    expect(host.control.value).toBe('2028-02-29');
    expect(displayInput().value).toBe('29/02/2028');
  });

  it('updates a time as HH:mm from the native time picker', () => {
    host.format = 'time';
    fixture.detectChanges();
    pickerInput().value = '19:30';
    pickerInput().dispatchEvent(new Event('change'));

    expect(host.control.value).toBe('19:30');
    expect(displayInput().value).toBe('19:30');
  });

  it('continues accepting manual normalized input', () => {
    displayInput().value = '05/09/2026';
    displayInput().dispatchEvent(new Event('input'));

    expect(host.control.value).toBe('2026-09-05');
  });

  it('keeps the datetime API value when selected natively', () => {
    host.format = 'datetime';
    fixture.detectChanges();
    pickerInput().value = '2026-09-05T19:30';
    pickerInput().dispatchEvent(new Event('change'));

    expect(host.control.value).toBe('2026-09-05T19:30');
    expect(displayInput().value).toBe('05/09/2026 19:30');
  });

  function displayInput(): HTMLInputElement {
    return fixture.debugElement.query(By.css('input[type="text"]')).nativeElement;
  }

  function pickerInput(): HTMLInputElement {
    return fixture.debugElement.query(By.css('input.visually-hidden')).nativeElement;
  }
});
