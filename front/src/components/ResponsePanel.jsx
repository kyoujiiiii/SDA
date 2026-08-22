import EntityTags from './EntityTags'

export default function ResponsePanel({ result }) {
  return (
    <div className="bg-airlock-card border border-airlock-border rounded-xl flex flex-col overflow-hidden">
      <div className="px-4 py-3 border-b border-airlock-border flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-airlock-green" />
        <span className="text-xs font-semibold text-airlock-muted uppercase tracking-wider">
          Response — Final Output
        </span>
      </div>

      <div className="flex-1 p-4 overflow-y-auto">
        {result ? (
          <>
            <pre className="font-mono text-sm leading-relaxed text-airlock-text whitespace-pre-wrap break-word">
              {result.final_response}
            </pre>

            {result.detected_entities?.length > 0 && (
              <EntityTags entities={result.detected_entities} />
            )}

            <div className="mt-4 pt-3 border-t border-airlock-border flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-airlock-muted">
              <span>
                Session: <span className="text-airlock-cyan font-mono">{result.session_id?.slice(0, 8)}...</span>
              </span>
              <span>
                Model: <span className="text-airlock-cyan font-mono">{result.llm_model}</span>
              </span>
              <span>
                Latency: <span className="text-airlock-cyan font-mono">{result.latency_ms}ms</span>
              </span>
              {result.token_usage && (
                <span>
                  Tokens: <span className="text-airlock-cyan font-mono">{result.token_usage.total_tokens}</span>
                </span>
              )}
            </div>
          </>
        ) : (
          <div className="text-airlock-subtle italic text-sm">
            Response from the Airlock...
          </div>
        )}
      </div>
    </div>
  )
}
