import { test, describe } from 'node:test';
import assert from 'node:assert';
import { normalizeApiBaseUrl, getMediaUrl } from './client.js';

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

describe('getMediaUrl', () => {
  test('returns null for empty, undefined, or whitespace URLs', () => {
    assert.strictEqual(getMediaUrl(undefined), null);
    assert.strictEqual(getMediaUrl(null), null);
    assert.strictEqual(getMediaUrl(''), null);
    assert.strictEqual(getMediaUrl('   '), null);
  });

  test('returns absolute HTTP and HTTPS URLs unchanged, including S3 presigned URLs', () => {
    const s3Url = 'https://campus-resumes.s3.amazonaws.com/resumes/student_1.pdf?X-Amz-Signature=abcd123';
    assert.strictEqual(getMediaUrl(s3Url), s3Url);

    const httpUrl = 'http://external-storage.example.com/resumes/cv.pdf';
    assert.strictEqual(getMediaUrl(httpUrl), httpUrl);
  });

  test('resolves local relative media paths against the backend origin', () => {
    assert.strictEqual(
      getMediaUrl('/media/resumes/student_cv.pdf'),
      'http://127.0.0.1:8000/media/resumes/student_cv.pdf'
    );
    assert.strictEqual(
      getMediaUrl('media/resumes/student_cv.pdf'),
      'http://127.0.0.1:8000/media/resumes/student_cv.pdf'
    );
  });

  test('resolves against configured API base URLs with or without trailing /api', () => {
    assert.strictEqual(
      getMediaUrl('/media/resumes/cv.pdf', 'https://my-backend.awsapprunner.com/api'),
      'https://my-backend.awsapprunner.com/media/resumes/cv.pdf'
    );
    assert.strictEqual(
      getMediaUrl('/media/resumes/cv.pdf', 'https://my-backend.awsapprunner.com/api/'),
      'https://my-backend.awsapprunner.com/media/resumes/cv.pdf'
    );
    assert.strictEqual(
      getMediaUrl('/media/resumes/cv.pdf', 'https://api.campusjobs.com'),
      'https://api.campusjobs.com/media/resumes/cv.pdf'
    );
  });
});
