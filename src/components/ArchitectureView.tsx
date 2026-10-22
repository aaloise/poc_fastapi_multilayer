import { type Layer } from '../types';

const layers: Layer[] = [
  {
    name: 'Entry Point',
    description: 'main.py — Setup e lifespan',
    color: 'from-blue-500 to-cyan-500',
    glowClass: 'glow-blue',
    icon: '🚀',
    components: ['FastAPI app', 'Lifespan (startup/shutdown)', 'Middleware CORS', 'Router registration'],
  },
  {
    name: 'Routes',
    description: 'routes.py — Endpoints HTTP',
    color: 'from-cyan-500 to-teal-500',
    glowClass: 'glow-blue',
    icon: '🔌',
    components: ['POST /tasks', 'GET /tasks', 'GET /tasks/{id}', 'GET /health', 'POST /flows/*'],
  },
  {
    name: 'Services',
    description: 'services.py — Business logic',
    color: 'from-green-500 to-emerald-500',
    glowClass: 'glow-green',
    icon: '⚙️',
    components: ['create_task()', 'execute_task()', 'get_task_by_id()', 'get_all_tasks()', 'get_stats()'],
  },
  {
    name: 'Models',
    description: 'models.py — Domain + DB (juntos)',
    color: 'from-yellow-500 to-amber-500',
    glowClass: 'glow-orange',
    icon: '📦',
    components: ['Task (Pydantic)', 'TaskRow (SQLAlchemy)', 'TaskStatus', 'Priority', 'DB operations'],
  },
  {
    name: 'Infrastructure',
    description: 'database.py + queue.py + flows.py',
    color: 'from-purple-500 to-pink-500',
    glowClass: 'glow-purple',
    icon: '🔧',
    components: ['SQLAlchemy async', 'Queuefy (task queue)', 'Prefect (workflows)', 'NiceGUI (UI)'],
  },
];

export default function ArchitectureView() {
  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="text-center">
        <h2 className="text-3xl font-bold gradient-text mb-2">Arquitetura Simples</h2>
        <p className="text-slate-400">Flat structure — sem camadas desnecessárias</p>
      </div>

      {/* File structure */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>📁</span> Estrutura de Arquivos
        </h3>
        <div className="code-block text-sm">
          <code className="text-slate-300">
            <span className="text-slate-500">backend/src/app/</span>{'\n'}
            <span className="text-blue-400">├── main.py</span>
            <span className="text-slate-500">          # Entry point + lifespan</span>{'\n'}
            <span className="text-blue-400">├── config.py</span>
            <span className="text-slate-500">        # Settings (pydantic)</span>{'\n'}
            <span className="text-green-400">├── models.py</span>
            <span className="text-slate-500">       # Domain + DB models (juntos)</span>{'\n'}
            <span className="text-emerald-400">├── services.py</span>
            <span className="text-slate-500">     # Business logic</span>{'\n'}
            <span className="text-cyan-400">├── routes.py</span>
            <span className="text-slate-500">       # FastAPI routes</span>{'\n'}
            <span className="text-pink-400">├── ui.py</span>
            <span className="text-slate-500">           # NiceGUI pages</span>{'\n'}
            <span className="text-purple-400">├── queue.py</span>
            <span className="text-slate-500">        # Queuefy integration</span>{'\n'}
            <span className="text-purple-400">├── flows.py</span>
            <span className="text-slate-500">        # Prefect flows</span>{'\n'}
            <span className="text-purple-400">└── database.py</span>
            <span className="text-slate-500">     # DB setup</span>
          </code>
        </div>
      </div>

      {/* Components flow */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>🔄</span> Fluxo de Execução
        </h3>
        <div className="flex flex-wrap items-center justify-center gap-2 text-sm">
          <span className="px-3 py-2 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400">HTTP Request</span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-2 rounded-lg bg-orange-500/10 border border-orange-500/30 text-orange-400">Granian</span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">FastAPI</span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-2 rounded-lg bg-green-500/10 border border-green-500/30 text-green-400">Service</span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-2 rounded-lg bg-purple-500/10 border border-purple-500/30 text-purple-400">DB/Queue</span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-2 rounded-lg bg-pink-500/10 border border-pink-500/30 text-pink-400">Response</span>
        </div>
      </div>

      {/* Key principles */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>💡</span> Princípios
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-green-500/5 border border-green-500/20">
            <p className="text-green-400 font-medium mb-2">✅ Simples</p>
            <ul className="text-sm text-slate-300 space-y-1">
              <li>• 9 arquivos no total</li>
              <li>• Sem camadas desnecessárias</li>
              <li>• Models + DB juntos</li>
              <li>• Fácil de entender</li>
            </ul>
          </div>
          <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/20">
            <p className="text-blue-400 font-medium mb-2">⚡ 100% Async</p>
            <ul className="text-sm text-slate-300 space-y-1">
              <li>• uvloop event loop</li>
              <li>• Granian (Rust) server</li>
              <li>• SQLAlchemy async</li>
              <li>• Queuefy async queue</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Server stack */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>🦀</span> Server Stack
        </h3>
        <div className="flex items-center justify-center gap-4 p-4 rounded-xl bg-gradient-to-r from-orange-500/10 via-red-500/10 to-orange-500/10 border border-orange-500/20">
          <div className="text-center">
            <div className="text-3xl mb-2">🦀</div>
            <p className="font-bold text-orange-400">Granian</p>
            <p className="text-xs text-slate-400">Rust ASGI Server</p>
          </div>
          <div className="text-2xl text-slate-600">+</div>
          <div className="text-center">
            <div className="text-3xl mb-2">🔄</div>
            <p className="font-bold text-cyan-400">uvloop</p>
            <p className="text-xs text-slate-400">Fast Event Loop</p>
          </div>
          <div className="text-2xl text-slate-600">+</div>
          <div className="text-center">
            <div className="text-3xl mb-2">⚡</div>
            <p className="font-bold text-blue-400">FastAPI</p>
            <p className="text-xs text-slate-400">Async Framework</p>
          </div>
        </div>
      </div>
    </div>
  );
}
