import { AppProvider, useApp } from './store'
import Header from './components/Header'
import TabNav from './components/TabNav'
import DemoView from './components/DemoView'
import VaultInspector from './components/VaultInspector'
import StatsPanel from './components/StatsPanel'
import AuditLog from './components/AuditLog'
import Toast from './components/Toast'

function TabContent() {
  const { currentTab } = useApp()

  switch (currentTab) {
    case 'demo':
      return <DemoView />
    case 'vault':
      return <VaultInspector />
    case 'stats':
      return <StatsPanel />
    case 'audit':
      return <AuditLog />
    default:
      return <DemoView />
  }
}

export default function App() {
  return (
    <AppProvider>
      <div className="min-h-screen flex flex-col bg-airlock-bg">
        <Header />
        <TabNav />
        <main className="flex-1 overflow-y-auto">
          <TabContent />
        </main>
        <Toast />
      </div>
    </AppProvider>
  )
}
