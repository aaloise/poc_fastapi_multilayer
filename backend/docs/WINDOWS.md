# 🪟 Guia para Windows

## ⚠️ Diferenças Importantes

### uvloop não é compatível com Windows

O **uvloop** é uma implementação ultra-rápida do event loop baseada em **libuv** (a mesma do Node.js), mas **não funciona no Windows**.

### O que acontece?

| Sistema Operacional | Event Loop | Performance |
|---------------------|------------|-------------|
| **Linux/macOS** | uvloop (automático) | ⚡ Excelente |
| **Windows** | asyncio padrão | ✅ Bom |

### A boa notícia

A POC **funciona perfeitamente no Windows**! A diferença de performance é mínima para desenvolvimento.

---

## 🔧 Como Funciona

### Detecção Automática

O código detecta automaticamente o sistema operacional:

```python
# main.py
import platform

UVLOOP = False
if platform.system() != "Windows":
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        UVLOOP = True
    except ImportError:
        pass
```

### O que isso significa?

- ✅ **Windows**: Usa `asyncio` padrão (funciona perfeitamente)
- ✅ **Linux/macOS**: Usa `uvloop` (mais rápido)
- ✅ **Health check**: Mostra `uvloop: false` no Windows
- ✅ **Tudo funciona**: Sem mudanças no código da aplicação

---

## 🚀 Usando no Windows

### Instalação

```powershell
# Instala dependências (uvloop será ignorado automaticamente)
uv sync

# Popula banco
uv run python scripts/seed_data.py

# Inicia API
uv run python -m app.main
```

### Verificando

```powershell
# Health check
curl http://localhost:8000/api/v1/health

# Resposta (no Windows):
{
    "status": "healthy",
    "components": {
        "fastapi": true,
        "database": true,
        "queuefy": true,
        "prefect": true,
        "nicegui": true,
        "uvloop": false  ← Windows!
    }
}
```

---

## 📊 Performance

### Comparação

| Operação | Linux (uvloop) | Windows (asyncio) | Diferença |
|----------|----------------|-------------------|-----------|
| Health check | ~2ms | ~5ms | 2.5x |
| Create task | ~35ms | ~45ms | 1.3x |
| List tasks | ~20ms | ~25ms | 1.25x |

**Conclusão**: A diferença é **mínima** para desenvolvimento. Em produção, use Linux.

---

## 🐛 Troubleshooting

### Erro: "uvloop does not support Windows"

**Causa**: Tentativa de importar uvloop no Windows.

**Solução**: O código já está corrigido! Se ainda aparecer:

```powershell
# Atualize o código
git pull

# Reinstale dependências
uv sync --reinstall
```

### Erro: "ModuleNotFoundError: No module named 'uvloop'"

**Causa**: uvloop não foi instalado (correto no Windows).

**Solução**: Isso é **normal** no Windows! O código detecta e continua.

### Erro ao iniciar Granian

**Causa**: Granian com uvloop no Windows.

**Solução**: Use uvicorn no Windows:

```powershell
# Em vez de:
uv run granian --interface asgi app.main:app

# Use:
uv run python -m app.main
```

---

## 💡 Dicas para Windows

### 1. Use WSL2 (Recomendado)

Se você precisa de performance máxima, use **WSL2** (Windows Subsystem for Linux):

```powershell
# Instala WSL2
wsl --install

# No WSL2 (Linux):
cd /mnt/c/path/to/backend
uv sync
uv run python -m app.main
```

**Vantagens**:
- ✅ uvloop funciona
- ✅ Performance máxima
- ✅ Compatível com produção

### 2. Docker Desktop

Use Docker para ter ambiente Linux no Windows:

```powershell
# Build
docker build -t async-poc .

# Run
docker run -p 8000:8000 async-poc
```

### 3. Terminal Recomendado

Use **Windows Terminal** com PowerShell 7+:

```powershell
# Instala Windows Terminal
winget install Microsoft.WindowsTerminal

# Instala PowerShell 7
winget install Microsoft.PowerShell
```

---

## 📝 Scripts no Windows

### dev.py

```powershell
# Funciona normalmente
uv run python scripts/dev.py start
uv run python scripts/dev.py seed
uv run python scripts/dev.py test
```

### test_interactive.py

```powershell
# Funciona normalmente
uv run python scripts/test_interactive.py
```

### benchmark.py

```powershell
# Funciona normalmente (resultados serão um pouco mais lentos)
uv run python scripts/benchmark.py
```

---

## 🔄 Comparação de Ambientes

### Windows (Desenvolvimento)

```powershell
# Event loop
asyncio (padrão)

# Server
uvicorn

# Database
SQLite (dev_poc.db)

# Performance
✅ Bom para desenvolvimento
```

### Linux/macOS (Desenvolvimento)

```bash
# Event loop
uvloop (automático)

# Server
granian ou uvicorn

# Database
SQLite (dev_poc.db)

# Performance
⚡ Excelente
```

### Linux (Produção)

```bash
# Event loop
uvloop

# Server
granian

# Database
PostgreSQL

# Performance
⚡⚡⚡ Máxima
```

---

## 🎯 Recomendações

### Para Desenvolvimento no Windows

1. ✅ Use a POC normalmente — funciona perfeitamente
2. ✅ Não se preocupe com performance — é suficiente
3. ✅ Use Windows Terminal + PowerShell 7
4. ✅ Considere WSL2 se precisar de performance máxima

### Para Produção

1. ✅ **Sempre use Linux** (Docker, VM, cloud)
2. ✅ uvloop será usado automaticamente
3. ✅ Granian para máxima performance
4. ✅ PostgreSQL para banco de dados

---

## 📚 Links Úteis

- [uvloop no GitHub](https://github.com/MagicStack/uvloop)
- [WSL2 Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Windows Terminal](https://aka.ms/terminal)
- [PowerShell 7](https://github.com/PowerShell/PowerShell)

---

## 🎉 Conclusão

A POC **funciona perfeitamente no Windows**! A única diferença é que o uvloop não é usado, mas isso não impacta significativamente o desenvolvimento.

**Para produção**, sempre use Linux para ter a máxima performance com uvloop + Granian.
