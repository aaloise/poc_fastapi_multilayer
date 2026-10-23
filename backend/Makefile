.PHONY: install dev prod granian test test-interactive benchmark seed reset logs shell docker-build docker-up docker-down help

# Help
help:
	@echo "Async POC — Comandos disponíveis"
	@echo ""
	@echo "Instalação:"
	@echo "  make install          Instala dependências (uv sync)"
	@echo ""
	@echo "Desenvolvimento:"
	@echo "  make dev              Inicia API em modo dev (SQLite)"
	@echo "  make seed             Popula banco com dados de exemplo"
	@echo "  make reset            Reseta banco de dados"
	@echo "  make logs             Mostra logs/estatísticas do banco"
	@echo "  make shell            Abre shell Python com contexto"
	@echo ""
	@echo "Testes:"
	@echo "  make test             Executa testes unitários (pytest)"
	@echo "  make test-interactive Executa testes interativos"
	@echo "  make benchmark        Executa benchmark de performance"
	@echo ""
	@echo "Produção:"
	@echo "  make prod             Inicia API em modo produção (PostgreSQL)"
	@echo "  make granian          Inicia com Granian (recomendado)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build da imagem Docker"
	@echo "  make docker-up        Sobe containers (docker-compose)"
	@echo "  make docker-down      Derruba containers"
	@echo ""
	@echo "Qualidade:"
	@echo "  make lint             Roda linter (ruff)"
	@echo "  make format           Formata código (ruff format)"
	@echo ""

# Instalação
install:
	@echo "📦 Instalando dependências..."
	uv sync
	@echo "✓ Dependências instaladas"

install-dev:
	@echo "📦 Instalando dependências de desenvolvimento..."
	uv sync --dev
	@echo "✓ Dependências instaladas"

# Desenvolvimento
dev:
	@echo "🚀 Iniciando API (DEV)..."
	@echo "   Ambiente: development"
	@echo "   Database: SQLite (dev_poc.db)"
	@echo "   URL: http://localhost:8000"
	@echo ""
	POC_ENV=development uv run python -m app.main

seed:
	@echo "🌱 Populando banco..."
	uv run python scripts/seed_data.py

reset:
	@echo "⚠️  Resetando banco..."
	uv run python scripts/dev.py reset

logs:
	@echo "📊 Logs do banco..."
	uv run python scripts/dev.py logs

shell:
	@echo "🐍 Abrindo shell..."
	uv run python scripts/dev.py shell

# Testes
test:
	@echo "🧪 Executando testes unitários..."
	uv run pytest tests/ -v --asyncio-mode=auto

test-cov:
	@echo "🧪 Executando testes com coverage..."
	uv run pytest tests/ -v --asyncio-mode=auto --cov=src/app --cov-report=term-missing

test-interactive:
	@echo "🧪 Executando testes interativos..."
	uv run python scripts/test_interactive.py

benchmark:
	@echo "⚡ Executando benchmark..."
	uv run python scripts/benchmark.py --requests 10

benchmark-heavy:
	@echo "⚡ Executando benchmark intenso..."
	uv run python scripts/benchmark.py --requests 100

# Produção
prod:
	@echo "🚀 Iniciando API (PROD)..."
	@echo "   Ambiente: production"
	@echo "   Database: PostgreSQL"
	@echo "   URL: http://localhost:8000"
	@echo ""
	@echo "⚠️  Certifique-se de que o PostgreSQL está rodando:"
	@echo "   docker start poc-postgres"
	@echo ""
	POC_ENV=production uv run python -m app.main

granian:
	@echo "🦀 Iniciando com Granian..."
	@echo "   Ambiente: production"
	@echo "   Server: Granian (Rust)"
	@echo "   URL: http://localhost:8000"
	@echo ""
	POC_ENV=production uv run granian --interface asgi --config granian.toml app.main:app

setup-prod:
	@echo "🚀 Configurando ambiente de produção..."
	chmod +x scripts/setup_production.sh
	./scripts/setup_production.sh

# Docker
docker-build:
	@echo "🐳 Build Docker image..."
	docker build -t async-poc .

docker-up:
	@echo "🐳 Subindo containers..."
	docker-compose up -d

docker-down:
	@echo "🐳 Derrubando containers..."
	docker-compose down

docker-logs:
	@echo "🐳 Logs dos containers..."
	docker-compose logs -f

# Qualidade
lint:
	@echo "🔍 Rodando linter..."
	uv run ruff check src/ tests/ scripts/

lint-fix:
	@echo "🔍 Rodando linter (auto-fix)..."
	uv run ruff check --fix src/ tests/ scripts/

format:
	@echo "🎨 Formatando código..."
	uv run ruff format src/ tests/ scripts/

type-check:
	@echo "🔍 Verificando tipos..."
	uv run mypy src/

# Limpeza
clean:
	@echo "🧹 Limpando..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache .pytest_cache .ruff_cache dist/ build/ *.egg-info
	rm -f dev_poc.db poc.db
	@echo "✓ Limpo"

# Tudo
all: install seed dev

# Quick start
quick:
	@echo "🚀 Quick start..."
	@echo "1. Instalando dependências..."
	@uv sync
	@echo "2. Populando banco..."
	@uv run python scripts/seed_data.py
	@echo "3. Iniciando API..."
	@echo ""
	@echo "✓ Pronto! Acesse: http://localhost:8000/ui/"
	@echo ""
	@POC_ENV=development uv run python -m app.main
