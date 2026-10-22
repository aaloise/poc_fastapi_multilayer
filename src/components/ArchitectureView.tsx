import { type Layer } from '../types';

const layers: Layer[] = [
  {
    name: 'Presentation',
    description: 'FastAPI REST API + NiceGUI Interactive UI',
    color: 'from-blue-500 to-cyan-500',
    glowClass: 'glow-blue',
    icon: '📡',
    components: ['FastAPI Router (/api/v1/*)', 'NiceGUI Pages (/ui/*)', 'Request/Response DTOs', 'Dependency Injection'],
  },
  {
    name: 'Application',
    description: 'Use Cases & Orchestrators',
    color: 'from-green-500 to-emerald-500',
    glowClass: 'glow-green',
    icon: '⚙️',
    components: ['TaskService', 'create_task()', 'execute_task()', 'list_tasks() / get_stats()'],
  },
  {
    name: 'Domain',
    description: 'Entities, Value Objects & Repository Ports',
    color: 'from-yellow-500 to-amber-500',
    glowClass: 'glow-orange',
    icon: '🧱',
    components: ['Task Entity', 'TaskResult', 'TaskStatus / Priority', 'TaskRepository (Protocol)'],
  },
  {
    name: 'Infrastructure',
    description: 'Adapters & External Integrations',
    color: 'from-purple-500 to-pink-500',
    glowClass: 'glow-purple',
    icon: '🔧',
    components: ['SQLAlchemyTaskRepository', 'QueueManager (Queuefy)', 'Prefect Flows', 'Async Database Engine'],
  },
];

export default function ArchitectureView() {
  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="text-center">
        <h2 className="text-3xl font-bold gradient-text mb-2">Arquitetura em Camadas</h2>
        <p className="text-slate-400">Separação de responsabilidades com dependências apontando para dentro</p>
      </div>

      {/* Architecture Diagram */}
      <div className="glass-card p-6 md:p-8">
        <div className="space-y-4">
          {/* Server Bar */}
          <div className="flex items-center justify-center gap-4 p-4 rounded-xl bg-gradient-to-r from-orange-500/10 via-red-500/10 to-orange-500/10 border border-orange-500/20">
            <span className="text-2xl">🦀</span>
            <div className="text-center">
              <p className="font-bold text-orange-400">Granian (Rust ASGI Server)</p>
              <p className="text-xs text-slate-400">+ uvloop event loop + HTTP/2 + WebSocket</p>
            </div>
            <span className="text-2xl">🔄</span>
          </div>

          {/* Arrow */}
          <div className="flex justify-center">
            <div className="w-0.5 h-6 bg-gradient-to-b from-orange-500/50 to-blue-500/50"></div>
          </div>

          {/* Layers */}
          {layers.map((layer, idx) => (
            <div key={layer.name} className="animate-slide-in" style={{ animationDelay: `${idx * 100}ms` }}>
              <div className={`layer-card glass-card ${layer.glowClass} p-5`}>
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${layer.color} flex items-center justify-center text-2xl shrink-0`}>
                    {layer.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-bold text-lg">{layer.name}</h3>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-slate-700 text-slate-300">
                        Layer {layers.length - idx}
                      </span>
                    </div>
                    <p className="text-sm text-slate-400 mb-3">{layer.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {layer.components.map((comp) => (
                        <span
                          key={comp}
                          className="text-xs px-2.5 py-1 rounded-lg bg-slate-700/50 border border-slate-600/50 text-slate-300"
                        >
                          {comp}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Arrow between layers */}
              {idx < layers.length - 1 && (
                <div className="flex justify-center py-2">
                  <div className="flex flex-col items-center">
                    <div className="w-0.5 h-4 bg-slate-700"></div>
                    <div className="w-2 h-2 border-r-2 border-b-2 border-slate-600 rotate-45 -mt-1"></div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Dependency Rule */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
          <span>📐</span> Regra de Dependência
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-green-500/5 border border-green-500/20">
            <p className="text-green-400 font-medium mb-2">✅ Permitido</p>
            <ul className="text-sm text-slate-300 space-y-1">
              <li>• Presentation → Application</li>
              <li>• Application → Domain</li>
              <li>• Infrastructure → Domain (implements ports)</li>
            </ul>
          </div>
          <div className="p-4 rounded-xl bg-red-500/5 border border-red-500/20">
            <p className="text-red-400 font-medium mb-2">❌ Proibido</p>
            <ul className="text-sm text-slate-300 space-y-1">
              <li>• Domain → Infrastructure</li>
              <li>• Domain → Application</li>
              <li>• Domain → Presentation</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Async Flow */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>🔄</span> Fluxo Async Completo
        </h3>
        <div className="flex flex-wrap items-center justify-center gap-2 text-sm">
          <span className="px-3 py-2 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400">HTTP Request</span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-2 rounded-lg bg-orange-500/10 border border-orange-500/30 text-orange-400">Granian</span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">uvloop</span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-2 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400">FastAPI</span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-2 rounded-lg bg-green-500/10 border border-green-500/30 text-green-400">TaskService</span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">Queuefy</span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-2 rounded-lg bg-purple-500/10 border border-purple-500/30 text-purple-400">Worker</span>
          <span className="text-slate-600">→</span>
          <span className="px-3 py-2 rounded-lg bg-pink-500/10 border border-pink-500/30 text-pink-400">Response</span>
        </div>
      </div>
    </div>
  );
}
