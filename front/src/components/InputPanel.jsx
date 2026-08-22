import { useState } from 'react'

const EXAMPLES = [
  'Send CHF 50,000 to Hans Peter, IBAN CH9300000000000000000',
  'Contact maria@example.com or call +41 79 123 45 67',
  'Employee AHV: 756.1234.5678.90, address Bahnhofstrasse 1, Zurich',
  'Invoice for TechCorp AG, amount CHF 12,500.00, due 2026-03-15',
]

export default function InputPanel({ onSend, loading }) {
  const [input, setInput] = useState('')

  const handleSend = () => {
    const trimmed = input.trim()
    if (!trimmed || loading) return
    onSend(trimmed)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      handleSend()
    }
  }

  const loadExample = (text) => {
    setInput(text)
  }

  return (
    <div className="bg-airlock-card border border-airlock-border rounded-xl flex flex-col overflow-hidden relative">
      <div className="px-4 py-3 border-b border-airlock-border flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-airlock-red" />
        <span className="text-xs font-semibold text-airlock-muted uppercase tracking-wider">
          Input — Raw Text
        </span>
      </div>

      <div className="flex-1 p-3">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a prompt with sensitive data..."
          className="w-full h-full min-h-[200px] bg-airlock-input text-airlock-text border border-airlock-border rounded-lg p-3 font-mono text-sm leading-relaxed resize-none outline-none focus:border-airlock-blue transition-colors"
        />
      </div>

      <div className="px-3 pb-3 flex flex-wrap gap-1.5">
        <span className="text-[11px] text-airlock-subtle self-center mr-1">Examples:</span>
        {EXAMPLES.map((ex, i) => (
          <button
            key={i}
            onClick={() => loadExample(ex)}
            className="text-[11px] px-2 py-0.5 rounded bg-airlock-border/50 text-airlock-muted hover:text-airlock-text hover:bg-airlock-border transition-colors truncate max-w-[200px]"
            title={ex}
          >
            {ex.length > 30 ? ex.slice(0, 30) + '...' : ex}
          </button>
        ))}
      </div>

      <div className="px-3 pb-3 flex items-center gap-2">
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="px-4 py-2 rounded-lg bg-airlock-green text-white text-sm font-semibold hover:bg-airlock-green-hover disabled:bg-airlock-border disabled:text-airlock-subtle disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Processing...' : 'Send to Airlock'}
        </button>
        <button
          onClick={() => setInput('')}
          className="px-4 py-2 rounded-lg bg-airlock-border text-airlock-muted text-sm font-medium hover:bg-airlock-subtle/50 transition-colors"
        >
          Clear
        </button>
      </div>
    </div>
  )
}
