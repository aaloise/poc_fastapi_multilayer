# 🔧 Configurando o Ambiente Python

## ✅ Correção Aplicada

O `pyproject.toml` foi atualizado para incluir a configuração do build system:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/app"]
```

Isso diz ao `uv` onde encontrar o pacote `app` (dentro do diretório `src/`).

## 🚀 Passos para Resolver o Problema

### 1. Reinstale as dependências

```bash
cd backend

# Remove o ambiente virtual antigo
rm -rf .venv  # Linux/macOS
# ou no Windows PowerShell:
Remove-Item -Recurse -Force .venv

# Reinstala tudo
uv sync
```

### 2. Verifique se o pacote foi instalado

```bash
uv pip list | grep async-poc
```

Deve mostrar algo como:
```
async-poc  0.1.0
```

### 3. Teste a importação

```bash
uv run python -c "import app; print(app.__version__)"
```

Deve mostrar:
```
0.1.0
```

### 4. Execute a aplicação

```bash
uv run python -m app.main
```

Agora deve funcionar! 🎉

## 📋 Comandos Úteis

### Verificar instalação

```bash
# Lista pacotes instalados
uv pip list

# Mostra informações do pacote
uv pip show async-poc

# Verifica dependências
uv pip check
```

### Limpar e reinstalar

```bash
# Remove ambiente virtual
rm -rf .venv  # Linux/macOS
Remove-Item -Recurse -Force .venv  # Windows PowerShell

# Remove cache do uv
uv cache clean

# Reinstala
uv sync
```

### Debug de imports

```bash
# Mostra o path do Python
uv run python -c "import sys; print('\n'.join(sys.path))"

# Verifica se o pacote está instalável
uv run python -c "import app; print(app.__file__)"
```

## 🐛 Se Ainda Não Funcionar

### Opção 1: Instalar em modo de desenvolvimento

```bash
uv pip install -e .
```

### Opção 2: Usar PYTHONPATH

```bash
# Linux/macOS
PYTHONPATH=src uv run python -m app.main

# Windows PowerShell
$env:PYTHONPATH="src"; uv run python -m app.main

# Windows CMD
set PYTHONPATH=src && uv run python -m app.main
```

### Opção 3: Mover o código (menos recomendado)

Se nada funcionar, você pode mover `src/app` para `app`:

```bash
# Linux/macOS
mv src/app .
rmdir src

# Windows PowerShell
Move-Item -Path src\app -Destination .
Remove-Item -Path src
```

Depois remova a configuração do hatch do `pyproject.toml`.

## 📚 Explicação Técnica

### Por que isso é necessário?

O `uv` usa o `pyproject.toml` para entender a estrutura do projeto. Sem a configuração `[tool.hatch.build.targets.wheel]`, ele não sabe que o pacote `app` está em `src/app`.

### O que o hatchling faz?

O `hatchling` é o build backend que:
1. Lê o `pyproject.toml`
2. Encontra o pacote `app` em `src/app`
3. Cria um "wheel" (pacote instalável)
4. Instala no ambiente virtual

### Por que usar a estrutura `src/`?

A estrutura `src/app` é uma boa prática porque:
- ✅ Evita imports acidentais do código local
- ✅ Testa o pacote como seria em produção
- ✅ Separa código fonte de outros arquivos
- ✅ Padrão recomendado pela Python Packaging Authority

## ✅ Checklist

- [ ] `pyproject.toml` tem `[build-system]` com hatchling
- [ ] `pyproject.toml` tem `[tool.hatch.build.targets.wheel]` apontando para `src/app`
- [ ] `src/app/__init__.py` existe
- [ ] `uv sync` foi executado sem erros
- [ ] `uv pip list` mostra `async-poc`
- [ ] `uv run python -c "import app"` funciona
- [ ] `uv run python -m app.main` inicia a aplicação

## 🎯 Próximos Passos

1. Execute os passos acima
2. Verifique se tudo funciona
3. Popule o banco: `uv run python scripts/seed_data.py`
4. Inicie a API: `uv run python -m app.main`
5. Acesse: http://localhost:8000/ui/

---

**Precisa de ajuda?** Consulte o [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
