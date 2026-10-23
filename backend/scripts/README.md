# 📜 Scripts — Automação e Testes

Este diretório contém scripts para facilitar o desenvolvimento, teste e operação da POC.

## 📋 Lista de Scripts

### Desenvolvimento

- **`dev.py`** — Script principal de desenvolvimento (comandos úteis)
- **`seed_data.py`** — Popula banco com dados de exemplo

### Testes

- **`test_interactive.py`** — Testes interativos completos
- **`test_dashboard.py`** — Dashboard de testes (NiceGUI)
- **`benchmark.py`** — Benchmark de performance

### Produção

- **`setup_production.sh`** — Configura ambiente de produção com PostgreSQL

## 🚀 Uso Rápido

### Script de Desenvolvimento

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

### Ou via Makefile

```bash
make dev              # Inicia API
make seed             # Popula banco
make test-interactive # Testes interativos
make benchmark        # Benchmark
make reset            # Reseta banco
make logs             # Mostra logs
make shell            # Shell Python
```

## 📖 Documentação Detalhada

### dev.py

Script multifuncional para desenvolvimento.

**Comandos:**

- `start` — Inicia API em modo desenvolvimento
- `seed` — Popula banco com dados de exemplo
- `test` — Executa testes interativos
- `benchmark` — Executa benchmark
- `reset` — Reseta banco de dados
- `logs` — Mostra estatísticas do banco
- `shell` — Abre shell Python com contexto

**Exemplos:**

```bash
# Inicia API
uv run python scripts/dev.py start

# Popula banco
uv run python scripts/dev.py seed

# Ambiente de produção
POC_ENV=production uv run python scripts/dev.py logs
```

### seed_data.py

Popula o banco com 10 tasks de exemplo em diferentes status.

**O que cria:**

- 3 tasks pendentes (pending)
- 2 tasks em execução (running)
- 3 tasks completadas (completed)
- 2 tasks falhadas (failed)

**Uso:**

```bash
# Ambiente dev (SQLite)
uv run python scripts/seed_data.py

# Ambiente prod (PostgreSQL)
POC_ENV=production uv run python scripts/seed_data.py
```

### test_interactive.py

Executa 10 testes completos da POC de forma interativa.

**O que testa:**

1. Health Check
2. Create Task (simples)
3. Create Multiple Tasks (5 tasks)
4. List Tasks
5. Get Task by ID
6. Get Stats
7. Queuefy Integration
8. Prefect Flow
9. NiceGUI UI
10. Error Handling

**Uso:**

```bash
uv run python scripts/test_interactive.py
```

**Saída:**

- Mostra cada teste sendo executado
- Exibe resultados em tempo real
- Tabela com resumo final
- Tempo total de execução

### test_dashboard.py

Dashboard interativo no NiceGUI para executar testes.

**Acesso:**

```bash
# Inicie a API primeiro
uv run python -m app.main

# Acesse no navegador
http://localhost:8000/ui/tests
```

**Features:**

- Botões para executar testes individuais
- Botão para executar todos os testes
- Logs em tempo real
- Tabela de resumo

### benchmark.py

Mede performance da API em diferentes operações.

**O que mede:**

- Health Check
- Create Task
- List Tasks
- Get Task by ID
- Get Stats

**Métricas:**

- Min, Max, Mean, Median
- Std Dev, P95, P99
- Requests/s

**Uso:**

```bash
# Benchmark básico (10 requests)
uv run python scripts/benchmark.py

# Benchmark intenso (100 requests)
uv run python scripts/benchmark.py --requests 100
```

### setup_production.sh

Configura ambiente de produção com PostgreSQL.

**O que faz:**

1. Inicia PostgreSQL via Docker
2. Cria banco `poc_prod`
3. Cria arquivo `.env.production`
4. Popula banco com dados
5. Mostra instruções

**Uso:**

```bash
chmod +x scripts/setup_production.sh
./scripts/setup_production.sh
```

## 🎯 Workflows Comuns

### Desenvolvimento Local

```bash
# 1. Instala dependências
make install

# 2. Popula banco
make seed

# 3. Inicia API
make dev

# 4. Em outro terminal, executa testes
make test-interactive
```

### Teste de Performance

```bash
# 1. Inicia API
make dev

# 2. Popula com mais dados
uv run python scripts/seed_data.py

# 3. Executa benchmark
make benchmark

# 4. Ou benchmark intenso
make benchmark-heavy
```

### Ambiente de Produção

```bash
# 1. Configura ambiente
make setup-prod

# 2. Inicia API
make prod

# 3. Ou com Granian
make granian
```

### Debug

```bash
# 1. Inicia API
make dev

# 2. Em outro terminal, abre shell
make shell

# 3. No shell, testa funções
task = await create_task('test', {'foo': 'bar'})
stats = await get_stats()

# 4. Ver logs do banco
make logs
```

## 📊 Comparação de Ambientes

| Aspecto | Desenvolvimento | Produção |
|---------|----------------|----------|
| **Database** | SQLite (dev_poc.db) | PostgreSQL |
| **Debug** | ✅ Habilitado | ❌ Desabilitado |
| **Workers** | 4 | 8 |
| **Queue Concurrency** | 4 | 16 |
| **Log Level** | DEBUG | WARNING |
| **Host** | 127.0.0.1 | 0.0.0.0 |

## 🔧 Troubleshooting

### Script não executa

```bash
# Verifica permissões
chmod +x scripts/*.sh

# Verifica se uv está instalado
uv --version

# Instala uv se necessário
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Testes falham

```bash
# Verifica se API está rodando
curl http://localhost:8000/api/v1/health

# Se não estiver, inicia
make dev

# Executa testes novamente
make test-interactive
```

### Benchmark lento

```bash
# Reduz número de requests
uv run python scripts/benchmark.py --requests 5

# Verifica uso de CPU
top

# Fecha outros processos
```

### PostgreSQL não conecta

```bash
# Verifica se container está rodando
docker ps | grep poc-postgres

# Se não estiver, inicia
docker start poc-postgres

# Verifica se banco existe
docker exec -it poc-postgres psql -U poc -c "\l"
```

## 📚 Links Relacionados

- [Guia de Testes Completo](../docs/TESTING_GUIDE.md)
- [Documentação de Testes](../docs/TESTING.md)
- [Guia de Deploy](../docs/DEPLOYMENT.md)

## 💡 Dicas

1. **Use o dev.py** — É o script mais completo para desenvolvimento
2. **Teste antes de commit** — Execute `make test-interactive`
3. **Benchmark regularmente** — Monitore performance
4. **Use ambientes separados** — Dev (SQLite) vs Prod (PostgreSQL)
5. **Leia os logs** — Eles mostram o que está acontecendo

---

**Divirta-se testando!** 🎉
