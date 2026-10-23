# 🧪 Scripts de Teste e Automação

Este diretório contém scripts para testar, popular e automatizar tarefas da POC.

## 📋 Scripts Disponíveis

### 🌱 seed_data.py
Popula o banco de dados com tasks de exemplo.

```bash
# Executar
uv run python scripts/seed_data.py

# Com ambiente específico
POC_ENV=production uv run python scripts/seed_data.py
```

**O que faz:**
- Cria 10 tasks em diferentes estados (pending, running, completed, failed)
- Simula timestamps realistas
- Mostra resumo visual com Rich

---

### 🧪 test_interactive.py
Executa testes interativos completos da POC.

```bash
# Executar
uv run python scripts/test_interactive.py
```

**O que testa:**
1. ✅ Health Check
2. ✅ Create Task
3. ✅ Create Multiple Tasks
4. ✅ List Tasks
5. ✅ Get Task by ID
6. ✅ Get Stats
7. ✅ Queuefy Integration
8. ✅ Prefect Flow
9. ✅ NiceGUI UI
10. ✅ Error Handling

**Requisito:** API deve estar rodando em `http://localhost:8000`

---

### ⚡ benchmark.py
Mede performance da API em diferentes operações.

```bash
# Executar (10 requests por teste)
uv run python scripts/benchmark.py

# Com mais requests
uv run python scripts/benchmark.py --requests 50
```

**O que mede:**
- Latência (min, max, mean, median, P95, P99)
- Throughput (requests/s)
- Performance de diferentes endpoints

**Requisito:** API deve estar rodando em `http://localhost:8000`

---

### 🛠️ dev.py
Script multifuncional para desenvolvimento.

```bash
# Inicia API em modo dev
uv run python scripts/dev.py start

# Popula banco
uv run python scripts/dev.py seed

# Executa testes
uv run python scripts/dev.py test

# Benchmark
uv run python scripts/dev.py benchmark

# Reseta banco
uv run python scripts/dev.py reset

# Mostra logs
uv run python scripts/dev.py logs

# Shell Python
uv run python scripts/dev.py shell
```

---

### 🎨 test_dashboard.py
Dashboard interativo no NiceGUI para executar testes.

**Acesso:** http://localhost:8000/ui/tests

**Requisito:** API deve estar rodando

**Features:**
- Botões para executar testes individuais
- Logs em tempo real
- Tabela de resumo

---

## 🚀 Workflow Recomendado

### 1. Primeiro Uso

```bash
# Instala dependências
uv sync

# Popula banco com dados de exemplo
uv run python scripts/seed_data.py

# Inicia API
uv run python -m app.main
```

### 2. Testando

```bash
# Em outro terminal, execute testes
uv run python scripts/test_interactive.py
```

### 3. Benchmark

```bash
# Mede performance
uv run python scripts/benchmark.py
```

### 4. Desenvolvimento Diário

```bash
# Usa o script dev.py
uv run python scripts/dev.py start    # Inicia API
uv run python scripts/dev.py seed     # Popula banco
uv run python scripts/dev.py test     # Testa
uv run python scripts/dev.py reset    # Reseta
```

---

## 🐛 Troubleshooting

### ModuleNotFoundError: No module named 'app'

**Causa:** O Python não consegue encontrar o módulo `app` porque ele está em `backend/src/app/`.

**Solução:** Os scripts já incluem o path correto automaticamente. Se ainda ocorrer:

```bash
# Execute do diretório backend
cd backend
uv run python scripts/seed_data.py
```

### API não está rodando

**Erro:** `ConnectionRefusedError` ou `httpx.ConnectError`

**Solução:**
```bash
# Inicia a API primeiro
uv run python -m app.main

# Depois execute os testes
uv run python scripts/test_interactive.py
```

### Banco não existe

**Erro:** `sqlite3.OperationalError: no such table`

**Solução:**
```bash
# Popula o banco
uv run python scripts/seed_data.py
```

---

## 📊 Comparação de Scripts

| Script | Função | Requer API | Tempo |
|--------|--------|------------|-------|
| `seed_data.py` | Popula banco | ❌ | ~2s |
| `test_interactive.py` | Testa tudo | ✅ | ~5s |
| `benchmark.py` | Mede performance | ✅ | ~10s |
| `dev.py` | Multifuncional | Varia | Varia |

---

## 💡 Dicas

### Use o dev.py para tudo

O `dev.py` é o script mais completo e fácil de usar:

```bash
# Em vez de:
uv run python scripts/seed_data.py

# Use:
uv run python scripts/dev.py seed
```

### Combine scripts

```bash
# Reset + Seed + Test
uv run python scripts/dev.py reset
uv run python scripts/dev.py seed
uv run python scripts/dev.py test
```

### Alias úteis (Linux/macOS)

Adicione ao seu `.bashrc` ou `.zshrc`:

```bash
alias poc-seed='cd ~/path/to/backend && uv run python scripts/dev.py seed'
alias poc-test='cd ~/path/to/backend && uv run python scripts/dev.py test'
alias poc-start='cd ~/path/to/backend && uv run python scripts/dev.py start'
```

### PowerShell (Windows)

Crie um profile:

```powershell
# Abra o profile
notepad $PROFILE

# Adicione funções
function Poc-Seed { Set-Location ~\path\to\backend; uv run python scripts/dev.py seed }
function Poc-Test { Set-Location ~\path\to\backend; uv run python scripts/dev.py test }
function Poc-Start { Set-Location ~\path\to\backend; uv run python scripts/dev.py start }
```

---

## 📚 Documentação Relacionada

- [Guia de Testes Completo](../docs/TESTING_GUIDE.md)
- [Guia Rápido](../QUICKSTART.md)
- [Documentação Principal](../README.md)

---

## 🎯 Próximos Passos

1. ✅ Execute `seed_data.py` para popular o banco
2. ✅ Inicie a API com `dev.py start`
3. ✅ Execute `test_interactive.py` para testar tudo
4. ✅ Execute `benchmark.py` para medir performance
5. ✅ Acesse o dashboard em http://localhost:8000/ui/tests

---

**Divirta-se testando!** 🎉
