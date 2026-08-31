import {
  Directive,
  ElementRef,
  forwardRef,
  HostListener,
  Input,
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

@Directive({
  selector: 'input[appTemporalInput]',
  standalone: true,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => TemporalInputDirective),
      multi: true,
    },
    {
      provide: NG_VALIDATORS,
      useExisting: forwardRef(() => TemporalInputDirective),
      multi: true,
    },
  ],
})
export class TemporalInputDirective implements ControlValueAccessor, Validator {
  @Input('appTemporalInput') format: TemporalFormat = 'date';

  private onChange: (value: string) => void = () => undefined;
  private onTouched: () => void = () => undefined;
  private onValidatorChange: () => void = () => undefined;
  private validInput = true;

  constructor(private readonly elementRef: ElementRef<HTMLInputElement>) {}

  @HostListener('input', ['$event'])
  handleInput(event: Event): void {
    const displayValue = (event.target as HTMLInputElement).value;
    if (!displayValue.trim()) {
      this.validInput = true;
      this.onChange('');
    } else {
      const apiValue = parseTemporalDisplay(displayValue, this.format);
      this.validInput = apiValue !== null;
      this.onChange(apiValue ?? displayValue);
    }
    this.onValidatorChange();
  }

  @HostListener('blur')
  handleBlur(): void {
    this.onTouched();
  }

  writeValue(value: string | null | undefined): void {
    this.elementRef.nativeElement.value = formatTemporal(value, this.format);
    this.validInput = !value || this.elementRef.nativeElement.value !== value ||
      parseTemporalDisplay(value, this.format) !== null;
  }

  registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.elementRef.nativeElement.disabled = isDisabled;
  }

  validate(control: AbstractControl): ValidationErrors | null {
    return control.value && !this.validInput ? { temporalFormat: true } : null;
  }

  registerOnValidatorChange(fn: () => void): void {
    this.onValidatorChange = fn;
  }
}
