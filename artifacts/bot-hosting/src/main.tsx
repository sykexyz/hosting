import { createRoot } from 'react-dom/client';

import App from './App';

import './index.css';

(function initTheme() {
  const stored = localStorage.getItem('theme');
  const theme = stored === 'light' || stored === 'dark'
    ? stored
    : (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.classList.toggle('dark', theme === 'dark');
})();

createRoot(document.getElementById('root')!).render(<App />);
