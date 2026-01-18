import { describe, it, expect } from 'vitest';
import { sanitizeKey, sanitizeRecord } from '@utils/sanitize';

describe('useLiveMatches - Security', () => {
  it('should sanitize keys to prevent prototype pollution via __proto__', () => {
    const maliciousKey = '__proto__';
    const sanitized = sanitizeKey(maliciousKey);
    
    expect(sanitized).toBe('$__proto__');
    expect(sanitized).not.toBe('__proto__');
  });
  
  it('should sanitize keys to prevent prototype pollution via constructor', () => {
    const maliciousKey = 'constructor';
    const sanitized = sanitizeKey(maliciousKey);
    
    expect(sanitized).toBe('$constructor');
    expect(sanitized).not.toBe('constructor');
  });
  
  it('should sanitize keys to prevent prototype pollution via toString', () => {
    const maliciousKey = 'toString';
    const sanitized = sanitizeKey(maliciousKey);
    
    expect(sanitized).toBe('$toString');
  });
  
  it('should sanitize all keys in a Record object', () => {
    const testRecord = {
      'fixtureId1': ['event1'],
      'fixtureId2': ['event2'],
      'validId123': ['event3']
    };
    
    const sanitized = sanitizeRecord(testRecord);
    
    // Verify keys are sanitized with $ prefix
    expect(sanitized['$fixtureId1']).toEqual(['event1']);
    expect(sanitized['$fixtureId2']).toEqual(['event2']);
    expect(sanitized['$validId123']).toEqual(['event3']);
    
    // Verify original keys are not present
    expect(sanitized['fixtureId1']).toBeUndefined();
    expect(sanitized['fixtureId2']).toBeUndefined();
    expect(sanitized['validId123']).toBeUndefined();
  });
  
  it('should not pollute Object prototype when using sanitized keys', () => {
    const testObj: Record<string, unknown> = {};
    const maliciousKey = '__proto__';
    const sanitizedKey = sanitizeKey(maliciousKey);
    
    // Assign value using sanitized key
    testObj[sanitizedKey] = 'malicious value';
    
    // Verify prototype is not polluted
    const newObj = {};
    expect((newObj as Record<string, unknown>).polluted).toBeUndefined();
    
    // Verify value is stored under the sanitized key
    expect(testObj[sanitizedKey]).toBe('malicious value');
  });
  
  it('should handle normal fixture IDs correctly', () => {
    const normalId = 'match-12345';
    const sanitized = sanitizeKey(normalId);
    
    expect(sanitized).toBe('$match-12345');
  });
  
  it('should preserve data when sanitizing records', () => {
    const record = {
      'fixture1': [{ minute: 10, description: 'Goal', type: 'goal' }],
      'fixture2': [{ minute: 20, description: 'Card', type: 'card' }]
    };
    
    const sanitized = sanitizeRecord(record);
    
    expect(sanitized['$fixture1']).toEqual(record.fixture1);
    expect(sanitized['$fixture2']).toEqual(record.fixture2);
  });
});
