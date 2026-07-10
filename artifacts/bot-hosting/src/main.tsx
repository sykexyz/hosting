import { createRoot } from 'react-dom/client';

import App from './App';

import './index.css';

// Always force dark mode — the site is black/white neon only.
document.documentElement.classList.add('dark');
localStorage.setItem('theme', 'dark');

createRoot(document.getElementById('root')!).render(<App />);
