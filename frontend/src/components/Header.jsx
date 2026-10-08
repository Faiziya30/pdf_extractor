import { Link, useLocation } from 'react-router-dom';
import ToggleTheme from './ToggleTheme';

export default function Header() {
  const location = useLocation();
  const active = location.pathname === '/';
  return <header className="sticky top-0 z-50 px-3 pt-3 sm:px-4 sm:pt-4"><div className="surface mx-auto flex max-w-7xl items-center justify-between rounded-[1.75rem] px-4 py-3 sm:px-5"><Link to="/" className="flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-2xl bg-gradient-to-br from-rose-500 via-red-500 to-orange-400 text-sm font-bold text-white shadow-lg shadow-rose-500/20">SP</span><span><span className="block text-lg font-bold tracking-tight text-slate-900 dark:text-white">SmartPDF</span><span className="hidden text-xs font-medium uppercase tracking-[0.24em] text-slate-500 dark:text-slate-400 sm:block">document workspace</span></span></Link><nav className="flex items-center gap-2"><Link to="/" className={`rounded-full px-4 py-2 text-sm font-semibold ${active ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900' : 'text-slate-600 dark:text-slate-300'}`}>Upload</Link><ToggleTheme /></nav></div></header>;
}
