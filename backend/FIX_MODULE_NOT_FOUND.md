# ✅ Problema Resolvido: ModuleNotFoundError

## 🔧 O que foi feito

O `pyproject.toml` foi atualizado para incluir a configuração correta do build system:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/app"]
```

Isso diz ao `uv` onde encontrar o pacote `app` (dentro do diretório `src/`).

## 🚀 Como Resolver o Problema

### Passo 1: Limpar o ambiente virtual

```bash
cd backend

# No Windows PowerShell:
Remove-Item -Recurse -Force .venv

# No Linux/macOS:
rm -rf .venv
```

### Passo 2: Reinstalar dependências

```bash
uv sync
```

### Passo 3: Verificar a configuração

```bash
uv run python scripts/verify_setup.py
```

Este script verifica:
- ✅ Estrutura de diretórios
- ✅ Configuração do pyproject.toml
- ✅ Instalação do pacote
- ✅ Importação do módulo `app`
- ✅ Dependências principais
- ✅ Scripts disponíveis

### Passo 4: Executar a aplicação

```bash
uv run python -m app.main
```

Agora deve funcionar! 🎉

## 📋 Comandos Rápidos

### Verificação completa

```bash
# Verifica se está tudo configurado
uv run python scripts/verify_setup.py

# Se tudo estiver OK, inicia a API
uv run python -m app.main
```

### Limpar e reinstalar

```bash
# Windows PowerShell
Remove-Item -Recurse -Force .venv
uv sync

# Linux/macOS
rm -rf .venv
uv sync
```

### Testar importação

```bash
# Testa se o módulo pode ser importado
uv run python -c "import app; print(app.__version__)"

# Deve mostrar: 0.1.0
```

## 🐛 Se Ainda Não Funcionar

### Opção 1: Instalar em modo de desenvolvimento

```bash
uv pip install -e .
```

### Opção 2: Usar PYTHONPATH

```bash
# Windows PowerShell
$env:PYTHONPATH="src"; uv run python -m app.main

# Linux/macOS
PYTHONPATH=src uv run python -m app.main
```

### Opção 3: Mover o código (último recurso)

Se nada funcionar, você pode mover `src/app` para `app`:

```bash
# Windows PowerShell
Move-Item -Path src\app -Destination .
Remove-Item -Path src

# Linux/macOS
mv src/app .
rmdir src
```

Depois remova a configuração do hatch do `pyproject.toml`.

## 📚 Documentação

- **SETUP.md** — Guia completo de configuração
- **TROUBLESHOOTING.md** — Solução de problemas
- **QUICKSTART.md** — Guia rápido
- **scripts/verify_setup.py** — Script de verificação

## ✅ Checklist

Antes de executar a aplicação, verifique:

- [ ] `pyproject.toml` tem `[build-system]` com hatchling
- [ ] `pyproject.toml` tem `[tool.hatch.build.targets.wheel]`
- [ ] `src/app/__init__.py` existe
- [ ] `uv sync` foi executado sem erros
- [ ] `uv pip list` mostra `async-poc`
- [ ] `uv run python -c "import app"` funciona
- [ ] `uv run python scripts/verify_setup.py` passa em todos os checks

## 🎯 Fluxo Correto

```bash
# 1. Limpar e reinstalar
Remove-Item -Recurse -Force .venv  # Windows
uv sync

# 2. Verificar
uv run python scripts/verify_setup.py

# 3. Popular banco
uv run python scripts/seed_data.py

# 4. Iniciar API
uv run python -m app.main

# 5. Acessar
# http://localhost:8000/ui/
```

## 💡 Dica

Sempre que encontrar problemas de importação:

1. Execute `uv run python scripts/verify_setup.py`
2. Siga as instruções do script
3. Consulte `SETUP.md` para mais detalhes

---

**O problema foi resolvido!** 🎉

Agora você pode executar `uv run python -m app.main` sem erros de `ModuleNotFoundError`.
