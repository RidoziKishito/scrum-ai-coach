const LOCAL_API_BASE_URL = 'http://127.0.0.1:8000/api';

const normalizeApiBaseUrl = (url) => {
  const trimmedUrl = (url || '').trim().replace(/^['"]|['"]$/g, '');

  if (!trimmedUrl || ['null', 'none', 'undefined'].includes(trimmedUrl.toLowerCase())) {
    return LOCAL_API_BASE_URL;
  }

  const withoutTrailingSlash = trimmedUrl.replace(/\/+$/, '');

  return withoutTrailingSlash.endsWith('/api')
    ? withoutTrailingSlash
    : `${withoutTrailingSlash}/api`;
};

export const API_BASE_URL = normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL);
