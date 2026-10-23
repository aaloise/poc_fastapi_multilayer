# 🚀 Modos de Execução

A POC pode ser executada em **2 modos diferentes**:

## 1️⃣ API Pura (Recomendado para desenvolvimento)

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

**Use quando:**
- Desenvolvendo a API
- Testes automatizados
- Integração com frontend externo
- Produção (API apenas)

---

## 2️⃣ API + Dashboard NiceGUI

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

**Use quando:**
- Demonstração visual
- Debug da UI
- Testes manuais
- Desenvolvimento full-stack

---

## 📊 Comparação

| Aspecto | main.py | main_with_ui.py |
|---------|---------|-----------------|
| **Dashboard** | ❌ Não | ✅ Sim (NiceGUI) |
| **API** | ✅ Sim | ✅ Sim |
| **Queuefy** | ✅ Sim | ✅ Sim |
| **Performance** | ⚡ Máxima | ⚡ Boa |
| **Memory** | 💚 Menor | 💛 Maior |
| **Use para** | Dev/Prod | Demo/Debug |

---

## 🎯 Qual usar?

| Cenário | Use |
|---------|-----|
| Desenvolvimento da API | `main.py` |
| Testes automatizados | `main.py` |
| Usar Dashboard React | `main.py` |
| Demonstração visual | `main_with_ui.py` |
| Debug da UI Python | `main_with_ui.py` |
| Produção (API) | `main.py` |
| Produção (com UI) | `main_with_ui.py` |

---

## 🔄 Executando ambos simultaneamente

Você pode executar os dois modos em portas diferentes:

```bash
# Terminal 1: API pura na porta 8000
uv run python -m app.main

# Terminal 2: API + NiceGUI na porta 8001
POC_PORT=8001 uv run python -m app.main_with_ui
```

---

## 🧪 Testando

### Com main.py (API pura)

```bash
# Inicia API
uv run python -m app.main

# Em outro terminal, execute testes
uv run python scripts/test_interactive.py

# Ou use curl
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/tasks
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

Para desenvolvimento diário:
- Use **main.py** para desenvolvimento da API
- Use **main_with_ui.py** quando precisar do dashboard visual

Para produção:
- Use **main.py** para máxima performance
- Use **main_with_ui.py** se precisar do dashboard

---

## 📚 Documentação Relacionada

- [GUIA_RAPIDO.md](GUIA_RAPIDO.md) — Guia rápido
- [COMO_FUNCIONA.md](COMO_FUNCIONA.md) — Como tudo funciona
- [PROBLEMAS.md](PROBLEMAS.md) — Solução de problemas
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — Arquitetura
