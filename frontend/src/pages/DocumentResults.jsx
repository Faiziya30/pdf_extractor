import { useEffect, useState } from 'react';
import { FileText } from 'lucide-react';
import { useParams } from 'react-router-dom';
import { getDocument } from '../services/api';

const metadataFields = [
  ['Title', 'title'],
  ['Author', 'author'],
  ['Subject', 'subject'],
  ['Creator', 'creator'],
  ['Producer', 'producer'],
  ['Created', 'creationDate'],
  ['Modified', 'modDate'],
];

export default function DocumentResults() {
  const { documentId } = useParams();
  const [document, setDocument] = useState(null);
  const [selectedPage, setSelectedPage] = useState(1);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    getDocument(documentId)
      .then((result) => { if (active) setDocument(result); })
      .catch((requestError) => {
        if (active) setError(requestError.response?.data?.error?.message || 'We could not load this document.');
      });
    return () => { active = false; };
  }, [documentId]);

  if (error) return <div role="alert" className="empty-state"><p className="font-semibold">We could not load this document.</p><p className="mt-2">{error}</p></div>;
  if (!document) return <div className="empty-state"><p className="font-semibold">Analyzing your PDF...</p><p className="mt-2">Loading extracted document data.</p></div>;

  const { document: summary, pages, outline } = document;
  const page = pages.find((item) => item.page_number === selectedPage) || pages[0];

  return (
    <section className="space-y-6">
      <header className="surface rounded-[2rem] p-6 sm:p-8">
        <span className="section-eyebrow">Processed document</span>
        <h1 className="mt-4 break-words text-3xl font-semibold tracking-tight text-slate-950 dark:text-white">{summary.title || summary.filename}</h1>
        {summary.title && <p className="mt-2 break-words text-sm text-slate-500 dark:text-slate-400">{summary.filename}</p>}
        <div className="mt-5 flex flex-wrap gap-3 text-sm text-slate-500 dark:text-slate-400"><span>{summary.page_count} pages</span><span>{(summary.file_size / 1024 / 1024).toFixed(2)} MB</span><span>{outline.length} detected headings</span></div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[0.72fr_1.5fr_0.72fr]">
        <aside className="surface rounded-[2rem] p-5">
          <h2 className="panel-title text-xl">Outline</h2>
          <div className="mt-5 space-y-2">
            {outline.length === 0 ? <p className="text-sm text-slate-500">No headings detected.</p> : outline.map((heading) => <button key={`${heading.page}-${heading.text}`} type="button" onClick={() => setSelectedPage(heading.page)} className={`w-full rounded-xl p-3 text-left text-sm transition ${selectedPage === heading.page ? 'bg-rose-50 text-rose-800 dark:bg-rose-500/10 dark:text-rose-200' : 'hover:bg-slate-50 dark:hover:bg-white/5'}`}><span className="mr-2 text-xs font-bold text-rose-500">{heading.level}</span>{heading.text}<span className="mt-1 block text-xs text-slate-400">Page {heading.page} · {Math.round(heading.confidence * 100)}% heuristic confidence</span></button>)}
          </div>
        </aside>

        <article className="surface rounded-[2rem] p-6 sm:p-8">
          <div className="flex items-center justify-between gap-4"><div><p className="section-eyebrow">Page {page.page_number}</p><h2 className="mt-4 text-2xl font-semibold">Extracted text</h2></div><FileText className="text-rose-500" /></div>
          <pre className="mt-6 whitespace-pre-wrap font-sans text-sm leading-8 text-slate-700 dark:text-slate-300">{page.text || 'No native text is available on this page.'}</pre>
        </article>

        <aside className="surface rounded-[2rem] p-5">
          <h2 className="panel-title text-xl">Document facts</h2>
          <p className="mt-2 text-xs text-slate-500">Metadata status: {summary.metadata_status}</p>
          <dl className="mt-5 space-y-4 text-sm">{metadataFields.map(([label, key]) => <div key={key}><dt className="text-slate-500">{label}</dt><dd className="mt-1 break-words font-semibold">{summary.metadata[key] || 'Not provided'}</dd></div>)}</dl>
          <div className="mt-8 border-t border-slate-200/70 pt-5 dark:border-white/10"><p className="text-sm font-semibold">Pages</p><div className="mt-3 flex flex-wrap gap-2">{pages.map((item) => <button type="button" key={item.page_number} onClick={() => setSelectedPage(item.page_number)} className={`grid h-9 w-9 place-items-center rounded-lg text-sm font-semibold ${item.page_number === page.page_number ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900' : 'bg-slate-100 dark:bg-white/10'}`}>{item.page_number}</button>)}</div></div>
        </aside>
      </div>
    </section>
  );
}
