#!/bin/bash
# Script de Setup — Configura ambiente de produção com PostgreSQL
# ================================================================
#
# Uso:
#     ./scripts/setup_production.sh
#
# Este script:
# 1. Inicia PostgreSQL via Docker
# 2. Cria o banco de dados
# 3. Configura variáveis de ambiente
# 4. Inicia a aplicação em modo produção

set -e

echo "🚀 Async POC — Setup Production"
echo "================================"
echo

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verifica se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Docker não está rodando. Por favor, inicie o Docker.${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Passo 1: Iniciando PostgreSQL...${NC}"

# Cria rede Docker se não existir
docker network create poc-network 2>/dev/null || true

# Para container anterior se existir
docker stop poc-postgres 2>/dev/null || true
docker rm poc-postgres 2>/dev/null || true

# Inicia PostgreSQL
docker run -d \
    --name poc-postgres \
    --network poc-network \
    -e POSTGRES_USER=poc \
    -e POSTGRES_PASSWORD=poc \
    -e POSTGRES_DB=poc_prod \
    -p 5432:5432 \
    -v poc-postgres-data:/var/lib/postgresql/data \
    postgres:16-alpine

echo -e "${GREEN}✓ PostgreSQL iniciado${NC}"

# Aguarda PostgreSQL estar pronto
echo -e "${BLUE}⏳ Aguardando PostgreSQL estar pronto...${NC}"
sleep 5

# Verifica se PostgreSQL está rodando
if ! docker exec poc-postgres pg_isready > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  PostgreSQL não está pronto. Aguardando mais...${NC}"
    sleep 5
fi

echo -e "${GREEN}✓ PostgreSQL está pronto${NC}"

echo
echo -e "${BLUE}📝 Passo 2: Configurando variáveis de ambiente...${NC}"

# Cria arquivo .env.production
cat > .env.production << EOF
# Produção — PostgreSQL
POC_APP_NAME=Async POC (PROD)
POC_DEBUG=false
POC_ENV=production
POC_HOST=0.0.0.0
POC_PORT=8000
POC_WORKERS=8
POC_DB_URL=postgresql+asyncpg://poc:poc@localhost:5432/poc_prod
POC_DB_ECHO=false
POC_QUEUE_CONCURRENCY=16
POC_UI_PREFIX=/ui
POC_LOG_LEVEL=WARNING
EOF

echo -e "${GREEN}✓ Arquivo .env.production criado${NC}"

echo
echo -e "${BLUE}🌱 Passo 3: Populando banco com dados de exemplo...${NC}"

# Instala dependências se necessário
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠️  uv não encontrado. Instalando...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Sync dependencies
uv sync

# Executa seed
POC_ENV=production uv run python scripts/seed_data.py

echo -e "${GREEN}✓ Banco populado${NC}"

echo
echo -e "${BLUE}🚀 Passo 4: Iniciando aplicação em modo produção...${NC}"

echo
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Setup concluído!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo
echo -e "${BLUE}Próximos passos:${NC}"
echo
echo -e "  1. Inicie a aplicação:"
echo -e "     ${YELLOW}POC_ENV=production uv run python -m app.main${NC}"
echo
echo -e "  2. Ou use Granian (recomendado para produção):"
echo -e "     ${YELLOW}POC_ENV=production uv run granian --interface asgi app.main:app${NC}"
echo
echo -e "  3. Acesse:"
echo -e "     ${YELLOW}API:        http://localhost:8000/api/v1/health${NC}"
echo -e "     ${YELLOW}Dashboard:  http://localhost:8000/ui/${NC}"
echo -e "     ${YELLOW}Tests:      http://localhost:8000/ui/tests${NC}"
echo -e "     ${YELLOW}Docs:       http://localhost:8000/docs${NC}"
echo
echo -e "  4. Execute os testes:"
echo -e "     ${YELLOW}uv run python scripts/test_interactive.py${NC}"
echo
echo -e "  5. Execute o benchmark:"
echo -e "     ${YELLOW}uv run python scripts/benchmark.py --requests 50${NC}"
echo
echo -e "${BLUE}PostgreSQL:${NC}"
echo -e "  ${YELLOW}docker exec -it poc-postgres psql -U poc -d poc_prod${NC}"
echo
echo -e "${BLUE}Para parar:${NC}"
echo -e "  ${YELLOW}docker stop poc-postgres${NC}"
echo -e "  ${YELLOW}docker rm poc-postgres${NC}"
echo
echo -e "${BLUE}Para limpar tudo:${NC}"
echo -e "  ${YELLOW}docker stop poc-postgres && docker rm poc-postgres${NC}"
echo -e "  ${YELLOW}docker volume rm poc-postgres-data${NC}"
echo
