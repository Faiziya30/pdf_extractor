import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import DocumentResults from './pages/DocumentResults';

export default function App() {
  return <BrowserRouter><div className="app-shell text-slate-900 dark:text-slate-100"><Header /><main className="mx-auto w-full max-w-7xl px-4 pb-16 pt-8 sm:px-6 lg:px-8"><Routes><Route path="/" element={<Home />} /><Route path="/upload" element={<Home />} /><Route path="/documents/:documentId" element={<DocumentResults />} /><Route path="*" element={<Navigate to="/" replace />} /></Routes></main></div></BrowserRouter>;
}