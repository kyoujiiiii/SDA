import { useState, useEffect } from 'react'
import { getAudit, getSessionAudit } from '../api'
import { useApp } from '../store'

export default function AuditLog() {
  const { sessionId, addToast } = useApp()
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [limit, setLimit] = useState(20)
  const [expandedId, setExpandedId] = useState(null)
  const [filterSession, setFilterSession] = useState(sessionId || '')

  const load = async () => {
    setLoading(true)
    try {
      const data = filterSession.trim()
        ? await getSessionAudit(filterSession.trim(), limit)
        : await getAudit(limit)
      setEntries(data.entries || [])
    } catch (err) {
      addToast(err.message, 'error')
      setEntries([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [limit, filterSession])

  useEffect(() => {
    if (sessionId && !filterSession) {
      setFilterSession(sessionId)
    }
  }, [sessionId])

  const formatTime = (ts) => {
    if (!ts) return '-'
    return new Date(ts * 1000).toLocaleTimeString()
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h2 className="text-xl font-semibold text-white">Audit Log</h2>
        <div className="flex items-center gap-3">
          <input
            value={filterSession}
            onChange={e => setFilterSession(e.target.value)}
            placeholder="Filter by session ID"
            className="bg-airlock-input text-airlock-text border border-airlock-border rounded-lg px-3 py-1.5 text-xs font-mono outline-none focus:border-airlock-blue w-64"
          />
          <select
            value={limit}
            onChange={e => setLimit(Number(e.target.value))}
            className="bg-airlock-input text-airlock-text border border-airlock-border rounded-lg px-2 py-1.5 text-xs outline-none"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
          <button onClick={load} disabled={loading} className="text-xs text-airlock-muted hover:text-airlock-text transition-colors">
            Refresh
          </button>
        </div>
      </div>

      {loading && entries.length === 0 ? (
        <div className="flex items-center justify-center h-40">
          <div className="w-6 h-6 border-2 border-airlock-blue border-t-transparent rounded-full animate-spin" />
        </div>
      ) : entries.length === 0 ? (
        <div className="text-airlock-subtle text-sm italic text-center py-10">No audit entries found</div>
      ) : (
        <div className="bg-airlock-card border border-airlock-border rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-airlock-border bg-airlock-bg/50">
                <th className="text-left px-4 py-3 text-airlock-muted font-medium text-xs">Time</th>
                <th className="text-left px-4 py-3 text-airlock-muted font-medium text-xs">Role</th>
                <th className="text-left px-4 py-3 text-airlock-muted font-medium text-xs">Masked Prompt</th>
                <th className="text-center px-4 py-3 text-airlock-muted font-medium text-xs">Entities</th>
                <th className="text-left px-4 py-3 text-airlock-muted font-medium text-xs">Model</th>
                <th className="text-right px-4 py-3 text-airlock-muted font-medium text-xs">Latency</th>
              </tr>
            </thead>
            <tbody>
              {entries.map(entry => (
                <tr
                  key={entry.id}
                  className="border-b border-airlock-border/50 cursor-pointer hover:bg-airlock-border/20 transition-colors"
                  onClick={() => setExpandedId(expandedId === entry.id ? null : entry.id)}
                >
                  <td className="px-4 py-2.5 font-mono text-xs text-airlock-muted">{formatTime(entry.created_at)}</td>
                  <td className="px-4 py-2.5">
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${entry.role === 'admin' ? 'bg-airlock-green/15 text-airlock-green' : 'bg-airlock-yellow/15 text-airlock-yellow'}`}>
                      {entry.role}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 font-mono text-xs text-airlock-text truncate max-w-[300px]">{entry.masked_prompt}</td>
                  <td className="px-4 py-2.5 text-center">
                    <span className="text-xs font-mono text-airlock-cyan">{entry.entity_count}</span>
                  </td>
                  <td className="px-4 py-2.5 font-mono text-xs text-airlock-muted">{entry.llm_model}</td>
                  <td className="px-4 py-2.5 text-right font-mono text-xs text-airlock-muted">{entry.latency_ms}ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
