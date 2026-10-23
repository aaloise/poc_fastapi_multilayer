# 🚀 Guia Rápido de Execução

## Passo a Passo

### 1. Instalar dependências

```bash
cd backend
uv sync
```

### 2. Popular banco de dados

```bash
uv run python scripts/seed_data.py
```

Isso cria 10 tasks de exemplo no banco SQLite.

### 3. Iniciar aplicação

```bash
uv run python -m app.main
```

Você verá:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     database.ready url=sqlite+aiosqlite:///./dev_poc.db
INFO:     queuefy.started concurrency=4
INFO:     queue.ready
INFO:     nicegui.pages.registered prefix=/ui
INFO:     started host=127.0.0.1 port=8000
```

### 4. Acessar

Abra no navegador:
- **Dashboard**: http://localhost:8000/ui/
- **API**: http://localhost:8000/api/v1/tasks
- **Docs**: http://localhost:8000/docs

### 5. Testar (em outro terminal)

```bash
# Testes interativos
uv run python scripts/test_interactive.py

# Benchmark de performance
uv run python scripts/benchmark.py
```

## ✅ Checklist

- [ ] `uv sync` executou sem erros
- [ ] `seed_data.py` criou tasks (mostra "10 tasks criadas")
- [ ] `app.main` iniciou sem erros
- [ ] http://localhost:8000/ui/ abre o dashboard
- [ ] http://localhost:8000/docs mostra Swagger UI

## 🎯 O que cada coisa faz

### Dashboard (/ui/)
- Visualiza tasks em tempo real
- Cria novas tasks
- Mostra estatísticas
- Interface interativa

### API (/api/v1/)
- `POST /tasks` - Criar task
- `GET /tasks` - Listar tasks
- `GET /tasks/{id}` - Buscar task
- `GET /tasks/stats` - Estatísticas
- `GET /health` - Health check

### Queuefy
- Processa tasks em background
- Worker roda automaticamente
- Retry automático em falhas
- Cron jobs agendados

## 📊 Verificando se funciona

### 1. Health check

```bash
curl http://localhost:8000/api/v1/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "components": {
    "fastapi": true,
    "database": true,
    "queuefy": true,
    "prefect": true,
    "nicegui": true,
    "uvloop": false
  }
}
```

### 2. Listar tasks

```bash
curl http://localhost:8000/api/v1/tasks
```

Deve retornar lista de tasks (as 10 que o seed criou).

### 3. Criar task

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"name": "test_task", "payload": {"foo": "bar"}}'
```

### 4. Verificar processamento

Aguarde 2 segundos e verifique:

```bash
curl http://localhost:8000/api/v1/tasks/{task_id}
```

O status deve mudar de `pending` para `completed`.

## 🐛 Problemas Comuns

### "ModuleNotFoundError: No module named 'app'"

```bash
uv sync
```

### "Port 8000 already in use"

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### "uvloop does not support Windows"

Isso é normal! No Windows usa asyncio automaticamente. Funciona perfeitamente.

### Dashboard não carrega

Verifique se o servidor está rodando:
```bash
curl http://localhost:8000/api/v1/health
```

Se não responder, reinicie:
```bash
uv run python -m app.main
```

## 🎓 Próximos Passos

1. ✅ Execute os passos acima
2. ✅ Teste o dashboard em /ui/
3. ✅ Execute `test_interactive.py`
4. ✅ Execute `benchmark.py`
5. ✅ Leia `docs/ARCHITECTURE.md` para entender a arquitetura
6. ✅ Leia `docs/QUEUEFY.md` para entender o Queuefy

## 📚 Documentação Completa

- `docs/ARCHITECTURE.md` - Arquitetura em camadas
- `docs/QUEUEFY.md` - Como Queuefy funciona
- `docs/DATABASE.md` - Modelo de banco de dados
- `docs/FASTAPI.md` - FastAPI completo
- `docs/NICEGUI.md` - NiceGUI completo
- `docs/TESTING_GUIDE.md` - Guia de testes
- `docs/DEPLOYMENT.md` - Como fazer deploy

## 💡 Dicas

- Use o dashboard para visualizar tasks em tempo real
- Execute `test_interactive.py` para testar tudo automaticamente
- Execute `benchmark.py` para medir performance
- Leia os logs no terminal para ver o que está acontecendo
- Use `/docs` para testar a API interativamente

## 🎉 Pronto!

Você tem uma POC completa funcionando com:
- API REST (FastAPI)
- Dashboard visual (NiceGUI)
- Task queue (Queuefy)
- Banco de dados (SQLite)
- Testes automatizados
- Benchmark de performance

Agora é só explorar e modificar! 🚀
