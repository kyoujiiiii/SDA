import { useState, useEffect } from 'react'
import { getStats } from '../api'
import { useApp } from '../store'

export default function StatsPanel() {
  const { addToast } = useApp()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const data = await getStats()
      setStats(data)
    } catch (err) {
      addToast(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    const interval = setInterval(load, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading && !stats) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <div className="w-6 h-6 border-2 border-airlock-blue border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!stats) {
    return <div className="p-6 text-airlock-subtle">Failed to load stats</div>
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-white">System Statistics</h2>
        <button
          onClick={load}
          className="text-xs text-airlock-muted hover:text-airlock-text transition-colors"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard title="Vault" icon="🔐" stats={stats.vault} />
        <StatCard title="LLM" icon="🤖" stats={stats.llm} />
        <StatCard title="Audit" icon="📋" stats={stats.audit} />
      </div>
    </div>
  )
}

function StatCard({ title, icon, stats }) {
  if (!stats) return null

  const entries = Object.entries(stats).filter(([k]) => k !== 'backend' && k !== 'mode')

  return (
    <div className="bg-airlock-card border border-airlock-border rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-lg">{icon}</span>
        <span className="text-sm font-semibold text-airlock-muted uppercase tracking-wider">{title}</span>
        {stats.backend && (
          <span className="ml-auto text-[10px] px-2 py-0.5 rounded-full bg-airlock-border text-airlock-muted font-mono">
            {stats.backend}
          </span>
        )}
        {stats.mode && (
          <span className={`ml-auto text-[10px] px-2 py-0.5 rounded-full font-mono ${
            stats.mode === 'live' ? 'bg-airlock-green/15 text-airlock-green' : 'bg-airlock-yellow/15 text-airlock-yellow'
          }`}>
            {stats.mode}
          </span>
        )}
      </div>
      <div className="space-y-3">
        {entries.map(([key, value]) => (
          <div key={key} className="flex items-baseline justify-between">
            <span className="text-xs text-airlock-muted capitalize">
              {key.replace(/_/g, ' ')}
            </span>
            <span className="font-mono text-lg text-white font-semibold">
              {typeof value === 'number' ? value.toLocaleString() : String(value)}
              {key.includes('latency') && <span className="text-xs text-airlock-muted ml-1">ms</span>}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
