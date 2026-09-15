import { describe, expect, it } from 'vitest';
import { isJsonObject, isPositiveNumber, isString } from '../main/guards';

describe('isString', () => {
  it('принимает только строки', () => {
    expect(isString('')).toBe(true);
    expect(isString('text')).toBe(true);
    expect(isString(1)).toBe(false);
    expect(isString(null)).toBe(false);
    expect(isString(undefined)).toBe(false);
  });
});

describe('isPositiveNumber', () => {
  it('принимает только конечные числа больше нуля', () => {
    expect(isPositiveNumber(1)).toBe(true);
    expect(isPositiveNumber(0.5)).toBe(true);
    expect(isPositiveNumber(0)).toBe(false);
    expect(isPositiveNumber(-1)).toBe(false);
    expect(isPositiveNumber(Number.NaN)).toBe(false);
    expect(isPositiveNumber(Number.POSITIVE_INFINITY)).toBe(false);
    expect(isPositiveNumber('1')).toBe(false);
  });
});

describe('isJsonObject', () => {
  it('принимает только простые объекты', () => {
    expect(isJsonObject({})).toBe(true);
    expect(isJsonObject([])).toBe(false);
    expect(isJsonObject(null)).toBe(false);
    expect(isJsonObject('text')).toBe(false);
    expect(isJsonObject(undefined)).toBe(false);
  });
});
