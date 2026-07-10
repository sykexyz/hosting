import { createRoot } from 'react-dom/client';
import { setBaseUrl } from '@workspace/api-client-react';

import App from './App';

import './index.css';

// Always force dark mode — the site is black/white neon only.
document.documentElement.classList.add('dark');
localStorage.setItem('theme', 'dark');

// On Railway, the frontend and API are separate services on different domains.
// Set VITE_API_URL to the Railway API service URL (e.g. https://api-xxx.railway.app)
// so all API calls are routed there instead of the same origin.
const apiUrl = import.meta.env.VITE_API_URL as string | undefined;
if (apiUrl) {
  setBaseUrl(apiUrl);
}

createRoot(document.getElementById('root')!).render(<App />);
