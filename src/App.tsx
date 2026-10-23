import { useState } from 'react';
import Header from './components/Header';
import ArchitectureView from './components/ArchitectureView';
import CodeView from './components/CodeView';
import StackView from './components/StackView';
import EndpointsView from './components/EndpointsView';
import QueuefyView from './components/QueuefyView';

type Tab = 'architecture' | 'code' | 'stack' | 'endpoints' | 'queuefy';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('architecture');

  return (
    <div className="min-h-screen flex flex-col">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      
      <main className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full">
        <div className="animate-slide-in">
          {activeTab === 'architecture' && <ArchitectureView />}
          {activeTab === 'code' && <CodeView />}
          {activeTab === 'stack' && <StackView />}
          {activeTab === 'endpoints' && <EndpointsView />}
          {activeTab === 'queuefy' && <QueuefyView />}
        </div>
      </main>

      <footer className="border-t border-slate-800 py-4 text-center text-slate-500 text-sm">
        <p>Async POC — FastAPI + uvloop + Granian + Prefect + Queuefy + NiceGUI — 100% Async, Flat Structure</p>
      </footer>
    </div>
  );
}

export default App;
