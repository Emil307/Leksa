import { describe, expect, it } from 'vitest';
import { countUtf8Octets } from '../main/text';

describe('countUtf8Octets', () => {
  it('считает байты UTF-8, а не символы', () => {
    expect(countUtf8Octets('')).toBe(0);
    expect(countUtf8Octets('abc')).toBe(3);
    expect(countUtf8Octets('ёж')).toBe(4);
    expect(countUtf8Octets('😀')).toBe(4);
  });
});
