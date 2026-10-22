import { type Tab } from '../types';

interface HeaderProps {
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
}

const tabs: { id: Tab; label: string; icon: string }[] = [
  { id: 'architecture', label: 'Arquitetura', icon: '🏗️' },
  { id: 'code', label: 'Código', icon: '💻' },
  { id: 'stack', label: 'Stack', icon: '📦' },
  { id: 'endpoints', label: 'Endpoints', icon: '🔌' },
];

export default function Header({ activeTab, onTabChange }: HeaderProps) {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 md:px-8">
        {/* Top bar */}
        <div className="flex items-center justify-between py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xl">
              ⚡
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">Async POC</h1>
              <p className="text-xs text-slate-400">FastAPI + Granian + Queuefy + NiceGUI</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20">
              <span className="pulse-dot bg-green-400"></span>
              <span className="text-xs text-green-400 font-medium">100% Async</span>
            </div>
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20">
              <span className="pulse-dot bg-blue-400"></span>
              <span className="text-xs text-blue-400 font-medium">uvloop</span>
            </div>
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20">
              <span className="text-xs text-purple-400 font-medium">🐦 uv</span>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex gap-1 pb-3 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`nav-link whitespace-nowrap flex items-center gap-2 ${
                activeTab === tab.id ? 'active' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
}
