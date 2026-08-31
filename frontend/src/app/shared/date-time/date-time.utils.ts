export type TemporalFormat = 'date' | 'datetime' | 'time';

const API_DATE_PATTERN = /^(\d{4})-(\d{2})-(\d{2})/;
const DISPLAY_DATE_PATTERN = /^(\d{2})\/(\d{2})\/(\d{4})$/;
const TIME_PATTERN = /^(\d{2}):(\d{2})$/;

function isLeapYear(year: number): boolean {
  return year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
}

function daysInMonth(month: number, year: number): number {
  const days = [31, isLeapYear(year) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  return days[month - 1] ?? 0;
}

function isValidDate(day: number, month: number, year: number): boolean {
  return year >= 1 && month >= 1 && month <= 12 && day >= 1 && day <= daysInMonth(month, year);
}

function isValidTime(hour: number, minute: number): boolean {
  return hour >= 0 && hour <= 23 && minute >= 0 && minute <= 59;
}

export function displayDateToApi(value: string): string | null {
  const match = DISPLAY_DATE_PATTERN.exec(value.trim());
  if (!match) {
    return null;
  }

  const [, day, month, year] = match;
  if (!isValidDate(Number(day), Number(month), Number(year))) {
    return null;
  }

  return `${year}-${month}-${day}`;
}

export function displayTimeToApi(value: string): string | null {
  const match = TIME_PATTERN.exec(value.trim());
  if (!match || !isValidTime(Number(match[1]), Number(match[2]))) {
    return null;
  }

  return `${match[1]}:${match[2]}`;
}

export function displayDateTimeToApi(value: string): string | null {
  const parts = value.trim().split(/\s+/);
  if (parts.length !== 2) {
    return null;
  }

  const date = displayDateToApi(parts[0]);
  const time = displayTimeToApi(parts[1]);
  return date && time ? `${date}T${time}` : null;
}

export function parseTemporalDisplay(value: string, format: TemporalFormat): string | null {
  switch (format) {
    case 'date':
      return displayDateToApi(value);
    case 'datetime':
      return displayDateTimeToApi(value);
    case 'time':
      return displayTimeToApi(value);
  }
}

export function formatTemporal(value: string | null | undefined, format: TemporalFormat): string {
  if (!value) {
    return '';
  }

  if (format === 'time') {
    const timeMatch = value.match(/(?:T|^)(\d{2}):(\d{2})/);
    return timeMatch && isValidTime(Number(timeMatch[1]), Number(timeMatch[2]))
      ? `${timeMatch[1]}:${timeMatch[2]}`
      : value;
  }

  const dateMatch = API_DATE_PATTERN.exec(value);
  if (!dateMatch) {
    return value;
  }

  const [, year, month, day] = dateMatch;
  if (!isValidDate(Number(day), Number(month), Number(year))) {
    return value;
  }

  const displayedDate = `${day}/${month}/${year}`;
  if (format === 'date') {
    return displayedDate;
  }

  const timeMatch = value.match(/[T ](\d{2}):(\d{2})/);
  return timeMatch && isValidTime(Number(timeMatch[1]), Number(timeMatch[2]))
    ? `${displayedDate} ${timeMatch[1]}:${timeMatch[2]}`
    : value;
}
