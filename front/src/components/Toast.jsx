import { useApp } from '../store'

export default function Toast() {
  const { toasts, removeToast } = useApp()

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map(t => (
        <div
          key={t.id}
          className={`px-4 py-3 rounded-lg shadow-lg border text-sm flex items-start gap-3 max-w-sm animate-slide-up ${
            t.type === 'error'
              ? 'bg-red-500/10 border-red-500/30 text-red-400'
              : 'bg-green-500/10 border-green-500/30 text-green-400'
          }`}
        >
          <span className="flex-1">{t.message}</span>
          <button
            onClick={() => removeToast(t.id)}
            className="text-current opacity-50 hover:opacity-100 text-lg leading-none"
          >
            &times;
          </button>
        </div>
      ))}
    </div>
  )
}
