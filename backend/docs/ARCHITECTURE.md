# 🏗️ Arquitetura

## Visão Geral

Esta POC usa uma **arquitetura flat** (plana) — sem camadas desnecessárias, direto ao ponto.

```
backend/src/app/
├── main.py         # Entry point + lifespan
├── config.py       # Settings centralizadas
├── models.py       # Domain + DB models
├── services.py     # Business logic
├── routes.py       # FastAPI routes
├── ui.py           # NiceGUI pages
├── queue.py        # Queuefy integration
├── parallel.py     # Joblib (CPU-bound tasks)
├── flows.py        # Prefect flows
└── database.py     # DB setup
```

## Por que Flat?

### ✅ Vantagens

1. **Simplicidade** — 9 arquivos, fácil de navegar
2. **Direto ao ponto** — sem abstrações desnecessárias
3. **Fácil de entender** — iniciantes conseguem seguir
4. **Rápido de desenvolver** — menos boilerplate
5. **Funciona bem para POCs** — perfeito para provar conceitos

### ❌ Quando NÃO usar

- Projetos grandes (100+ arquivos)
- Times grandes (10+ devs)
- Quando precisa de separação rigorosa (DDD, Clean Arch)
- Quando há múltiplos domínios complexos

## Fluxo de Execução

```
┌─────────────────────────────────────────────────────────┐
│                    REQUEST HTTP                          │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Granian (Rust ASGI Server)                 │
│              + uvloop (Fast Event Loop)                 │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                 FastAPI Framework                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  routes.py — Endpoints HTTP                      │  │
│  │  • POST /api/v1/tasks                            │  │
│  │  • GET /api/v1/tasks                             │  │
│  │  • GET /api/v1/tasks/{id}                        │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              services.py — Business Logic               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  • create_task()                                 │  │
│  │  • execute_task()                                │  │
│  │  • get_task_by_id()                              │  │
│  │  • get_all_tasks()                               │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
┌──────────────────────┐  ┌──────────────────────┐
│   database.py        │  │    queue.py          │
│   SQLAlchemy async   │  │    Queuefy           │
│                      │  │                      │
│   • init_db()        │  │   • init_queue()     │
│   • get_session()    │  │   • enqueue()        │
│   • close_db()       │  │   • Worker           │
└──────────────────────┘  └──────────────────────┘
              │                     │
              ▼                     ▼
┌──────────────────────┐  ┌──────────────────────┐
│   models.py          │  │  queuefy_* tables    │
│   tasks table        │  │  (auto-created)      │
│                      │  │                      │
│   • Task (Pydantic)  │  │  • queuefy_runs      │
│   • TaskRow (SQLA)   │  │  • queuefy_schedules │
└──────────────────────┘  └──────────────────────┘
```

## Responsabilidades de Cada Arquivo

### `main.py` — Entry Point

**O que faz:**
- Cria a aplicação FastAPI
- Gerencia o lifespan (startup/shutdown)
- Inicializa banco, queue, UI
- Configura middleware

**Quando mexer:**
- Adicionar novo middleware
- Mudar ordem de inicialização
- Adicionar novo serviço no startup

### `config.py` — Configurações

**O que faz:**
- Define todas as configurações
- Carrega de variáveis de ambiente
- Valida com Pydantic

**Quando mexer:**
- Adicionar nova configuração
- Mudar valores padrão
- Adicionar validação

### `models.py` — Modelos

**O que faz:**
- Define entidades de domínio (Pydantic)
- Define modelos de banco (SQLAlchemy)
- Funções de conversão entre eles

**Quando mexer:**
- Adicionar novo campo
- Mudar schema do banco
- Adicionar nova entidade

### `services.py` — Lógica de Negócio

**O que faz:**
- Implementa casos de uso
- Coordena operações
- Não conhece HTTP ou banco diretamente

**Quando mexer:**
- Adicionar nova operação
- Mudar regras de negócio
- Refatorar lógica

### `routes.py` — Endpoints HTTP

**O que faz:**
- Define rotas REST
- Valida requests
- Chama services
- Retorna responses

**Quando mexer:**
- Adicionar novo endpoint
- Mudar API
- Adicionar validação

### `ui.py` — Interface Web

**O que faz:**
- Define páginas NiceGUI
- Dashboard interativo
- Visualização em tempo real

**Quando mexer:**
- Adicionar nova página
- Mudar layout
- Adicionar gráficos

### `queue.py` — Fila de Tarefas

**O que faz:**
- Integra com Queuefy
- Registra handlers
- Gerencia worker

**Quando mexer:**
- Adicionar novo handler
- Mudar retry policy
- Adicionar cron job

### `flows.py` — Orquestração

**O que faz:**
- Define flows Prefect
- Orquestra workflows complexos
- Retry e monitoring

**Quando mexer:**
- Adicionar novo flow
- Mudar pipeline
- Adicionar steps

### `database.py` — Banco de Dados

**O que faz:**
- Cria engine SQLAlchemy
- Gerencia sessions
- Inicializa tabelas

**Quando mexer:**
- Mudar URL do banco
- Adicionar connection pool
- Mudar driver

## Princípios de Design

### 1. Separação de Preocupações

Cada arquivo tem UMA responsabilidade clara:
- `routes.py` → HTTP
- `services.py` → Lógica
- `models.py` → Dados
- `queue.py` → Fila

### 2. Dependências Unidirecionais

```
routes.py → services.py → models.py
                ↓
           database.py
                ↓
           queue.py
```

Nunca o contrário!

### 3. Async First

Tudo é async/await:
- FastAPI é async
- SQLAlchemy é async
- Queuefy é async
- Prefect é async

### 4. Configuração Externa

Nada hardcoded:
- URLs de banco via env vars
- Portas via env vars
- Flags via env vars

### 5. Testável

Cada parte pode ser testada isoladamente:
- Services sem HTTP
- Models sem banco
- Queue sem worker

## Comparação com Arquiteturas Tradicionais

### Clean Architecture (4 camadas)

```
presentation/
application/
domain/
infrastructure/
```

**Problemas para POC:**
- Muitos arquivos
- Difícil de navegar
- Over-engineering

### MVC (Model-View-Controller)

```
models/
views/
controllers/
```

**Problemas:**
- Controllers ficam gigantes
- Views misturadas com lógica
- Não escala bem

### Flat Architecture (esta POC)

```
9 arquivos, tudo claro
```

**Vantagens:**
- Simples
- Rápido
- Fácil de entender
- Perfeito para POCs

## Quando Migrar para Arquitetura em Camadas?

Considere migrar quando:

1. **Projeto cresce** — 50+ arquivos
2. **Time cresce** — 10+ devs
3. **Domínios complexos** — múltiplos bounded contexts
4. **Reuso** — precisa compartilhar código entre projetos
5. **Testabilidade** — precisa de mocks complexos

### Como Migrar

```
# De (flat)
models.py → models/domain.py + models/db.py
services.py → application/services.py
routes.py → presentation/routes.py
queue.py → infrastructure/queue.py

# Para (camadas)
src/app/
├── domain/
│   ├── entities.py
│   └── value_objects.py
├── application/
│   └── services.py
├── infrastructure/
│   ├── database.py
│   └── queue.py
└── presentation/
    ├── routes.py
    └── ui.py
```

## Conclusão

Esta arquitetura flat é **intencionalmente simples** para:
- Provar conceitos rapidamente
- Facilitar o aprendizado
- Demonstrar tecnologias
- Servir como base para projetos maiores

Para projetos de produção grandes, considere migrar para uma arquitetura em camadas mais robusta.
