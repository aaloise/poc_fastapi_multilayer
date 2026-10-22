export default function QueuefyView() {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold gradient-text mb-2">Como o Queuefy Funciona</h2>
        <p className="text-slate-400">Task queue que usa o próprio banco de dados — sem broker externo</p>
      </div>

      {/* Fluxo visual */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>🔄</span> Fluxo de Execução
        </h3>
        
        <div className="space-y-4">
          {/* Step 1 */}
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-full bg-blue-500/20 border-2 border-blue-500 flex items-center justify-center text-blue-400 font-bold shrink-0">
              1
            </div>
            <div className="flex-1">
              <p className="font-bold text-blue-400 mb-1">API recebe request</p>
              <p className="text-sm text-slate-300">
                <code className="text-green-400">POST /api/v1/tasks</code> → cria task no banco (status: pending)
              </p>
              <div className="code-block mt-2 text-xs">
                <code>
                  <span className="text-slate-500"># services.py</span>{'\n'}
                  <span className="text-blue-400">async def</span> <span className="text-green-400">create_task</span>(name, payload):{'\n'}
                  {'    '}task = Task(name=name, payload=payload){'\n'}
                  {'    '}session = <span className="text-blue-400">await</span> get_session(){'\n'}
                  {'    '}task = <span className="text-blue-400">await</span> save_task(session, task){'\n'}
                  {'    '}<span className="text-blue-400">await</span> enqueue(<span className="text-yellow-400">"process_task"</span>, task_id=task.id){'\n'}
                </code>
              </div>
            </div>
          </div>

          {/* Arrow */}
          <div className="flex justify-center">
            <div className="w-0.5 h-6 bg-gradient-to-b from-blue-500/50 to-purple-500/50"></div>
          </div>

          {/* Step 2 */}
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-full bg-purple-500/20 border-2 border-purple-500 flex items-center justify-center text-purple-400 font-bold shrink-0">
              2
            </div>
            <div className="flex-1">
              <p className="font-bold text-purple-400 mb-1">Queuefy enfileira</p>
              <p className="text-sm text-slate-300">
                Insere linha na tabela <code className="text-yellow-400">queuefy_runs</code> (status: pending)
              </p>
              <div className="code-block mt-2 text-xs">
                <code>
                  <span className="text-slate-500"># queue.py</span>{'\n'}
                  <span className="text-blue-400">async def</span> <span className="text-green-400">enqueue</span>(task_name, task_id, **kwargs):{'\n'}
                  {'    '}<span className="text-slate-500"># Insere no banco (tabela queuefy_runs)</span>{'\n'}
                  {'    '}<span className="text-blue-400">await</span> _queuefy.enqueue(task_name, task_id=task_id, **kwargs){'\n'}
                </code>
              </div>
            </div>
          </div>

          {/* Arrow */}
          <div className="flex justify-center">
            <div className="w-0.5 h-6 bg-gradient-to-b from-purple-500/50 to-green-500/50"></div>
          </div>

          {/* Step 3 */}
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-full bg-green-500/20 border-2 border-green-500 flex items-center justify-center text-green-400 font-bold shrink-0">
              3
            </div>
            <div className="flex-1">
              <p className="font-bold text-green-400 mb-1">Worker processa</p>
              <p className="text-sm text-slate-300">
                Worker em background busca tasks pendentes e executa o handler
              </p>
              <div className="code-block mt-2 text-xs">
                <code>
                  <span className="text-slate-500"># queue.py — handler registrado</span>{'\n'}
                  <span className="text-purple-400">@_queuefy.task</span>(<span className="text-yellow-400">"process_task"</span>, max_attempts=3){'\n'}
                  <span className="text-blue-400">async def</span> <span className="text-green-400">handle_process_task</span>(task_id, payload):{'\n'}
                  {'    '}<span className="text-slate-500"># Executa a lógica de negócio</span>{'\n'}
                  {'    '}result = <span className="text-blue-400">await</span> execute_task(task_id){'\n'}
                  {'    '}<span className="text-blue-400">return</span> result{'\n'}
                </code>
              </div>
            </div>
          </div>

          {/* Arrow */}
          <div className="flex justify-center">
            <div className="w-0.5 h-6 bg-gradient-to-b from-green-500/50 to-pink-500/50"></div>
          </div>

          {/* Step 4 */}
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-full bg-pink-500/20 border-2 border-pink-500 flex items-center justify-center text-pink-400 font-bold shrink-0">
              4
            </div>
            <div className="flex-1">
              <p className="font-bold text-pink-400 mb-1">Atualiza status</p>
              <p className="text-sm text-slate-300">
                Marca como <code className="text-green-400">completed</code> ou <code className="text-red-400">failed</code> no banco
              </p>
              <div className="code-block mt-2 text-xs">
                <code>
                  <span className="text-slate-500"># services.py</span>{'\n'}
                  <span className="text-blue-400">async def</span> <span className="text-green-400">execute_task</span>(task_id):{'\n'}
                  {'    '}task.status = TaskStatus.RUNNING{'\n'}
                  {'    '}<span className="text-blue-400">await</span> save_task(session, task){'\n'}
                  {'    '}<span className="text-slate-500"># ... processa ...</span>{'\n'}
                  {'    '}task.status = TaskStatus.COMPLETED{'\n'}
                  {'    '}<span className="text-blue-400">await</span> save_task(session, task){'\n'}
                </code>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabelas do banco */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>🗄️</span> Tabelas no Banco de Dados
        </h3>

        <div className="space-y-6">
          {/* Tabela tasks */}
          <div>
            <h4 className="font-bold text-blue-400 mb-2 flex items-center gap-2">
              <span>📦</span> tasks (sua aplicação)
            </h4>
            <div className="code-block text-xs">
              <code>
                <span className="text-purple-400">CREATE TABLE</span> <span className="text-green-400">tasks</span> ({'\n'}
                {'  '}id          <span className="text-cyan-400">VARCHAR(36)</span> <span className="text-yellow-400">PRIMARY KEY</span>,{'\n'}
                {'  '}name        <span className="text-cyan-400">VARCHAR(255)</span> <span className="text-yellow-400">NOT NULL</span>,{'\n'}
                {'  '}payload     <span className="text-cyan-400">JSON</span>,{'\n'}
                {'  '}status      <span className="text-cyan-400">VARCHAR(20)</span> <span className="text-yellow-400">DEFAULT</span> <span className="text-green-400">'pending'</span>,{'\n'}
                {'  '}priority    <span className="text-cyan-400">VARCHAR(20)</span> <span className="text-yellow-400">DEFAULT</span> <span className="text-green-400">'medium'</span>,{'\n'}
                {'  '}queue       <span className="text-cyan-400">VARCHAR(100)</span> <span className="text-yellow-400">DEFAULT</span> <span className="text-green-400">'default'</span>,{'\n'}
                {'  '}attempts    <span className="text-cyan-400">INTEGER</span> <span className="text-yellow-400">DEFAULT</span> <span className="text-orange-400">0</span>,{'\n'}
                {'  '}created_at  <span className="text-cyan-400">DATETIME</span>,{'\n'}
                {'  '}started_at  <span className="text-cyan-400">DATETIME</span>,{'\n'}
                {'  '}completed_at <span className="text-cyan-400">DATETIME</span>,{'\n'}
                {'  '}error       <span className="text-cyan-400">VARCHAR(1000)</span>{'\n'}
                );
              </code>
            </div>
          </div>

          {/* Tabela queuefy_runs */}
          <div>
            <h4 className="font-bold text-purple-400 mb-2 flex items-center gap-2">
              <span>📊</span> queuefy_runs (Queuefy)
            </h4>
            <p className="text-sm text-slate-400 mb-2">
              Tabela interna do Queuefy — criada automaticamente
            </p>
            <div className="code-block text-xs">
              <code>
                <span className="text-purple-400">CREATE TABLE</span> <span className="text-green-400">queuefy_runs</span> ({'\n'}
                {'  '}id          <span className="text-cyan-400">VARCHAR(36)</span> <span className="text-yellow-400">PRIMARY KEY</span>,{'\n'}
                {'  '}task_name   <span className="text-cyan-400">VARCHAR(255)</span> <span className="text-yellow-400">NOT NULL</span>,{'\n'}
                {'  '}task_id     <span className="text-cyan-400">VARCHAR(36)</span>,{'\n'}
                {'  '}kwargs      <span className="text-cyan-400">JSON</span>,{'\n'}
                {'  '}status      <span className="text-cyan-400">VARCHAR(20)</span>,{'\n'}
                {'  '}attempts    <span className="text-cyan-400">INTEGER</span>,{'\n'}
                {'  '}created_at  <span className="text-cyan-400">DATETIME</span>,{'\n'}
                {'  '}started_at  <span className="text-cyan-400">DATETIME</span>,{'\n'}
                {'  '}completed_at <span className="text-cyan-400">DATETIME</span>,{'\n'}
                {'  '}error       <span className="text-cyan-400">TEXT</span>{'\n'}
                );
              </code>
            </div>
          </div>

          {/* Tabela queuefy_schedules */}
          <div>
            <h4 className="font-bold text-purple-400 mb-2 flex items-center gap-2">
              <span>⏰</span> queuefy_schedules (Queuefy)
            </h4>
            <p className="text-sm text-slate-400 mb-2">
              Para tasks agendadas com cron — criada automaticamente
            </p>
            <div className="code-block text-xs">
              <code>
                <span className="text-purple-400">CREATE TABLE</span> <span className="text-green-400">queuefy_schedules</span> ({'\n'}
                {'  '}task_name   <span className="text-cyan-400">VARCHAR(255)</span> <span className="text-yellow-400">PRIMARY KEY</span>,{'\n'}
                {'  '}cron        <span className="text-cyan-400">VARCHAR(100)</span>,{'\n'}
                {'  '}next_run    <span className="text-cyan-400">DATETIME</span>,{'\n'}
                {'  '}last_run    <span className="text-cyan-400">DATETIME</span>{'\n'}
                );
              </code>
            </div>
          </div>
        </div>
      </div>

      {/* Exemplos de uso */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>💡</span> Exemplos de Uso
        </h3>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <p className="font-medium text-green-400 mb-2">✅ Task imediata</p>
            <div className="code-block text-xs">
              <code>
                <span className="text-slate-500"># Enfileira para processar agora</span>{'\n'}
                <span className="text-blue-400">await</span> enqueue({'\n'}
                {'    '}<span className="text-yellow-400">"process_task"</span>,{'\n'}
                {'    '}task_id=<span className="text-yellow-400">"123"</span>,{'\n'}
                {'    '}payload={'{'}<span className="text-yellow-400">"foo"</span>: <span className="text-yellow-400">"bar"</span>{'}'}{'\n'}
                )
              </code>
            </div>
          </div>

          <div>
            <p className="font-medium text-blue-400 mb-2">⏰ Task agendada</p>
            <div className="code-block text-xs">
              <code>
                <span className="text-slate-500"># Rodar daqui a 1 hora</span>{'\n'}
                <span className="text-blue-400">await</span> enqueue_at({'\n'}
                {'    '}<span className="text-yellow-400">"send_notification"</span>,{'\n'}
                {'    '}when=datetime.utcnow() + timedelta(hours=1),{'\n'}
                {'    '}message=<span className="text-yellow-400">"Hello!"</span>,{'\n'}
                {'    '}channel=<span className="text-yellow-400">"email"</span>{'\n'}
                )
              </code>
            </div>
          </div>

          <div>
            <p className="font-medium text-purple-400 mb-2">🔄 Cron job</p>
            <div className="code-block text-xs">
              <code>
                <span className="text-slate-500"># Registrado no queue.py</span>{'\n'}
                <span className="text-purple-400">@_queuefy.task</span>({'\n'}
                {'    '}<span className="text-yellow-400">"daily_report"</span>,{'\n'}
                {'    '}cron=<span className="text-yellow-400">"0 4 * * *"</span>  <span className="text-slate-500"># 4h da manhã</span>{'\n'}
                ){'\n'}
                <span className="text-blue-400">async def</span> handle_report():{'\n'}
                {'    '}...
              </code>
            </div>
          </div>

          <div>
            <p className="font-medium text-orange-400 mb-2">🔁 Retry automático</p>
            <div className="code-block text-xs">
              <code>
                <span className="text-slate-500"># Tenta 3 vezes se falhar</span>{'\n'}
                <span className="text-purple-400">@_queuefy.task</span>({'\n'}
                {'    '}<span className="text-yellow-400">"process_task"</span>,{'\n'}
                {'    '}max_attempts=<span className="text-orange-400">3</span>,{'\n'}
                {'    '}timeout=<span className="text-orange-400">60</span>  <span className="text-slate-500"># segundos</span>{'\n'}
                ){'\n'}
                <span className="text-blue-400">async def</span> handle_task(...):{'\n'}
                {'    '}...
              </code>
            </div>
          </div>
        </div>
      </div>

      {/* Vantagens */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>✨</span> Vantagens do Queuefy
        </h3>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-green-500/5 border border-green-500/20">
            <p className="text-green-400 font-medium mb-2">✅ Zero dependências externas</p>
            <p className="text-sm text-slate-300">
              Usa o mesmo banco da aplicação (SQLite/PostgreSQL). 
              Não precisa de Redis, RabbitMQ ou outro broker.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/20">
            <p className="text-blue-400 font-medium mb-2">⚡ 100% Async</p>
            <p className="text-sm text-slate-300">
              Todo o código é async/await. 
              Integra perfeitamente com FastAPI e uvloop.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-purple-500/5 border border-purple-500/20">
            <p className="text-purple-400 font-medium mb-2">🔁 Retry automático</p>
            <p className="text-sm text-slate-300">
              Se uma task falhar, tenta novamente automaticamente 
              (configurável: max_attempts).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-orange-500/5 border border-orange-500/20">
            <p className="text-orange-400 font-medium mb-2">⏰ Cron jobs nativos</p>
            <p className="text-sm text-slate-300">
              Suporta agendamento com expressões cron. 
              Tasks rodam automaticamente no horário configurado.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-pink-500/5 border border-pink-500/20">
            <p className="text-pink-400 font-medium mb-2">👥 Multi-worker safe</p>
            <p className="text-sm text-slate-300">
              Vários workers podem rodar em paralelo sem duplicar tasks. 
              Usa locking no banco para garantir exclusividade.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-cyan-500/5 border border-cyan-500/20">
            <p className="text-cyan-400 font-medium mb-2">🎯 Simples de usar</p>
            <p className="text-sm text-slate-300">
              API minimalista: apenas <code>enqueue()</code> e <code>@task</code>. 
              Sem configuração complexa.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
