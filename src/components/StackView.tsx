import { type StackItem } from '../types';

const stackItems: StackItem[] = [
  {
    name: 'FastAPI',
    role: 'Framework HTTP Async',
    icon: '⚡',
    color: 'from-blue-500 to-cyan-500',
    description: 'Framework web moderno e ultra-rápido para APIs com Python 3.7+, baseado em type hints e Starlette.',
    features: ['Async/await nativo', 'OpenAPI automático', 'Dependency injection', 'Pydantic v2', 'Starlette ASGI'],
  },
  {
    name: 'uvloop',
    role: 'Event Loop Ultra-Rápido',
    icon: '🔄',
    color: 'from-cyan-500 to-teal-500',
    description: 'Implementação do asyncio baseada em libuv (a mesma do Node.js). 2-4x mais rápido que o loop padrão.',
    features: ['Drop-in replacement', 'Baseado em libuv', '2-4x mais rápido', 'Auto-detectado pelo Granian', 'Zero config'],
  },
  {
    name: 'Granian',
    role: 'Servidor ASGI em Rust',
    icon: '🦀',
    color: 'from-orange-500 to-red-500',
    description: 'Servidor HTTP de alta performance escrito em Rust. Suporta ASGI, WSGI, HTTP/1, HTTP/2 e WebSocket.',
    features: ['Escrito em Rust', 'HTTP/2 nativo', 'WebSocket support', 'Multi-worker', 'Graceful reload'],
  },
  {
    name: 'Queuefy',
    role: 'Fila de Tarefas Async',
    icon: '📊',
    color: 'from-emerald-500 to-green-500',
    description: 'Task queue e scheduler 100% async. Sem broker, sem processo separado. Pure asyncio com SQLAlchemy ou Redis.',
    features: ['Zero dependencies (core)', 'Cron scheduling', 'Retry policies', 'Named queues', 'Multi-worker safe'],
  },
  {
    name: 'Prefect',
    role: 'Orquestração de Workflows',
    icon: '🔮',
    color: 'from-purple-500 to-pink-500',
    description: 'Plataforma de orquestração de workflows. Define flows e tasks com decorators, retry automático e monitoring.',
    features: ['@flow e @task decorators', 'Retry automático', 'Dashboard visual', 'Cron triggers', 'Hybrid execution'],
  },
  {
    name: 'NiceGUI',
    role: 'UI Interativa',
    icon: '🎨',
    color: 'from-pink-500 to-rose-500',
    description: 'Framework UI baseado em FastAPI e Vue.js. Permite criar interfaces web interativas direto do Python.',
    features: ['Montado no FastAPI', 'Vue.js internamente', 'WebSocket real-time', 'Dark mode', 'Charts & tables'],
  },
  {
    name: 'SQLAlchemy 2',
    role: 'ORM Async',
    icon: '🗄️',
    color: 'from-red-500 to-orange-500',
    description: 'ORM Python com suporte completo a async/await. Mapeamento declarativo e query builder poderoso.',
    features: ['Async sessions', 'Mapped columns', 'Async engine', 'Connection pooling', 'Migration (Alembic)'],
  },
  {
    name: 'structlog',
    role: 'Logging Estruturado',
    icon: '📝',
    color: 'from-indigo-500 to-blue-500',
    description: 'Logging estruturado para Python. Suporte a async, context binding e output em JSON.',
    features: ['Async logging', 'JSON output', 'Context binding', 'Processor chain', 'stdlib compatible'],
  },
];

export default function StackView() {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold gradient-text mb-2">Stack Tecnológica</h2>
        <p className="text-slate-400">Todas as ferramentas utilizadas nesta POC</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-card p-4 text-center glow-blue">
          <div className="text-3xl mb-2">🐍</div>
          <div className="text-2xl font-bold text-blue-400">3.11+</div>
          <div className="text-xs text-slate-400">Python</div>
        </div>
        <div className="glass-card p-4 text-center glow-green">
          <div className="text-3xl mb-2">⚡</div>
          <div className="text-2xl font-bold text-green-400">100%</div>
          <div className="text-xs text-slate-400">Async</div>
        </div>
        <div className="glass-card p-4 text-center glow-purple">
          <div className="text-3xl mb-2">📦</div>
          <div className="text-2xl font-bold text-purple-400">8</div>
          <div className="text-xs text-slate-400">Pacotes</div>
        </div>
        <div className="glass-card p-4 text-center glow-orange">
          <div className="text-3xl mb-2">🏗️</div>
          <div className="text-2xl font-bold text-orange-400">4</div>
          <div className="text-xs text-slate-400">Camadas</div>
        </div>
      </div>

      {/* Stack grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {stackItems.map((item, idx) => (
          <div
            key={item.name}
            className="layer-card glass-card p-6 animate-slide-in"
            style={{ animationDelay: `${idx * 80}ms` }}
          >
            <div className="flex items-start gap-4">
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${item.color} flex items-center justify-center text-2xl shrink-0 shadow-lg`}>
                {item.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-bold text-lg">{item.name}</h3>
                </div>
                <p className="text-sm text-slate-400 mb-1">{item.role}</p>
                <p className="text-sm text-slate-300 mb-3">{item.description}</p>
                <div className="flex flex-wrap gap-1.5">
                  {item.features.map((feat) => (
                    <span
                      key={feat}
                      className="text-xs px-2 py-0.5 rounded-md bg-slate-700/50 border border-slate-600/30 text-slate-400"
                    >
                      {feat}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Install command */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
          <span>📥</span> Instalação
        </h3>
        <div className="code-block">
          <code className="text-green-400">
            <span className="text-slate-500"># Clone e instale</span>{'\n'}
            <span className="text-slate-300">cd backend</span>{'\n'}
            <span className="text-slate-300">pip install -e ".[dev]"</span>{'\n\n'}
            <span className="text-slate-500"># Execute com Granian (produção)</span>{'\n'}
            <span className="text-cyan-400">granian</span>
            <span className="text-slate-300"> --interface asgi --config granian.toml app.main:app</span>{'\n\n'}
            <span className="text-slate-500"># Ou com uvicorn (desenvolvimento)</span>{'\n'}
            <span className="text-cyan-400">python</span>
            <span className="text-slate-300"> -m app.main</span>
          </code>
        </div>
      </div>
    </div>
  );
}
