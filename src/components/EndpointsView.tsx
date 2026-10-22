import { type Endpoint } from '../types';

const endpoints: Endpoint[] = [
  { method: 'POST', path: '/api/v1/tasks', description: 'Criar nova task e enfileirar no Queuefy', layer: 'Presentation' },
  { method: 'GET', path: '/api/v1/tasks', description: 'Listar tasks (com filtro por status)', layer: 'Presentation' },
  { method: 'GET', path: '/api/v1/tasks/{task_id}', description: 'Obter task por ID', layer: 'Presentation' },
  { method: 'GET', path: '/api/v1/tasks/stats', description: 'Estatísticas de tasks', layer: 'Presentation' },
  { method: 'GET', path: '/api/v1/health', description: 'Health check do sistema', layer: 'Presentation' },
  { method: 'POST', path: '/api/v1/flows/data-pipeline', description: 'Executar pipeline Prefect (ETL)', layer: 'Presentation' },
  { method: 'POST', path: '/api/v1/flows/batch', description: 'Processar batch de tasks', layer: 'Presentation' },
  { method: 'GET', path: '/ui/', description: 'NiceGUI Dashboard principal', layer: 'NiceGUI' },
  { method: 'GET', path: '/ui/architecture', description: 'NiceGUI — Visão da arquitetura', layer: 'NiceGUI' },
  { method: 'GET', path: '/ui/monitor', description: 'NiceGUI — Monitor em tempo real', layer: 'NiceGUI' },
  { method: 'GET', path: '/docs', description: 'Swagger UI (auto-gerado)', layer: 'FastAPI' },
  { method: 'GET', path: '/redoc', description: 'ReDoc docs (auto-gerado)', layer: 'FastAPI' },
];

const methodColors: Record<string, string> = {
  GET: 'bg-green-500/20 text-green-400 border-green-500/30',
  POST: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  PUT: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  DELETE: 'bg-red-500/20 text-red-400 border-red-500/30',
};

export default function EndpointsView() {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold gradient-text mb-2">Endpoints & Rotas</h2>
        <p className="text-slate-400">API REST + NiceGUI pages + documentação automática</p>
      </div>

      {/* API Endpoints */}
      <div className="glass-card overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700/50 bg-slate-800/30">
          <h3 className="font-bold text-lg flex items-center gap-2">
            <span>🔌</span> API REST (FastAPI)
          </h3>
          <p className="text-sm text-slate-400 mt-1">Endpoints HTTP para integração externa</p>
        </div>

        <div className="divide-y divide-slate-700/30">
          {endpoints.filter(e => e.layer !== 'NiceGUI').map((ep, idx) => (
            <div
              key={ep.path}
              className="flex items-center gap-4 px-6 py-4 hover:bg-slate-800/30 transition-colors animate-slide-in"
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              <span className={`text-xs font-bold px-2.5 py-1 rounded-md border ${methodColors[ep.method]} min-w-[60px] text-center`}>
                {ep.method}
              </span>
              <code className="text-sm text-slate-200 font-mono flex-1">{ep.path}</code>
              <span className="text-sm text-slate-400 hidden md:block">{ep.description}</span>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-700/50 text-slate-400 hidden lg:block">{ep.layer}</span>
            </div>
          ))}
        </div>
      </div>

      {/* NiceGUI Pages */}
      <div className="glass-card overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700/50 bg-slate-800/30">
          <h3 className="font-bold text-lg flex items-center gap-2">
            <span>🎨</span> NiceGUI Pages
          </h3>
          <p className="text-sm text-slate-400 mt-1">Páginas interativas montadas diretamente no FastAPI</p>
        </div>

        <div className="divide-y divide-slate-700/30">
          {endpoints.filter(e => e.layer === 'NiceGUI').map((ep, idx) => (
            <div
              key={ep.path}
              className="flex items-center gap-4 px-6 py-4 hover:bg-slate-800/30 transition-colors animate-slide-in"
              style={{ animationDelay: `${idx * 50}ms` }}
            >
              <span className={`text-xs font-bold px-2.5 py-1 rounded-md border ${methodColors[ep.method]} min-w-[60px] text-center`}>
                {ep.method}
              </span>
              <code className="text-sm text-slate-200 font-mono flex-1">{ep.path}</code>
              <span className="text-sm text-slate-400 hidden md:block">{ep.description}</span>
              <span className="text-xs px-2 py-0.5 rounded bg-pink-500/10 text-pink-400 border border-pink-500/20 hidden lg:block">NiceGUI</span>
            </div>
          ))}
        </div>
      </div>

      {/* Request/Response Examples */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
            <span>📤</span> Request Example
          </h3>
          <div className="code-block">
            <code className="text-sm">
              <span className="text-purple-400">POST</span>
              <span className="text-slate-300"> /api/v1/tasks</span>{'\n\n'}
              <span className="text-slate-500">{'{'}</span>{'\n'}
              <span className="text-slate-300">  </span>
              <span className="text-green-400">"name"</span>
              <span className="text-slate-300">: </span>
              <span className="text-yellow-400">"send_email"</span>
              <span className="text-slate-300">,</span>{'\n'}
              <span className="text-slate-300">  </span>
              <span className="text-green-400">"payload"</span>
              <span className="text-slate-300">: {'{'}</span>{'\n'}
              <span className="text-slate-300">    </span>
              <span className="text-green-400">"to"</span>
              <span className="text-slate-300">: </span>
              <span className="text-yellow-400">"user@example.com"</span>
              <span className="text-slate-300">,</span>{'\n'}
              <span className="text-slate-300">    </span>
              <span className="text-green-400">"subject"</span>
              <span className="text-slate-300">: </span>
              <span className="text-yellow-400">"Welcome!"</span>{'\n'}
              <span className="text-slate-300">  {'}'}</span>
              <span className="text-slate-300">,</span>{'\n'}
              <span className="text-slate-300">  </span>
              <span className="text-green-400">"priority"</span>
              <span className="text-slate-300">: </span>
              <span className="text-yellow-400">"high"</span>{'\n'}
              <span className="text-slate-500">{'}'}</span>
            </code>
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
            <span>📥</span> Response Example
          </h3>
          <div className="code-block">
            <code className="text-sm">
              <span className="text-slate-500">{'{'}</span>{'\n'}
              <span className="text-slate-300">  </span>
              <span className="text-green-400">"id"</span>
              <span className="text-slate-300">: </span>
              <span className="text-yellow-400">"a1b2c3d4-..."</span>
              <span className="text-slate-300">,</span>{'\n'}
              <span className="text-slate-300">  </span>
              <span className="text-green-400">"name"</span>
              <span className="text-slate-300">: </span>
              <span className="text-yellow-400">"send_email"</span>
              <span className="text-slate-300">,</span>{'\n'}
              <span className="text-slate-300">  </span>
              <span className="text-green-400">"status"</span>
              <span className="text-slate-300">: </span>
              <span className="text-yellow-400">"pending"</span>
              <span className="text-slate-300">,</span>{'\n'}
              <span className="text-slate-300">  </span>
              <span className="text-green-400">"priority"</span>
              <span className="text-slate-300">: </span>
              <span className="text-yellow-400">"high"</span>
              <span className="text-slate-300">,</span>{'\n'}
              <span className="text-slate-300">  </span>
              <span className="text-green-400">"queue_name"</span>
              <span className="text-slate-300">: </span>
              <span className="text-yellow-400">"default"</span>
              <span className="text-slate-300">,</span>{'\n'}
              <span className="text-slate-300">  </span>
              <span className="text-green-400">"attempts"</span>
              <span className="text-slate-300">: </span>
              <span className="text-cyan-400">0</span>
              <span className="text-slate-300">,</span>{'\n'}
              <span className="text-slate-300">  </span>
              <span className="text-green-400">"created_at"</span>
              <span className="text-slate-300">: </span>
              <span className="text-yellow-400">"2026-01-15T..."</span>{'\n'}
              <span className="text-slate-500">{'}'}</span>
            </code>
          </div>
        </div>
      </div>

      {/* Server info */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>🚀</span> Como Rodar
        </h3>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
            <p className="text-sm font-medium text-orange-400 mb-2">🦀 Granian + uv</p>
            <code className="text-xs text-slate-300 block bg-slate-900/50 p-2 rounded">
              uv sync<br/>
              uv run granian \<br/>
              &nbsp;&nbsp;--interface asgi \<br/>
              &nbsp;&nbsp;app.main:app
            </code>
          </div>
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
            <p className="text-sm font-medium text-blue-400 mb-2">⚡ Dev (uv)</p>
            <code className="text-xs text-slate-300 block bg-slate-900/50 p-2 rounded">
              uv run python \<br/>
              &nbsp;&nbsp;-m app.main
            </code>
          </div>
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
            <p className="text-sm font-medium text-green-400 mb-2">🐳 Docker</p>
            <code className="text-xs text-slate-300 block bg-slate-900/50 p-2 rounded">
              docker-compose up -d
            </code>
          </div>
        </div>
      </div>
    </div>
  );
}
