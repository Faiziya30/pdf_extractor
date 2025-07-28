import React from 'react';
import { useEffect, useState } from 'react';

const ToggleTheme = () => {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [dark]);

  return (
    <button onClick={() => setDark(!dark)} className="ml-4 px-2 py-1 border rounded">
      {dark ? '🌞' : '🌙'}
    </button>
  );
};

export default ToggleTheme;