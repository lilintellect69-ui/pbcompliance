// Compliance Assistant — bottom drawer chat UI.
//
// Per design brief §5 Phase 3:
//   - Collapsed (default): 48px input bar at viewport bottom with placeholder
//     reflecting current page
//   - Expanded: 60vh panel with chat history, streaming responses, context
//     badge showing scope, suggested-question chips
//   - Streaming markdown render (react-markdown + remark-gfm)
//   - Citation [id](#id) markdown links → intercepted, route to the right page
//   - Conversation history in localStorage, capped at last 10 turns
//   - Reset button + toggle for "reset on page change"
//
// Backend: POST /api/chat — streaming SSE events.

import { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  MessageCircle,
  ChevronDown,
  Send,
  RotateCcw,
  X,
  Loader2,
  Sparkles,
} from 'lucide-react';

const STORAGE_PREFIX = 'pb-assistant-';
const MAX_TURNS = 10; // user + assistant pairs

// ─── Route mapping (App.jsx view → backend route shape) ──────────────────────

function viewToRoute(view) {
  switch (view?.type) {
    case 'framework':
      return { type: 'framework', frameworkId: view.id };
    case 'requirement':
      return { type: 'requirement', reqId: view.id };
    case 'scenario':
      return { type: 'scenario', scenarioId: view.id };
    case 'openq':
      return view.id ? { type: 'oq', oqId: view.id } : { type: 'oq-index' };
    case 'graph':
      return { type: 'graph' };
    case 'home':
    default:
      return { type: 'home' };
  }
}

// ─── ID resolution (citation click → App.jsx view) ───────────────────────────

function resolveIdToView(id, data) {
  if (!id) return null;
  // Framework top-level ID
  if (data.frameworks[id]) return { type: 'framework', id };
  // Scenario
  if (id.startsWith('scn-')) return { type: 'scenario', id };
  // Open question
  if (id.startsWith('oq-')) return { type: 'openq', id };
  // Requirement — must exist in some framework's requirements
  for (const fw of Object.values(data.frameworks)) {
    if ((fw.requirements || []).some((r) => r.id === id)) {
      return { type: 'requirement', id };
    }
  }
  return null;
}

// ─── Page-specific placeholder + suggested questions ─────────────────────────

function placeholderForView(view, data) {
  switch (view?.type) {
    case 'framework': {
      const fw = data.frameworks[view.id];
      return fw ? `Ask about ${fw.full_name?.split(' ').slice(0, 4).join(' ') || view.id}…` : 'Ask about this framework…';
    }
    case 'requirement': {
      for (const fw of Object.values(data.frameworks)) {
        const req = (fw.requirements || []).find((r) => r.id === view.id);
        if (req) return `Ask about ${req.native_id || req.id}…`;
      }
      return 'Ask about this requirement…';
    }
    case 'scenario':
      return 'Ask about this scenario…';
    case 'openq':
      return view.id ? 'Ask about this open question…' : 'Ask about pending decisions…';
    case 'graph':
      return 'Ask about the cross-framework graph…';
    case 'home':
    default:
      return 'Ask the compliance assistant — anything from these 8 frameworks…';
  }
}

function suggestedForView(view, data) {
  switch (view?.type) {
    case 'home':
      return [
        "Where should I start?",
        "What's blocking us across all frameworks?",
        "Show me the highest-leverage controls",
        "Which frameworks am I covered on?",
      ];
    case 'framework':
      return [
        "What are the top risks here?",
        "How do I get audit-ready?",
        "What open questions are blocking us?",
        "Compare to a related framework",
      ];
    case 'requirement':
      return [
        "What evidence do I need?",
        "Where does this typically fail?",
        "Give me procurement language",
        "How does this map to other frameworks?",
      ];
    case 'scenario':
      return [
        "Which controls activate here?",
        "What's PB's role in this scenario?",
        "What customer responsibilities apply?",
      ];
    case 'openq':
      return view.id
        ? ["What does this block?", "Who needs to decide?", "What are my options?"]
        : ["What's the most blocking OQ?", "Group by decision owner"];
    case 'graph':
      return [
        "Which controls are most-leveraged?",
        "Which framework has the most outgoing edges?",
        "Show me unused anchor reqs",
      ];
    default:
      return [];
  }
}

// ─── Streaming SSE parser ────────────────────────────────────────────────────

async function* parseSSE(response) {
  if (!response.body) {
    yield { error: 'No response body — check that ANTHROPIC_API_KEY is set in Vercel env vars.' };
    return;
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split('\n\n');
    buffer = events.pop() || '';
    for (const evt of events) {
      const line = evt.trim();
      if (!line.startsWith('data:')) continue;
      const payload = line.slice(5).trim();
      try {
        yield JSON.parse(payload);
      } catch {
        // skip malformed
      }
    }
  }
}

// ─── Chat bubble ──────────────────────────────────────────────────────────────

function ChatBubble({ role, content, mode, onCitationClick }) {
  const isUser = role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${
          isUser
            ? 'bg-stone-900 text-stone-50'
            : 'bg-stone-100 text-stone-900 border border-stone-200'
        }`}
      >
        {!isUser && mode && mode !== 'explain' && (
          <div className="text-[10px] uppercase tracking-wider text-stone-500 mb-1 flex items-center gap-1">
            <Sparkles size={10} />
            {mode} mode
          </div>
        )}
        {isUser ? (
          <div className="whitespace-pre-wrap">{content}</div>
        ) : (
          <div className="prose prose-sm max-w-none prose-stone">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                a: ({ href, children }) => {
                  const isCitation = typeof href === 'string' && href.startsWith('#');
                  if (isCitation) {
                    const id = href.slice(1);
                    return (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          onCitationClick(id);
                        }}
                        className="font-mono text-xs text-indigo-700 hover:text-indigo-900 hover:underline cursor-pointer"
                      >
                        {children}
                      </button>
                    );
                  }
                  return (
                    <a href={href} target="_blank" rel="noopener noreferrer" className="text-indigo-700 hover:underline">
                      {children}
                    </a>
                  );
                },
                code: ({ inline, children, ...props }) =>
                  inline ? (
                    <code className="bg-stone-200 px-1 py-0.5 rounded text-[12px] font-mono" {...props}>
                      {children}
                    </code>
                  ) : (
                    <code className="block bg-stone-200 px-2 py-1 rounded text-[12px] font-mono whitespace-pre overflow-x-auto" {...props}>
                      {children}
                    </code>
                  ),
                table: ({ children }) => (
                  <div className="overflow-x-auto my-2">
                    <table className="min-w-full text-xs border-collapse">{children}</table>
                  </div>
                ),
                th: ({ children }) => <th className="border border-stone-300 px-2 py-1 bg-stone-200 text-left">{children}</th>,
                td: ({ children }) => <td className="border border-stone-300 px-2 py-1 align-top">{children}</td>,
                blockquote: ({ children }) => (
                  <blockquote className="border-l-2 border-stone-400 pl-3 my-2 text-stone-700 italic">
                    {children}
                  </blockquote>
                ),
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Main Assistant component ────────────────────────────────────────────────

export default function Assistant({ view, lens, data, navigate }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [streamingMode, setStreamingMode] = useState(null);
  const [error, setError] = useState(null);
  const [resetOnNav, setResetOnNav] = useState(false);

  const sessionId = useMemo(() => {
    if (typeof window === 'undefined') return null;
    let id = localStorage.getItem(`${STORAGE_PREFIX}session-id`);
    if (!id) {
      id = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2);
      localStorage.setItem(`${STORAGE_PREFIX}session-id`, id);
    }
    return id;
  }, []);

  const scrollRef = useRef(null);
  const inputRef = useRef(null);
  const abortRef = useRef(null);

  // Hydrate messages from localStorage on mount
  useEffect(() => {
    if (!sessionId) return;
    try {
      const raw = localStorage.getItem(`${STORAGE_PREFIX}history-${sessionId}`);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) setMessages(parsed.slice(-MAX_TURNS * 2));
      }
    } catch {
      // ignore
    }
  }, [sessionId]);

  // Persist messages
  useEffect(() => {
    if (!sessionId) return;
    try {
      localStorage.setItem(`${STORAGE_PREFIX}history-${sessionId}`, JSON.stringify(messages.slice(-MAX_TURNS * 2)));
    } catch {
      // ignore
    }
  }, [messages, sessionId]);

  // Reset on nav if toggle is on
  const viewKey = `${view?.type}:${view?.id || ''}`;
  useEffect(() => {
    if (resetOnNav) {
      setMessages([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [viewKey]);

  // Auto-scroll to bottom on new messages or streaming
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, streamingContent]);

  // Focus input when expanded
  useEffect(() => {
    if (isOpen && inputRef.current) inputRef.current.focus();
  }, [isOpen]);

  // Cancel in-flight stream on unmount
  useEffect(() => () => abortRef.current?.abort(), []);

  const handleSend = useCallback(async (overrideInput) => {
    const text = (overrideInput ?? input).trim();
    if (!text || streaming) return;

    setError(null);
    const userMsg = { role: 'user', content: text };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setInput('');
    setStreaming(true);
    setStreamingContent('');
    setStreamingMode(null);

    const route = viewToRoute(view);
    const abortController = new AbortController();
    abortRef.current = abortController;

    try {
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: nextMessages.slice(-MAX_TURNS * 2),
          route,
          lens,
        }),
        signal: abortController.signal,
      });

      if (!resp.ok) {
        let errMsg = `Server returned ${resp.status}`;
        try {
          const body = await resp.json();
          errMsg = body.error || errMsg;
        } catch {
          // ignore
        }
        setError(errMsg);
        setStreaming(false);
        return;
      }

      let accumulated = '';
      let detectedMode = null;
      for await (const event of parseSSE(resp)) {
        if (event.mode) {
          detectedMode = event.mode;
          setStreamingMode(event.mode);
        }
        if (event.delta) {
          accumulated += event.delta;
          setStreamingContent(accumulated);
        }
        if (event.error) {
          setError(event.error);
        }
        if (event.done) break;
      }

      // Commit the streamed message
      if (accumulated) {
        setMessages((prev) => [...prev, { role: 'assistant', content: accumulated, mode: detectedMode }]);
      }
      setStreamingContent('');
      setStreamingMode(null);
    } catch (e) {
      if (e.name !== 'AbortError') {
        setError(e?.message || String(e));
      }
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  }, [input, messages, view, lens, streaming]);

  const handleCitationClick = useCallback((id) => {
    const targetView = resolveIdToView(id, data);
    if (targetView) {
      navigate(targetView);
    }
  }, [data, navigate]);

  const handleReset = useCallback(() => {
    setMessages([]);
    setError(null);
    setStreamingContent('');
    if (sessionId) {
      try {
        localStorage.removeItem(`${STORAGE_PREFIX}history-${sessionId}`);
      } catch {
        // ignore
      }
    }
  }, [sessionId]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  }, [handleSend]);

  // Global keyboard shortcut: Cmd/Ctrl+K
  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(true);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const placeholder = placeholderForView(view, data);
  const suggestions = suggestedForView(view, data);
  const lensLabel = { 'on-prem': 'On-Prem', 'ai-factory': 'AI Factory', both: 'Both' }[lens] || lens;

  // Context-badge: shows scope of what bot has seen
  const contextBadge = (() => {
    switch (view?.type) {
      case 'requirement': {
        for (const fw of Object.values(data.frameworks)) {
          const r = (fw.requirements || []).find((x) => x.id === view.id);
          if (r) return `${fw._id || fw.id} · ${r.native_id || r.id}`;
        }
        return view.id;
      }
      case 'framework':
        return data.frameworks[view.id]?._id || view.id;
      case 'scenario':
        return `scenario · ${view.id}`;
      case 'openq':
        return view.id ? `OQ · ${view.id}` : 'all open questions';
      case 'graph':
        return 'cross-framework graph';
      case 'home':
      default:
        return 'home';
    }
  })();

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 pointer-events-none">
      {/* Expanded panel */}
      {isOpen && (
        <div className="pointer-events-auto mx-auto max-w-3xl mb-2 bg-white border border-stone-300 rounded-t-lg shadow-2xl flex flex-col" style={{ height: '60vh' }}>
          {/* Header */}
          <div className="flex items-center justify-between px-3 py-2 border-b border-stone-200 bg-stone-50 rounded-t-lg">
            <div className="flex items-center gap-2 text-xs">
              <MessageCircle size={14} className="text-stone-600" />
              <span className="font-mono uppercase tracking-wider text-stone-600">Compliance Assistant</span>
              <span className="text-stone-400">·</span>
              <span className="font-mono text-stone-700">{contextBadge}</span>
              <span className="text-stone-400">·</span>
              <span className="text-stone-700">lens: {lensLabel}</span>
            </div>
            <div className="flex items-center gap-1">
              <label className="text-[10px] text-stone-500 flex items-center gap-1 cursor-pointer">
                <input
                  type="checkbox"
                  checked={resetOnNav}
                  onChange={(e) => setResetOnNav(e.target.checked)}
                  className="cursor-pointer"
                />
                reset on nav
              </label>
              <button
                onClick={handleReset}
                title="Reset conversation"
                className="p-1 hover:bg-stone-200 rounded"
              >
                <RotateCcw size={14} className="text-stone-600" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                title="Close"
                className="p-1 hover:bg-stone-200 rounded"
              >
                <ChevronDown size={16} className="text-stone-600" />
              </button>
            </div>
          </div>

          {/* Chat history */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 py-3">
            {messages.length === 0 && !streaming && (
              <div className="text-center text-stone-500 text-sm py-8">
                <Sparkles size={20} className="inline mb-2 text-stone-400" />
                <div className="mb-3">Grounded in {Object.keys(data.frameworks).length} frameworks · {Object.values(data.frameworks).reduce((acc, fw) => acc + (fw.requirements?.length || 0), 0)} controls · current page in primary context</div>
                {suggestions.length > 0 && (
                  <div className="flex flex-wrap gap-2 justify-center mt-4">
                    {suggestions.map((q, i) => (
                      <button
                        key={i}
                        onClick={() => handleSend(q)}
                        className="text-xs px-2 py-1 bg-stone-100 border border-stone-300 rounded-full hover:bg-stone-200 transition-colors"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
            {messages.map((m, i) => (
              <ChatBubble
                key={i}
                role={m.role}
                content={m.content}
                mode={m.mode}
                onCitationClick={handleCitationClick}
              />
            ))}
            {streaming && (
              <ChatBubble
                role="assistant"
                content={streamingContent || '…'}
                mode={streamingMode}
                onCitationClick={handleCitationClick}
              />
            )}
            {error && (
              <div className="text-xs text-red-700 bg-red-50 border border-red-200 rounded px-2 py-1 mt-2">
                {error}
              </div>
            )}
          </div>

          {/* Footer disclaimer */}
          <div className="px-3 py-1 text-[10px] text-stone-500 border-t border-stone-200 bg-stone-50">
            Grounded in PrivateBox GRC OS. Verify against published source standards before reliance.
          </div>
        </div>
      )}

      {/* Collapsed input bar — always present */}
      <div className="pointer-events-auto mx-auto max-w-3xl bg-white border-t border-l border-r border-stone-300 rounded-t-lg shadow-lg">
        <div className="flex items-center gap-2 px-3 py-2">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="p-1 hover:bg-stone-100 rounded"
            title={isOpen ? 'Collapse' : 'Expand'}
          >
            {isOpen ? <ChevronDown size={16} className="text-stone-600" /> : <MessageCircle size={16} className="text-stone-600" />}
          </button>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => !isOpen && setIsOpen(true)}
            placeholder={placeholder}
            className="flex-1 text-sm bg-transparent outline-none placeholder-stone-400"
            disabled={streaming}
          />
          {streaming ? (
            <Loader2 size={16} className="text-stone-600 animate-spin" />
          ) : (
            <button
              onClick={() => handleSend()}
              disabled={!input.trim()}
              className="p-1 hover:bg-stone-100 rounded disabled:opacity-30 disabled:cursor-not-allowed"
              title="Send (Enter)"
            >
              <Send size={16} className="text-stone-700" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
