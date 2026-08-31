import { Pipe, PipeTransform } from '@angular/core';

import { formatTemporal, TemporalFormat } from './date-time.utils';

@Pipe({
  name: 'uiDateTime',
  standalone: true,
})
export class UiDateTimePipe implements PipeTransform {
  transform(value: string | null | undefined, format: TemporalFormat = 'date'): string {
    return formatTemporal(value, format);
  }
}
