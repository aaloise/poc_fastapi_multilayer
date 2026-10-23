# 🚀 Modos de Execução

A POC pode ser executada em **dois modos diferentes**, dependendo do que você precisa:

## 📋 Opções

### 1️⃣ API Pura (main.py)

**Use quando:**
- ✅ Quer apenas a API REST
- ✅ Vai usar o dashboard React (este projeto)
- ✅ Não precisa do dashboard NiceGUI
- ✅ Quer performance máxima

**Como executar:**
```bash
uv run python -m app.main
```

**O que tem:**
- ✅ API REST completa (`/api/v1/*`)
- ✅ Documentação Swagger (`/docs`)
- ✅ Queuefy processando tasks em background
- ❌ Dashboard NiceGUI

**Acesse:**
- API: http://localhost:8000/api/v1/
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

---

### 2️⃣ API + NiceGUI Dashboard (main_with_ui.py)

**Use quando:**
- ✅ Quer o dashboard visual integrado
- ✅ Quer testar a UI interativa
- ✅ Quer ver tudo em um só lugar
- ✅ Está desenvolvendo/debugando

**Como executar:**
```bash
uv run python -m app.main_with_ui
```

**O que tem:**
- ✅ API REST completa (`/api/v1/*`)
- ✅ Documentação Swagger (`/docs`)
- ✅ Dashboard NiceGUI (`/ui/`)
- ✅ Queuefy processando tasks em background

**Acesse:**
- Dashboard: http://localhost:8000/ui/
- API: http://localhost:8000/api/v1/
- Docs: http://localhost:8000/docs

---

## 🎯 Qual usar?

| Cenário | Use |
|---------|-----|
| Desenvolvimento da API | `main.py` |
| Testes automatizados | `main.py` |
| Demonstração visual | `main_with_ui.py` |
| Debug da UI | `main_with_ui.py` |
| Produção (API) | `main.py` |
| Produção (com UI) | `main_with_ui.py` |

---

## 🔄 Alternando entre modos

Você pode executar os dois modos simultaneamente em portas diferentes:

```bash
# Terminal 1: API pura na porta 8000
uv run python -m app.main

# Terminal 2: API + NiceGUI na porta 8001
POC_PORT=8001 uv run python -m app.main_with_ui
```

---

## 📊 Comparação

| Aspecto | main.py | main_with_ui.py |
|---------|---------|-----------------|
| **Performance** | ⚡ Máxima | ⚡ Boa |
| **Memory** | 💚 Menor | 💛 Maior |
| **Startup** | ⚡ Rápido | ⚡ Rápido |
| **Dashboard** | ❌ Não | ✅ Sim |
| **API** | ✅ Sim | ✅ Sim |
| **Queuefy** | ✅ Sim | ✅ Sim |
| **Prefect** | ✅ Sim | ✅ Sim |

---

## 🧪 Testando

### Com main.py (API pura)

```bash
# Inicia API
uv run python -m app.main

# Em outro terminal, execute testes
uv run python scripts/test_interactive.py
```

### Com main_with_ui.py (API + UI)

```bash
# Inicia API + UI
uv run python -m app.main_with_ui

# Acesse no navegador
# http://localhost:8000/ui/

# Ou execute testes
uv run python scripts/test_interactive.py
```

---

## 💡 Dica

Para desenvolvimento, use **main_with_ui.py** para ter o dashboard visual.
Para produção ou testes automatizados, use **main.py** para máxima performance.

---

## 🐛 Troubleshooting

### NiceGUI não carrega

Se o dashboard NiceGUI não aparecer:

1. Verifique se está usando `main_with_ui.py`:
   ```bash
   uv run python -m app.main_with_ui
   ```

2. Acesse a URL correta:
   ```
   http://localhost:8000/ui/
   ```

3. Verifique os logs da API

### API não responde

Se a API não responder:

1. Verifique se está rodando:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. Verifique os logs

3. Reinicie a aplicação

---

## 📚 Documentação Relacionada

- [QUICKSTART.md](QUICKSTART.md) — Guia rápido
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Solução de problemas
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Arquitetura
- [docs/NICEGUI.md](docs/NICEGUI.md) — Documentação do NiceGUI
