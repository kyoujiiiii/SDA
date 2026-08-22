export default function MaskedPanel({ maskedPayload }) {
  return (
    <div className="bg-airlock-card border border-airlock-border rounded-xl flex flex-col overflow-hidden">
      <div className="px-4 py-3 border-b border-airlock-border flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-airlock-yellow" />
        <span className="text-xs font-semibold text-airlock-muted uppercase tracking-wider">
          Airlock Outbound — Cloud View
        </span>
      </div>

      <div className="flex-1 p-4 overflow-y-auto">
        {maskedPayload ? (
          <pre className="font-mono text-sm leading-relaxed text-airlock-text whitespace-pre-wrap break-word">
            {highlightTokens(maskedPayload)}
          </pre>
        ) : (
          <div className="text-airlock-subtle italic text-sm">
            What the LLM cloud sees...
          </div>
        )}
      </div>
    </div>
  )
}

function highlightTokens(text) {
  const parts = text.split(/(\[[A-Z_]+_\d+\])/g)
  return parts.map((part, i) => {
    if (/^\[[A-Z_]+_\d+\]$/.test(part)) {
      return (
        <span
          key={i}
          className="bg-airlock-yellow/15 text-airlock-yellow border border-airlock-yellow/30 rounded px-1 mx-0.5 font-semibold"
        >
          {part}
        </span>
      )
    }
    return <span key={i}>{part}</span>
  })
}
