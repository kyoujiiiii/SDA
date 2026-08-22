import { useState, useCallback } from 'react'
import { useApp } from '../store'
import { chat } from '../api'
import InputPanel from './InputPanel'
import MaskedPanel from './MaskedPanel'
import ResponsePanel from './ResponsePanel'
import LoadingOverlay from './LoadingOverlay'

export default function DemoView() {
  const { role, sessionId, setSessionId, addToast } = useApp()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleSend = useCallback(async (prompt) => {
    setLoading(true)
    try {
      const res = await chat(prompt, role, sessionId)
      setSessionId(res.session_id)
      setResult(res)
    } catch (err) {
      addToast(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }, [role, sessionId, setSessionId, addToast])

  const handleClear = () => {
    setResult(null)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-full p-4">
      <div className="relative min-h-[400px]">
        <LoadingOverlay show={loading} />
        <InputPanel onSend={handleSend} loading={loading} />
      </div>
      <MaskedPanel maskedPayload={result?.masked_payload} />
      <ResponsePanel result={result} />
    </div>
  )
}
