# 🐛 Auditoria de Código - Relatório de Erros Corrigidos

## Data: 2026-01-15

---

## ✅ Erros Encontrados e Corrigidos

### 1. ❌ `datetime.utcnow()` Deprecated

**Problema:** `datetime.utcnow()` está deprecated no Python 3.12+

**Arquivos afetados:**
- `src/app/models.py` (2 ocorrências)
- `src/app/services.py` (2 ocorrências)
- `src/app/routes.py` (1 ocorrência)
- `src/app/ui.py` (1 ocorrência)
- `src/app/flows.py` (1 ocorrência)
- `src/app/queue.py` (1 ocorrência - docstring)
- `scripts/seed_data.py` (3 ocorrências)
- `scripts/test_dashboard.py` (2 ocorrências)

**Solução:** Substituído por `datetime.now(timezone.utc)`

**Exemplo:**
```python
# ❌ Antes (deprecated)
from datetime import datetime
created_at = datetime.utcnow()

# ✅ Depois (correto)
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
```

---

### 2. ❌ Ordem Incorreta de Rotas no FastAPI

**Problema:** Rota `/tasks/stats` estava DEPOIS de `/tasks/{task_id}`, causando conflito

**Arquivo afetado:** `src/app/routes.py`

**Solução:** Movido `/tasks/stats` para ANTES de `/tasks/{task_id}`

**Exemplo:**
```python
# ❌ Antes (errado)
@router.get("/tasks/{task_id}")  # FastAPI interpreta "stats" como task_id
@router.get("/tasks/stats")      # Nunca é alcançado

# ✅ Depois (correto)
@router.get("/tasks/stats")      # Rota específica primeiro
@router.get("/tasks/{task_id}")  # Rota genérica depois
```

---

### 3. ❌ Bug em `save_task()` no models.py

**Problema:** Expressão condicional incorreta na linha 178

**Arquivo afetado:** `src/app/models.py`

**Código errado:**
```python
await session.refresh(row if existing else row)  # Sempre retorna row!
```

**Solução:**
```python
target = existing if existing else row
await session.refresh(target)
```

---

### 4. ❌ Arquivo Obsoleto `config_dev.py`

**Problema:** Arquivo antigo que não deveria existir

**Arquivo afetado:** `src/app/config_dev.py`

**Solução:** Arquivo deletado

---

### 5. ❌ Configuração Incorreta do Lifespan no NiceGUI

**Problema:** Tentativa de configurar lifespan via `nicegui_app.router.lifespan_context`

**Arquivo afetado:** `src/app/main.py`

**Solução:** Usar `@nicegui_app.on_event("startup")` e `@nicegui_app.on_event("shutdown")`

**Exemplo:**
```python
# ❌ Antes (incorreto)
nicegui_app.router.lifespan_context = lifespan

# ✅ Depois (correto)
@nicegui_app.on_event("startup")
async def startup_event():
    await init_db(settings.db_url)
    ...

@nicegui_app.on_event("shutdown")
async def shutdown_event():
    await stop_queue()
    await close_db()
```

---

### 6. ❌ `get_session()` Async Desnecessário

**Problema:** Função `get_session()` era async mas não fazia nada assíncrono

**Arquivo afetado:** `src/app/database.py`

**Nota:** Isso é um problema menor de performance, mas não foi corrigido nesta auditoria porque requer mudanças em todos os callers.

**Solução futura:** Tornar `get_session()` sync:
```python
# ❌ Atualmente (async desnecessário)
async def get_session() -> AsyncSession:
    return _session_factory()

# ✅ Futuro (sync correto)
def get_session() -> AsyncSession:
    return _session_factory()
```

---

## 📊 Resumo

| Categoria | Quantidade |
|-----------|------------|
| **datetime.utcnow() deprecated** | 13 ocorrências |
| **Ordem de rotas** | 1 problema |
| **Bug lógico** | 1 problema |
| **Arquivo obsoleto** | 1 arquivo |
| **Configuração incorreta** | 1 problema |
| **Total** | 17 problemas |

---

## ✅ Status Final

- ✅ Todos os `datetime.utcnow()` corrigidos
- ✅ Ordem de rotas corrigida
- ✅ Bug em `save_task()` corrigido
- ✅ Arquivo obsoleto deletado
- ✅ Configuração do lifespan corrigida
- ✅ Build passando sem erros
- ✅ Sem código deprecated

---

## 🎯 Recomendações Futuras

1. **Tornar `get_session()` sync** - Melhora performance
2. **Adicionar type hints mais rigorosos** - Usa mypy strict
3. **Adicionar testes de integração** - Cobre mais cenários
4. **Implementar logging estruturado** - Usa structlog consistentemente
5. **Adicionar rate limiting** - Protege contra abuso
6. **Implementar cache** - Melhora performance de leituras frequentes

---

## 📚 Referências

- [Python 3.12 Release Notes - Deprecations](https://docs.python.org/3.12/whatsnew/3.12.html#deprecated)
- [FastAPI Path Parameters Order](https://fastapi.tiangolo.com/tutorial/path-params/#order-matters)
- [SQLAlchemy Async Session](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [NiceGUI Events](https://nicegui.io/documentation/page#events)

---

**Auditoria concluída com sucesso! ✅**
