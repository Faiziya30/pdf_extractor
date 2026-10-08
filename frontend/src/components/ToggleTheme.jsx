import { useEffect, useState } from 'react';
import { Moon, SunMedium } from 'lucide-react';

const ToggleTheme = () => {
  const [dark, setDark] = useState(() => {
    if (typeof window === 'undefined') {
      return false;
    }

    const storedTheme = window.localStorage.getItem('theme');
    if (storedTheme) {
      return storedTheme === 'dark';
    }

    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add('dark');
      window.localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      window.localStorage.setItem('theme', 'light');
    }
  }, [dark]);

  return (
    <button
      type="button"
      onClick={() => setDark((current) => !current)}
      className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/60 bg-white/80 text-slate-700 shadow-sm transition hover:-translate-y-0.5 hover:border-rose-200 hover:text-rose-600 dark:border-white/10 dark:bg-white/5 dark:text-slate-200 dark:hover:border-rose-400/30 dark:hover:text-white"
      aria-label="Toggle theme"
    >
      {dark ? <Moon size={18} /> : <SunMedium size={18} />}
    </button>
  );
};

export default ToggleTheme;