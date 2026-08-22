import { useEffect } from 'react'
import { useApp } from '../store'
import { getHealth } from '../api'

export default function Header() {
  const { role, setRole, health, setHealth } = useApp()

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'error' }))
    const interval = setInterval(() => {
      getHealth().then(setHealth).catch(() => setHealth({ status: 'error' }))
    }, 30000)
    return () => clearInterval(interval)
  }, [setHealth])

  return (
    <header className="bg-airlock-card border-b border-airlock-border px-6 py-3 flex items-center gap-4">
      <h1 className="text-lg font-semibold text-white tracking-tight">Swiss Data Airlock</h1>
      <span className="bg-airlock-green text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
        MVP
      </span>

      <div className="ml-auto flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs text-airlock-muted">
          <span
            className={`w-2 h-2 rounded-full ${
              health?.status === 'ok' ? 'bg-airlock-green' : 'bg-airlock-red'
            }`}
          />
          {health?.status === 'ok' ? (
            <span>
              Vault: <span className="text-airlock-cyan">{health.vault}</span> | LLM:{' '}
              <span className="text-airlock-cyan">{health.llm}</span>
            </span>
          ) : (
            <span className="text-airlock-red">Disconnected</span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <label htmlFor="role" className="text-xs text-airlock-muted">
            View as:
          </label>
          <select
            id="role"
            value={role}
            onChange={e => setRole(e.target.value)}
            className="bg-airlock-input text-airlock-text border border-airlock-border rounded-md px-2 py-1 text-xs outline-none focus:border-airlock-blue"
          >
            <option value="admin">Admin (Data Owner)</option>
            <option value="auditor">Auditor (Cloud View)</option>
          </select>
        </div>
      </div>
    </header>
  )
}
