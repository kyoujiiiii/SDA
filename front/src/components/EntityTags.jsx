const ENTITY_COLORS = {
  PERSON: { bg: 'bg-blue-500/15', text: 'text-blue-400', border: 'border-blue-500/30' },
  EMAIL: { bg: 'bg-green-500/15', text: 'text-green-400', border: 'border-green-500/30' },
  PHONE: { bg: 'bg-purple-500/15', text: 'text-purple-400', border: 'border-purple-500/30' },
  LOCATION: { bg: 'bg-yellow-500/15', text: 'text-yellow-400', border: 'border-yellow-500/30' },
  IBAN: { bg: 'bg-orange-500/15', text: 'text-orange-400', border: 'border-orange-500/30' },
  AHV: { bg: 'bg-red-500/15', text: 'text-red-400', border: 'border-red-500/30' },
  CREDIT_CARD: { bg: 'bg-pink-500/15', text: 'text-pink-400', border: 'border-pink-500/30' },
  IP_ADDRESS: { bg: 'bg-cyan-500/15', text: 'text-cyan-400', border: 'border-cyan-500/30' },
  PERSON_1: { bg: 'bg-blue-500/15', text: 'text-blue-400', border: 'border-blue-500/30' },
  IBAN_1: { bg: 'bg-orange-500/15', text: 'text-orange-400', border: 'border-orange-500/30' },
}

const DEFAULT_COLOR = { bg: 'bg-gray-500/15', text: 'text-gray-400', border: 'border-gray-500/30' }

export default function EntityTags({ entities }) {
  if (!entities || entities.length === 0) return null

  return (
    <div className="border-t border-airlock-border pt-3 mt-3">
      <div className="text-[11px] text-airlock-muted mb-2 uppercase tracking-wider font-medium">
        Detected PII ({entities.length})
      </div>
      <div className="flex flex-wrap gap-1.5">
        {entities.map((e, i) => {
          const colors = ENTITY_COLORS[e.entity_type] || DEFAULT_COLOR
          return (
            <span
              key={i}
              title={e.original_value}
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono border ${colors.bg} ${colors.text} ${colors.border} cursor-default`}
            >
              {e.token}
              <span className="opacity-50 text-[10px]">{e.entity_type}</span>
            </span>
          )
        })}
      </div>
    </div>
  )
}
