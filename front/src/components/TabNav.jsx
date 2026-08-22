import { useApp } from '../store'

const tabs = [
  { id: 'demo', label: 'Demo' },
  { id: 'vault', label: 'Vault' },
  { id: 'stats', label: 'Stats' },
  { id: 'audit', label: 'Audit' },
]

export default function TabNav() {
  const { currentTab, setCurrentTab } = useApp()

  return (
    <nav className="flex gap-1 px-6 py-2 bg-airlock-card border-b border-airlock-border">
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => setCurrentTab(tab.id)}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
            currentTab === tab.id
              ? 'bg-airlock-blue/15 text-airlock-blue'
              : 'text-airlock-muted hover:text-airlock-text hover:bg-airlock-border/50'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  )
}
