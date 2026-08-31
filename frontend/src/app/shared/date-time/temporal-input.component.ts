import {
  Component,
  ElementRef,
  forwardRef,
  Input,
  ViewChild,
} from '@angular/core';
import {
  AbstractControl,
  ControlValueAccessor,
  NG_VALIDATORS,
  NG_VALUE_ACCESSOR,
  ValidationErrors,
  Validator,
} from '@angular/forms';

import {
  formatTemporal,
  parseTemporalDisplay,
  TemporalFormat,
} from './date-time.utils';

type PickerInput = HTMLInputElement & {
  showPicker?: () => void;
};

@Component({
  selector: 'app-temporal-input',
  standalone: true,
  template: `
    <div class="input-group">
      <input
        #displayInput
        [id]="inputId"
        type="text"
        class="form-control"
        [class.is-invalid]="invalid"
        [attr.placeholder]="placeholder || defaultPlaceholder"
        inputmode="numeric"
        [disabled]="disabled"
        [attr.aria-describedby]="ariaDescribedBy || null"
        (input)="handleManualInput($event)"
        (blur)="onTouched()"
      />
      <button
        type="button"
        class="btn btn-outline-secondary temporal-picker-button"
        [disabled]="disabled"
        [attr.aria-label]="pickerLabel"
        [attr.title]="pickerLabel"
        (click)="openPicker()"
      >
        <span aria-hidden="true">{{ pickerIcon }}</span>
      </button>
      <input
        #pickerInput
        class="visually-hidden"
        tabindex="-1"
        [attr.type]="pickerType"
        [disabled]="disabled"
        [attr.min]="min || null"
        [attr.max]="max || null"
        [attr.step]="pickerType === 'time' ? 60 : null"
        aria-hidden="true"
        (change)="handlePickerChange($event)"
      />
    </div>
  `,
  styles: `
    :host {
      display: block;
    }

    .temporal-picker-button {
      min-width: 2.75rem;
    }
  `,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => TemporalInputComponent),
      multi: true,
    },
    {
      provide: NG_VALIDATORS,
      useExisting: forwardRef(() => TemporalInputComponent),
      multi: true,
    },
  ],
})
export class TemporalInputComponent implements ControlValueAccessor, Validator {
  @Input() format: TemporalFormat = 'date';
  @Input() inputId = '';
  @Input() placeholder = '';
  @Input() min = '';
  @Input() max = '';
  @Input() invalid = false;
  @Input() ariaDescribedBy = '';

  @ViewChild('displayInput', { static: true })
  private readonly displayInput!: ElementRef<HTMLInputElement>;

  @ViewChild('pickerInput', { static: true })
  private readonly pickerInput!: ElementRef<PickerInput>;

  disabled = false;
  private validInput = true;
  private technicalValue = '';
  private onChange: (value: string) => void = () => undefined;
  protected onTouched: () => void = () => undefined;
  private onValidatorChange: () => void = () => undefined;

  get pickerType(): 'date' | 'time' | 'datetime-local' {
    return this.format === 'datetime' ? 'datetime-local' : this.format;
  }

  get defaultPlaceholder(): string {
    if (this.format === 'date') {
      return 'DD/MM/YYYY';
    }
    return this.format === 'time' ? 'HH:mm' : 'DD/MM/YYYY HH:mm';
  }

  get pickerLabel(): string {
    if (this.format === 'date') {
      return 'Abrir selector de fecha';
    }
    return this.format === 'time'
      ? 'Abrir selector de hora'
      : 'Abrir selector de fecha y hora';
  }

  get pickerIcon(): string {
    return this.format === 'time' ? '🕒' : '📅';
  }

  handleManualInput(event: Event): void {
    const displayValue = (event.target as HTMLInputElement).value;
    if (!displayValue.trim()) {
      this.validInput = true;
      this.setTechnicalValue('');
    } else {
      const apiValue = parseTemporalDisplay(displayValue, this.format);
      this.validInput = apiValue !== null;
      this.setTechnicalValue(apiValue ?? displayValue);
    }
    this.onValidatorChange();
  }

  handlePickerChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    if (!value) {
      return;
    }

    this.validInput = true;
    this.technicalValue = value;
    this.displayInput.nativeElement.value = formatTemporal(value, this.format);
    this.onChange(value);
    this.onTouched();
    this.onValidatorChange();
  }

  openPicker(): void {
    const picker = this.pickerInput.nativeElement;
    picker.value = this.validInput ? this.technicalValue : '';
    try {
      if (picker.showPicker) {
        picker.showPicker();
      } else {
        picker.focus();
        picker.click();
      }
    } catch {
      picker.focus();
      picker.click();
    }
  }

  writeValue(value: string | null | undefined): void {
    this.technicalValue = value ?? '';
    this.displayInput.nativeElement.value = formatTemporal(value, this.format);
    this.pickerInput.nativeElement.value = value ?? '';
    this.validInput = !value || this.displayInput.nativeElement.value !== value ||
      parseTemporalDisplay(value, this.format) !== null;
  }

  registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }

  validate(control: AbstractControl): ValidationErrors | null {
    return control.value && !this.validInput ? { temporalFormat: true } : null;
  }

  registerOnValidatorChange(fn: () => void): void {
    this.onValidatorChange = fn;
  }

  private setTechnicalValue(value: string): void {
    this.technicalValue = value;
    this.pickerInput.nativeElement.value = this.validInput ? value : '';
    this.onChange(value);
  }
}
