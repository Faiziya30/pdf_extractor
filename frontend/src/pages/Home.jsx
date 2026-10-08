import { useRef, useState } from 'react';
import { FileText, UploadCloud } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { uploadDocument } from '../services/api';

const MAX_FILE_SIZE = 50 * 1024 * 1024;

export default function Home() {
  const inputRef = useRef(null);
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');

  const selectFile = (selectedFile) => {
    setError('');
    if (!selectedFile) return;
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) return setError('Please choose a PDF file.');
    if (selectedFile.size > MAX_FILE_SIZE) return setError('This file is larger than the 50 MB limit.');
    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return setError('Choose a PDF before uploading.');
    setStatus('uploading');
    setError('');
    try {
      const result = await uploadDocument(file);
      navigate(`/documents/${result.document.id}`);
    } catch (requestError) {
      setStatus('error');
      setError(requestError.response?.data?.error?.message || 'We could not process this PDF.');
    }
  };

  return <section className="space-y-10"><div className="max-w-3xl space-y-4"><span className="section-eyebrow">Document intelligence foundation</span><h1 className="display-heading text-5xl font-semibold tracking-tight text-slate-950 dark:text-white sm:text-7xl">Make the shape of a PDF visible.</h1><p className="max-w-2xl text-base leading-8 text-slate-600 dark:text-slate-300">SmartPDF extracts page text, metadata, and a layout-based outline so you can review a document without losing your place.</p></div><div className="grid gap-6 lg:grid-cols-[1fr_0.7fr]"><div className="surface rounded-[2rem] p-6 sm:p-8"><input ref={inputRef} type="file" accept="application/pdf" className="sr-only" onChange={(event) => selectFile(event.target.files?.[0])} /><button type="button" onClick={() => inputRef.current?.click()} className="flex min-h-72 w-full flex-col items-center justify-center rounded-3xl border border-dashed border-rose-300 bg-rose-50/60 px-6 text-center transition hover:border-rose-500 dark:border-rose-400/30 dark:bg-rose-500/5"><span className="grid h-16 w-16 place-items-center rounded-2xl bg-rose-500 text-white shadow-lg shadow-rose-500/20"><UploadCloud size={28} /></span><span className="mt-5 text-xl font-semibold text-slate-950 dark:text-white">Drop a PDF here or browse</span><span className="mt-2 text-sm text-slate-500 dark:text-slate-400">PDF only, up to 50 MB</span></button>{file && <div className="mt-5 flex items-center gap-3 rounded-2xl bg-slate-50 p-4 dark:bg-white/5"><FileText className="text-rose-500" size={22} /><div className="min-w-0"><p className="truncate font-semibold">{file.name}</p><p className="text-sm text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p></div></div>}{error && <p role="alert" className="mt-4 rounded-2xl bg-red-50 p-4 text-sm font-medium text-red-700 dark:bg-red-500/10 dark:text-red-200">{error}</p>}<button type="button" onClick={handleUpload} disabled={status === 'uploading' || !file} className="primary-btn mt-5 w-full">{status === 'uploading' ? 'Uploading and analyzing...' : 'Upload and extract'}</button></div><aside className="surface rounded-[2rem] p-6 sm:p-8"><p className="section-eyebrow">What you get</p><div className="mt-6 space-y-5">{['Page-by-page text', 'PDF metadata', 'Heuristic heading outline', 'Clickable page review'].map((item) => <div key={item} className="flex items-center gap-3 border-b border-slate-200/70 pb-5 text-sm font-semibold dark:border-white/10"><span className="h-2 w-2 rounded-full bg-rose-500" />{item}</div>)}</div><p className="mt-6 text-sm leading-7 text-slate-500 dark:text-slate-400">Heading confidence is a transparent layout heuristic, not a trained model score.</p></aside></div></section>;
}