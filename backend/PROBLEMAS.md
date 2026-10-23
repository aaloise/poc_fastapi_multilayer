# 🐛 Problemas Comuns e Soluções

## ModuleNotFoundError: No module named 'app'

**Causa:** Dependências não instaladas.

**Solução:**
```bash
uv sync
```

## Port 8000 already in use

**Causa:** Outro processo usando a porta.

**Solução Windows:**
```powershell
# Encontrar processo
netstat -ano | findstr :8000

# Matar processo (substitua <PID>)
taskkill /PID <PID> /F
```

**Solução Linux/Mac:**
```bash
# Encontrar e matar processo
lsof -ti:8000 | xargs kill -9
```

**Alternativa:** Usar outra porta
```bash
POC_PORT=8001 uv run python -m app.main
```

## uvloop does not support Windows

**Causa:** uvloop não funciona no Windows.

**Solução:** Nada! O código detecta automaticamente e usa asyncio. Funciona perfeitamente, só é um pouco mais lento.

**Verificar:**
```bash
curl http://localhost:8000/api/v1/health
```

Deve mostrar `"uvloop": false` no Windows.

## Dashboard não carrega (404)

**Causa:** Servidor não está rodando ou rota errada.

**Solução:**
1. Verifique se servidor está rodando
2. Acesse URL correta: http://localhost:8000/ui/
3. Verifique logs do servidor

**Testar:**
```bash
curl http://localhost:8000/api/v1/health
```

## Task não processa (status fica pending)

**Causa:** Worker não está rodando ou erro no handler.

**Solução:**
1. Verifique logs do servidor (deve mostrar `queuefy.started`)
2. Verifique se task foi enfileirada (deve mostrar `queuefy.enqueued`)
3. Verifique se há erro no handler

**Verificar no banco:**
```bash
sqlite3 dev_poc.db
SELECT * FROM tasks WHERE id = 'seu-task-id';
```

## Banco de dados não existe

**Causa:** seed_data.py não foi executado.

**Solução:**
```bash
uv run python scripts/seed_data.py
```

## Dependências conflitantes

**Causa:** Ambiente virtual corrompido.

**Solução:**
```bash
# Windows PowerShell
Remove-Item -Recurse -Force .venv
uv sync

# Linux/Mac
rm -rf .venv
uv sync
```

## NiceGUI não inicia

**Causa:** Erro de configuração.

**Solução:**
1. Verifique se está usando `main.py` (não `main_with_ui.py`)
2. Verifique logs de erro
3. Reinstale dependências: `uv sync`

## Testes falham

**Causa:** Servidor não está rodando.

**Solução:**
```bash
# Terminal 1: Iniciar servidor
uv run python -m app.main

# Terminal 2: Executar testes
uv run python scripts/test_interactive.py
```

## Performance lenta

**Causa:** Windows (sem uvloop) ou muitos dados.

**Solução:**
- Use Linux/Mac para máxima performance
- Limite dados: `GET /api/v1/tasks?limit=10`
- Execute benchmark: `uv run python scripts/benchmark.py`

## Erro ao conectar ao PostgreSQL

**Causa:** PostgreSQL não está rodando ou credenciais erradas.

**Solução:**
```bash
# Verificar se PostgreSQL está rodando
docker ps | grep postgres

# Iniciar PostgreSQL
docker start poc-postgres

# Verificar credenciais
cat .env | grep DATABASE_URL
```

## Logs não aparecem

**Causa:** Log level muito alto.

**Solução:**
```bash
POC_LOG_LEVEL=DEBUG uv run python -m app.main
```

## Script não encontra módulo

**Causa:** Executando script do diretório errado.

**Solução:**
```bash
# Sempre execute do diretório backend
cd backend
uv run python scripts/seed_data.py
```

## Erro de permissão

**Causa:** Scripts sem permissão de execução.

**Solução Linux/Mac:**
```bash
chmod +x scripts/*.py scripts/*.sh
```

## Erro ao importar nicegui

**Causa:** NiceGUI não instalado.

**Solução:**
```bash
uv sync
```

## Erro ao importar prefect

**Causa:** Prefect não instalado ou importação falhando.

**Solução:**
Prefect é opcional. Se não precisar, ignore o erro. O código continua funcionando.

## Banco SQLite bloqueado

**Causa:** Múltiplos processos acessando banco.

**Solução:**
1. Feche todas as instâncias da aplicação
2. Delete banco: `rm dev_poc.db`
3. Execute seed novamente: `uv run python scripts/seed_data.py`

## Websocket não conecta

**Causa:** Firewall ou proxy bloqueando.

**Solução:**
- Verifique firewall
- Use conexão direta (sem proxy)
- Tente outro navegador

## Memória alta

**Causa:** Muitos dados ou memory leak.

**Solução:**
1. Limite dados: `GET /api/v1/tasks?limit=10`
2. Reinicie aplicação
3. Verifique memory leak com profiler

## CPU alta

**Causa:** Worker processando muitas tasks.

**Solução:**
1. Reduza concorrência: `POC_QUEUE_CONCURRENCY=2`
2. Limite tasks pendentes
3. Monitore com `top` ou `htop`

## Ainda com problemas?

1. Verifique logs completos
2. Execute `uv run python scripts/verify_setup.py`
3. Reinstale tudo: `rm -rf .venv && uv sync`
4. Consulte documentação em `docs/`
5. Abra uma issue no repositório
