export default function LoadingOverlay({ show }) {
  if (!show) return null
  return (
    <div className="absolute inset-0 bg-airlock-bg/70 backdrop-blur-sm flex items-center justify-center z-10 rounded-xl">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-airlock-blue border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-airlock-muted">Processing through Airlock...</span>
      </div>
    </div>
  )
}
