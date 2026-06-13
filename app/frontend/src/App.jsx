import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
const HISTORY_KEY = 'querymind-research-history'
const LEGACY_HISTORY_KEY = 'perplexicity-research-history'

const STAGES = [
  ['Retrieving', 'Searching across available sources'],
  ['Fusing', 'Combining results from multiple retrievers'],
  ['Deduplication', 'Removing repeated and overlapping evidence'],
  ['Reranking', 'Prioritizing the most relevant documents'],
  ['Context building', 'Assembling the research context'],
  ['Prompt Building', 'Structuring the evidence for synthesis'],
  ['Answer Generation', 'Writing a clear, grounded answer'],
  ['Citation Mapping', 'Connecting the answer to its sources'],
]

const STARTERS = [
  { label: 'Technology', query: 'What are the most important recent advances in retrieval-augmented generation?' },
  { label: 'Science', query: 'Explain the current state of commercial fusion energy and its biggest obstacles.' },
  { label: 'Business', query: 'How is generative AI changing knowledge work and enterprise software?' },
  { label: 'Learning', query: 'Compare RAG, fine-tuning, and prompt engineering with practical examples.' },
]

function Icon({ name, size = 20 }) {
  const paths = {
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
    plus: <><path d="M12 5v14M5 12h14"/></>,
    history: <><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/></>,
    compass: <><circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5 5-2Z"/></>,
    send: <><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></>,
    copy: <><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M15 9V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h3"/></>,
    check: <path d="m5 12 4 4L19 6"/>,
    external: <><path d="M15 4h5v5M14 10l6-6"/><path d="M20 13v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h5"/></>,
    menu: <><path d="M4 7h16M4 12h16M4 17h16"/></>,
    close: <><path d="m6 6 12 12M18 6 6 18"/></>,
    spark: <><path d="m12 3-1.2 3.8L7 8l3.8 1.2L12 13l1.2-3.8L17 8l-3.8-1.2Z"/><path d="m5 14-.7 2.3L2 17l2.3.7L5 20l.7-2.3L8 17l-2.3-.7Z"/></>,
    globe: <><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/></>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    alert: <><circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/></>,
    trash: <><path d="M4 7h16M9 7V4h6v3M7 7l1 13h8l1-13"/></>,
  }
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>
}

function Logo() {
  return <div className="brand"><span className="brand-mark"><span /></span><span>QueryMind</span></div>
}

function readHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || localStorage.getItem(LEGACY_HISTORY_KEY)) || []
  } catch {
    return []
  }
}

function SpaceBackdrop() {
  return <div className="space-backdrop" aria-hidden="true">
    <div className="stars stars-near" />
    <div className="stars stars-far" />
    <div className="nebula nebula-one" />
    <div className="nebula nebula-two" />
    <div className="orbit orbit-one"><span /></div>
    <div className="orbit orbit-two"><span /></div>
    <div className="planet"><span /></div>
    <div className="shooting-star shooting-star-one" />
    <div className="shooting-star shooting-star-two" />
  </div>
}

function hostname(url) {
  try { return new URL(url).hostname.replace(/^www\./, '') } catch { return 'Source' }
}

function Sidebar({ open, onClose, history, onSelect, onNew, onClear }) {
  return <>
    {open && <button className="scrim" onClick={onClose} aria-label="Close navigation" />}
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      <div className="sidebar-top"><Logo /><button className="mobile-close" onClick={onClose}><Icon name="close" /></button></div>
      <button className="new-thread" onClick={onNew}><Icon name="plus" size={18} /> New thread <kbd>Ctrl K</kbd></button>
      <nav className="main-nav">
        <button className="nav-active" onClick={onNew}><Icon name="compass" size={18} /> Home</button>
        <button><Icon name="history" size={18} /> Library</button>
      </nav>
      <div className="history-head"><span>Recent</span>{history.length > 0 && <button onClick={onClear} title="Clear history"><Icon name="trash" size={15} /></button>}</div>
      <div className="history-list">
        {history.length === 0 ? <p className="history-empty">Your research threads will appear here.</p> : history.map(item => (
          <button key={item.id} onClick={() => onSelect(item)} title={item.query}>{item.query}</button>
        ))}
      </div>
      <div className="sidebar-foot"><span className="avatar">Q</span><div><strong>Research workspace</strong><small>Local session</small></div></div>
    </aside>
  </>
}

function QueryBox({ value, setValue, mode, setMode, onSubmit, loading, compact = false }) {
  const textarea = useRef(null)
  useEffect(() => {
    if (!textarea.current) return
    textarea.current.style.height = 'auto'
    textarea.current.style.height = `${Math.min(textarea.current.scrollHeight, compact ? 130 : 170)}px`
  }, [value, compact])

  return <form className={`query-box ${compact ? 'compact' : ''}`} onSubmit={onSubmit}>
    <textarea ref={textarea} value={value} onChange={e => setValue(e.target.value)} placeholder="Ask anything..." rows="1" maxLength="2000" disabled={loading} onKeyDown={e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); onSubmit(e) }
    }} />
    <div className="query-actions">
      <div className="mode-switch" role="group" aria-label="Research mode">
        <button type="button" className={mode === 'general' ? 'selected' : ''} onClick={() => setMode('general')}><Icon name="globe" size={16} /> General</button>
        <button type="button" className={mode === 'research' ? 'selected' : ''} onClick={() => setMode('research')}><Icon name="spark" size={16} /> Deep research</button>
      </div>
      <button className="submit" type="submit" disabled={!value.trim() || loading} aria-label="Submit query">{loading ? <span className="spinner" /> : <Icon name="send" size={18} />}</button>
    </div>
  </form>
}

function Progress({ status, query }) {
  const active = Math.max(0, STAGES.findIndex(([name]) => status.trim().toLowerCase().startsWith(name.toLowerCase())))
  return <div className="researching">
    <div className="research-title"><span className="pulse-logo"><span /></span><div><strong>Researching your question</strong><p>{query}</p></div></div>
    <div className="progress-line"><span style={{ width: `${Math.max(8, ((active + 1) / STAGES.length) * 100)}%` }} /></div>
    <div className="stage-list">{STAGES.map(([name, detail], index) => {
      const state = index < active ? 'done' : index === active ? 'active' : ''
      return <div className={`stage ${state}`} key={name}><span className="stage-dot">{state === 'done' ? <Icon name="check" size={13} /> : index + 1}</span><div><strong>{name}</strong>{state === 'active' && <p>{detail}</p>}</div></div>
    })}</div>
  </div>
}

function Sources({ sources }) {
  if (!sources?.length) return null
  return <section className="sources"><div className="section-label"><span>Sources</span><small>{sources.length} references</small></div><div className="source-grid">{sources.map((source, index) => (
    <a href={source.url} target="_blank" rel="noreferrer" className="source-card" key={`${source.url}-${index}`}>
      <div className="source-meta"><span className="source-number">{index + 1}</span><span>{source.provider || hostname(source.url)}</span><Icon name="external" size={14} /></div>
      <strong>{source.title || hostname(source.url)}</strong><small>{hostname(source.url)}</small>
    </a>
  ))}</div></section>
}

function Answer({ data, onFollowUp }) {
  const [copied, setCopied] = useState(false)
  const copy = async () => { await navigator.clipboard.writeText(data.answer || ''); setCopied(true); setTimeout(() => setCopied(false), 1600) }
  return <article className="answer-view">
    <header className="answer-header"><div><span className="eyebrow"><Icon name="spark" size={15} /> Answer</span><h1>{data.query}</h1></div><button className="icon-action" onClick={copy}>{copied ? <Icon name="check" size={17} /> : <Icon name="copy" size={17} />}<span>{copied ? 'Copied' : 'Copy'}</span></button></header>
    <div className="answer-body"><ReactMarkdown>{data.answer || ''}</ReactMarkdown></div>
    <Sources sources={data.sources} />
    <footer className="answer-footer"><span><Icon name="clock" size={15} /> Researched in {data.Time || '--'}s</span><span>{data.sources?.length || 0} sources analyzed</span></footer>
    <div className="follow-up"><span>Continue exploring</span><QueryBox {...onFollowUp} compact /></div>
  </article>
}

export default function App() {
  const [query, setQuery] = useState('')
  const [mode, setMode] = useState('general')
  const [view, setView] = useState('home')
  const [status, setStatus] = useState('')
  const [requestId, setRequestId] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [history, setHistory] = useState(readHistory)
  const pollRef = useRef(null)

  const loading = view === 'loading'
  useEffect(() => {
    const shortcut = e => { if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); newThread() } }
    window.addEventListener('keydown', shortcut)
    return () => window.removeEventListener('keydown', shortcut)
  }, [])

  useEffect(() => () => clearTimeout(pollRef.current), [])

  const saveResult = data => {
    const item = { id: crypto.randomUUID(), query: data.query, data, createdAt: Date.now() }
    setHistory(previous => {
      const next = [item, ...previous.filter(entry => entry.query !== data.query)].slice(0, 20)
      localStorage.setItem(HISTORY_KEY, JSON.stringify(next))
      return next
    })
  }

  const poll = async id => {
    try {
      const response = await fetch(`${API_BASE}/response/${id}`)
      if (!response.ok) throw new Error('The research request could not be found.')
      const data = await response.json()
      setStatus(data.status || 'Retrieving')
      if (data.status === 'completed') { setResult(data); setView('answer'); saveResult(data); return }
      if (data.status === 'failed') throw new Error(data.error || 'The research pipeline failed.')
      pollRef.current = setTimeout(() => poll(id), 1200)
    } catch (err) { setError(err.message || 'Unable to connect to the research server.'); setView('error') }
  }

  const submit = async event => {
    event?.preventDefault()
    const cleanQuery = query.trim()
    if (!cleanQuery || loading) return
    clearTimeout(pollRef.current)
    setError(''); setResult(null); setStatus('Retrieving'); setView('loading')
    try {
      const response = await fetch(`${API_BASE}/query`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: cleanQuery, intent: mode }) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Could not start the research request.')
      setRequestId(data.request_id)
      poll(data.request_id)
    } catch (err) { setError(err.message || 'Unable to connect to the research server.'); setView('error') }
  }

  const newThread = () => { clearTimeout(pollRef.current); setQuery(''); setResult(null); setRequestId(''); setError(''); setView('home'); setSidebarOpen(false) }
  const selectHistory = item => { clearTimeout(pollRef.current); setQuery(item.query); setResult(item.data); setView('answer'); setSidebarOpen(false) }
  const clearHistory = () => { localStorage.removeItem(HISTORY_KEY); setHistory([]) }

  return <div className={`app-shell ${view === 'home' ? 'space-mode' : ''}`}>
    <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} history={history} onSelect={selectHistory} onNew={newThread} onClear={clearHistory} />
    <main className={`main-panel ${view === 'home' ? 'home-active' : ''}`}>
      <header className="mobile-header"><button onClick={() => setSidebarOpen(true)}><Icon name="menu" /></button><Logo /><button onClick={newThread}><Icon name="plus" /></button></header>
      {view === 'home' && <section className="home-scene">
        <SpaceBackdrop />
        <div className="home-view">
          <div className="hero-copy"><span className="hero-kicker"><span /> QueryMind research engine</span><h1>What do you want<br />to <em>understand?</em></h1><p>Search deeply, compare sources, and turn complex questions into clear answers with traceable evidence.</p></div>
          <div className="home-search"><QueryBox value={query} setValue={setQuery} mode={mode} setMode={setMode} onSubmit={submit} loading={loading} /><p className="search-hint">Press Enter to search <span>Shift + Enter for a new line</span></p></div>
          <div className="starter-section"><div className="starter-heading"><span>Start with an idea</span><small>or ask your own question</small></div><div className="starter-grid">{STARTERS.map((item, index) => <button key={item.label} onClick={() => setQuery(item.query)}><span>{String(index + 1).padStart(2, '0')}</span><div><small>{item.label}</small><strong>{item.query}</strong></div><Icon name="send" size={16} /></button>)}</div></div>
        </div>
      </section>}
      {view === 'loading' && <section className="content-view"><Progress status={status} query={query} /><p className="request-id">Research ID {requestId.slice(0, 8)}</p></section>}
      {view === 'answer' && result && <section className="content-view"><Answer data={result} onFollowUp={{ value: query, setValue: setQuery, mode, setMode, onSubmit: submit, loading }} /></section>}
      {view === 'error' && <section className="error-view"><span className="error-icon"><Icon name="alert" size={28} /></span><h1>Research paused</h1><p>{error}</p><div><button onClick={submit}>Try again</button><button onClick={newThread}>New search</button></div></section>}
      <footer className="site-footer"><span>QueryMind</span><p>Answers can be inaccurate. Verify important information with the cited sources.</p></footer>
    </main>
  </div>
}
