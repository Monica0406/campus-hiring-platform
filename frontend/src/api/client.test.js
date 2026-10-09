import { test, describe } from 'node:test';
import assert from 'node:assert';
import { normalizeApiBaseUrl } from './client.js';

describe('normalizeApiBaseUrl', () => {
  test('returns local default when URL is undefined or empty', () => {
    assert.strictEqual(normalizeApiBaseUrl(undefined), 'http://127.0.0.1:8000/api');
    assert.strictEqual(normalizeApiBaseUrl(null), 'http://127.0.0.1:8000/api');
    assert.strictEqual(normalizeApiBaseUrl(''), 'http://127.0.0.1:8000/api');
    assert.strictEqual(normalizeApiBaseUrl('   '), 'http://127.0.0.1:8000/api');
  });

  test('appends /api when given root domain without api path', () => {
    assert.strictEqual(
      normalizeApiBaseUrl('https://my-backend.awsapprunner.com'),
      'https://my-backend.awsapprunner.com/api'
    );
    assert.strictEqual(
      normalizeApiBaseUrl('https://my-backend.awsapprunner.com/'),
      'https://my-backend.awsapprunner.com/api'
    );
  });

  test('preserves existing /api and strips trailing slash', () => {
    assert.strictEqual(
      normalizeApiBaseUrl('https://my-backend.awsapprunner.com/api'),
      'https://my-backend.awsapprunner.com/api'
    );
    assert.strictEqual(
      normalizeApiBaseUrl('https://my-backend.awsapprunner.com/api/'),
      'https://my-backend.awsapprunner.com/api'
    );
    assert.strictEqual(
      normalizeApiBaseUrl('http://127.0.0.1:8000/api///'),
      'http://127.0.0.1:8000/api'
    );
  });
});
