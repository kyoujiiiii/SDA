import { createContext, useContext, useState, useCallback } from 'react'

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [currentTab, setCurrentTab] = useState('demo')
  const [role, setRole] = useState('admin')
  const [sessionId, setSessionId] = useState(null)
  const [health, setHealth] = useState(null)
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'error') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 5000)
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  return (
    <AppContext.Provider
      value={{
        currentTab, setCurrentTab,
        role, setRole,
        sessionId, setSessionId,
        health, setHealth,
        toasts, addToast, removeToast,
      }}
    >
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used within AppProvider')
  return ctx
}
