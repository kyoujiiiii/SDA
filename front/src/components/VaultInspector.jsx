import { useState } from 'react'
import { useApp } from '../store'
import { getVault, deleteVault } from '../api'
import { useApi } from '../hooks/useApi'

export default function VaultInspector() {
  const { sessionId, addToast } = useApp()
  const [lookupId, setLookupId] = useState(sessionId || '')
  const { loading, data, execute } = useApi(getVault)
  const { execute: executeDelete, loading: deleting } = useApi(deleteVault)

  const handleLoad = async () => {
    if (!lookupId.trim()) return
    try {
      await execute(lookupId.trim())
    } catch (err) {
      addToast(err.message, 'error')
    }
  }

  const handleDelete = async () => {
    if (!lookupId.trim()) return
    try {
      await executeDelete(lookupId.trim())
      addToast('Session deleted', 'success')
    } catch (err) {
      addToast(err.message, 'error')
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <h2 className="text-xl font-semibold text-white">Vault Inspector</h2>

      <div className="flex gap-2">
        <input
          value={lookupId}
          onChange={e => setLookupId(e.target.value)}
          placeholder="Session ID"
          className="flex-1 bg-airlock-input text-airlock-text border border-airlock-border rounded-lg px-3 py-2 text-sm font-mono outline-none focus:border-airlock-blue"
          onKeyDown={e => e.key === 'Enter' && handleLoad()}
        />
        <button
          onClick={handleLoad}
          disabled={loading || !lookupId.trim()}
          className="px-4 py-2 rounded-lg bg-airlock-blue text-white text-sm font-semibold hover:opacity-90 disabled:opacity-40 transition-opacity"
        >
          {loading ? 'Loading...' : 'Load'}
        </button>
        <button
          onClick={handleDelete}
          disabled={deleting || !lookupId.trim()}
          className="px-4 py-2 rounded-lg bg-airlock-red/15 text-airlock-red border border-airlock-red/30 text-sm font-semibold hover:bg-airlock-red/25 disabled:opacity-40 transition-opacity"
        >
          {deleting ? 'Deleting...' : 'Delete'}
        </button>
      </div>

      {data && (
        <div className="space-y-4">
          <div className="bg-airlock-card border border-airlock-border rounded-xl p-4">
            <div className="text-xs text-airlock-muted uppercase tracking-wider font-medium mb-3">
              Token Mappings
            </div>
            {Object.keys(data.mappings).length === 0 ? (
              <div className="text-airlock-subtle text-sm italic">No mappings found</div>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-airlock-border">
                    <th className="text-left py-2 text-airlock-muted font-medium">Token</th>
                    <th className="text-left py-2 text-airlock-muted font-medium">Original Value</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(data.mappings).map(([token, value]) => (
                    <tr key={token} className="border-b border-airlock-border/50">
                      <td className="py-2 font-mono text-airlock-yellow">{token}</td>
                      <td className="py-2 font-mono text-airlock-text">{value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {data.session_info && (
            <div className="bg-airlock-card border border-airlock-border rounded-xl p-4">
              <div className="text-xs text-airlock-muted uppercase tracking-wider font-medium mb-3">
                Session Info
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-airlock-muted text-xs">Session ID</div>
                  <div className="font-mono text-airlock-cyan truncate">{data.session_info.session_id}</div>
                </div>
                <div>
                  <div className="text-airlock-muted text-xs">Token Count</div>
                  <div className="font-mono text-airlock-cyan">{data.session_info.token_count}</div>
                </div>
                <div>
                  <div className="text-airlock-muted text-xs">Request Count</div>
                  <div className="font-mono text-airlock-cyan">{data.session_info.request_count}</div>
                </div>
                <div>
                  <div className="text-airlock-muted text-xs">Age</div>
                  <div className="font-mono text-airlock-cyan">{Math.round(data.session_info.age_seconds)}s</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
