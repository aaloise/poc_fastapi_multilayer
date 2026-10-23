# 🔧 Solução de Problemas

## ❌ Erro: ModuleNotFoundError: No module named 'app'

### Causa
O Python não consegue encontrar o módulo `app` porque ele está em `backend/src/app/`, mas você está executando scripts de `backend/scripts/`.

### ✅ Solução

Os scripts já foram corrigidos para adicionar o path automaticamente. Agora você pode executar:

```bash
# Do diretório backend
cd backend

# Executar qualquer script
uv run python scripts/seed_data.py
uv run python scripts/test_interactive.py
uv run python scripts/benchmark.py
uv run python scripts/dev.py start
```

### Se ainda ocorrer o erro

**Opção 1: Use o dev.py (recomendado)**

```bash
uv run python scripts/dev.py seed
```

**Opção 2: Execute com PYTHONPATH**

```bash
# Linux/macOS
PYTHONPATH=src uv run python scripts/seed_data.py

# Windows (PowerShell)
$env:PYTHONPATH="src"; uv run python scripts/seed_data.py

# Windows (CMD)
set PYTHONPATH=src && uv run python scripts/seed_data.py
```

**Opção 3: Instale o pacote em modo de desenvolvimento**

```bash
uv pip install -e .
uv run python scripts/seed_data.py
```

---

## ❌ Erro: ConnectionRefusedError

### Causa
A API não está rodando.

### ✅ Solução

```bash
# Terminal 1: Inicia a API
uv run python -m app.main

# Terminal 2: Executa os testes
uv run python scripts/test_interactive.py
```

---

## ❌ Erro: sqlite3.OperationalError: no such table

### Causa
O banco de dados não foi inicializado ou populado.

### ✅ Solução

```bash
# Popula o banco
uv run python scripts/seed_data.py

# Ou reseta e popula
uv run python scripts/dev.py reset
uv run python scripts/dev.py seed
```

---

## ❌ Erro: uvloop does not support Windows

### Causa
O uvloop não é compatível com Windows.

### ✅ Solução

O código já foi corrigido para detectar automaticamente o sistema operacional. No Windows, usa o `asyncio` padrão.

Se ainda ocorrer:

```bash
# Atualize o código
git pull

# Reinstale dependências
uv sync --reinstall
```

---

## ❌ Erro: Port 8000 already in use

### Causa
Outro processo está usando a porta 8000.

### ✅ Solução

**Opção 1: Mate o processo**

```bash
# Linux/macOS
lsof -ti:8000 | xargs kill -9

# Windows (PowerShell)
Get-NetTCPConnection -LocalPort 8000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

**Opção 2: Use outra porta**

```bash
POC_PORT=8001 uv run python -m app.main
```

---

## ❌ Erro: Permission denied

### Causa
Scripts não têm permissão de execução.

### ✅ Solução

```bash
# Linux/macOS
chmod +x scripts/*.sh
chmod +x scripts/*.py

# Windows
# Não é necessário, execute com uv run
```

---

## ❌ Erro: uv not found

### Causa
O uv não está instalado ou não está no PATH.

### ✅ Solução

```bash
# Instala o uv
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Adicione ao PATH (se necessário)
export PATH="$HOME/.cargo/bin:$PATH"  # Linux/macOS
```

---

## ❌ Erro: Dependencies not installed

### Causa
As dependências não foram instaladas.

### ✅ Solução

```bash
# Instala todas as dependências
uv sync

# Ou reinstala
uv sync --reinstall
```

---

## ❌ Erro: Python version not supported

### Causa
O Python instalado é muito antigo (precisa >= 3.11).

### ✅ Solução

```bash
# Verifica versão
python --version

# Instala Python 3.11+ com uv
uv python install 3.11

# Usa Python específico
uv python pin 3.11
```

---

## 🎯 Workflow Correto

### 1. Instalação Inicial

```bash
cd backend
uv sync
```

### 2. Popula Banco

```bash
uv run python scripts/seed_data.py
```

### 3. Inicia API

```bash
uv run python -m app.main
```

### 4. Testa (em outro terminal)

```bash
uv run python scripts/test_interactive.py
```

---

## 📚 Documentação Relacionada

- [Guia para Windows](docs/WINDOWS.md)
- [Guia de Testes](docs/TESTING_GUIDE.md)
- [Quick Start](QUICKSTART.md)
- [Scripts README](scripts/README.md)

---

## 💡 Dicas Gerais

1. **Sempre execute do diretório `backend`**
   ```bash
   cd backend
   ```

2. **Use `uv run` para executar scripts**
   ```bash
   uv run python scripts/seed_data.py
   ```

3. **Use o dev.py para facilitar**
   ```bash
   uv run python scripts/dev.py seed
   uv run python scripts/dev.py test
   ```

4. **Verifique se a API está rodando antes de testar**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

5. **Leia os logs da API para debugar**
   - A API mostra logs detalhados no console
   - Use `POC_LOG_LEVEL=DEBUG` para mais detalhes

---

## 🆘 Ainda com problemas?

1. Verifique se está no diretório correto: `cd backend`
2. Verifique se as dependências estão instaladas: `uv sync`
3. Verifique se a API está rodando: `curl http://localhost:8000/api/v1/health`
4. Leia a documentação específica do script em `scripts/README.md`
5. Consulte a documentação completa em `docs/`

---

**Precisa de mais ajuda?** Abra uma issue no repositório! 🐛
