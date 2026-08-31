import {
  displayDateTimeToApi,
  displayDateToApi,
  formatTemporal,
} from './date-time.utils';

describe('date-time utilities', () => {
  it('formats an API date as DD/MM/YYYY', () => {
    expect(formatTemporal('2026-08-31', 'date')).toBe('31/08/2026');
  });

  it('formats date-time and time without changing timezone', () => {
    const value = '2026-08-31T18:30:00-04:00';
    expect(formatTemporal(value, 'datetime')).toBe('31/08/2026 18:30');
    expect(formatTemporal(value, 'time')).toBe('18:30');
  });

  it('converts a valid display date to API format', () => {
    expect(displayDateToApi('01/02/2026')).toBe('2026-02-01');
  });

  it('rejects impossible dates and non-leap February 29', () => {
    expect(displayDateToApi('31/02/2026')).toBeNull();
    expect(displayDateToApi('29/02/2025')).toBeNull();
  });

  it('accepts February 29 in a leap year', () => {
    expect(displayDateToApi('29/02/2028')).toBe('2028-02-29');
  });

  it('converts display date-time to the technical API value', () => {
    expect(displayDateTimeToApi('31/08/2026 18:30')).toBe('2026-08-31T18:30');
  });
});
