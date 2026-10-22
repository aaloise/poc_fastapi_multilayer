# 🦀 Granian — Servidor ASGI

## O que é?

Granian é um **servidor HTTP de alta performance** escrito em **Rust** para aplicações Python ASGI/WSGI.

## Por que Granian?

### Comparação com outros servidores

| Servidor | Linguagem | Performance | Features |
|----------|-----------|-------------|----------|
| **Uvicorn** | Python | Boa | Simples, popular |
| **Hypercorn** | Python | Média | HTTP/2, WebSocket |
| **Daphne** | Python | Média | Django Channels |
| **Granian** | **Rust** | **Excelente** | **HTTP/2, WebSocket, multi-worker** |

### Vantagens do Granian

1. **Performance** — Escrito em Rust, muito mais rápido que servidores Python
2. **HTTP/2** — Suporte nativo
3. **WebSocket** — Suporte nativo
4. **Multi-worker** — Gerenciamento de processos
5. **Graceful reload** — Reinício sem derrubar conexões
6. **Auto-detecção** — Detecta uvloop automaticamente

## Instalação

```bash
# Com uv
uv add granian[uvloop]

# Com pip
pip install "granian[uvloop]"
```

O `[uvloop]` instala o uvloop junto, que é o event loop mais rápido.

## Configuração

### granian.toml

```toml
# Endereço e porta
address = "0.0.0.0"
port = 8000

# Interface (ASGI para FastAPI)
interface = "asgi"

# Protocolo HTTP
http = "auto"  # Auto-detecta HTTP/1 ou HTTP/2

# Workers (processos)
workers = 4

# Threads por worker
threads = 2

# Backpressure (limite de conexões pendentes)
backpressure = 1024

# WebSocket
enable-websocket = true

# Logging
log-level = "info"

# Graceful shutdown
graceful-timeout = 30

# Respawn workers falhos
respawn-failed-workers = true
respawn-interval = 3.5
```

## Uso

### Desenvolvimento

```bash
# Com uvicorn (reload automático)
uv run python -m app.main
```

### Produção

```bash
# Com Granian
uv run granian --interface asgi --config granian.toml app.main:app

# Ou diretamente
uv run granian app.main:app --interface asgi --workers 4 --threads 2
```

### Docker

```dockerfile
CMD ["uv", "run", "granian", "--interface", "asgi", "--config", "granian.toml", "app.main:app"]
```

## Como Funciona

```
┌─────────────────────────────────────────┐
│         Granian (Rust)                  │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Worker 1 (processo)            │   │
│  │  ├─ Thread 1                    │   │
│  │  ├─ Thread 2                    │   │
│  │  └─ uvloop (event loop)         │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Worker 2 (processo)            │   │
│  │  ├─ Thread 1                    │   │
│  │  ├─ Thread 2                    │   │
│  │  └─ uvloop (event loop)         │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ... (mais workers)                    │
└─────────────────────────────────────────┘
```

### Arquitetura Multi-Worker

- **Workers** = Processos separados (isolamento, segurança)
- **Threads** = Threads dentro de cada worker (concorrência)
- **uvloop** = Event loop ultra-rápido (libuv)

### Quando usar mais workers?

```bash
# Regra geral: 2-4 workers por CPU core
# Exemplo: 4 cores = 8-16 workers

# CPU-bound (cálculos pesados)
workers = 4  # Menos workers, mais threads

# I/O-bound (banco, API externa)
workers = 8  # Mais workers, menos threads
```

## uvloop

### O que é?

uvloop é uma implementação do event loop do asyncio baseada em **libuv** (a mesma do Node.js).

### Performance

```
asyncio padrão:  ~50k requests/seg
uvloop:          ~150k requests/seg (3x mais rápido)
```

### Como funciona?

```python
# main.py
import asyncio

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    UVLOOP = True
except ImportError:
    UVLOOP = False
```

O Granian detecta automaticamente se uvloop está instalado e usa.

## Comparação de Performance

### Benchmark (requests/seg)

```
Uvicorn (Python):     50,000
Hypercorn (Python):   45,000
Granian (Rust):      150,000
Granian + uvloop:    200,000
```

### Latência (p99)

```
Uvicorn:              50ms
Hypercorn:            55ms
Granian:              15ms
Granian + uvloop:     10ms
```

## Configurações Importantes

### Workers

```toml
# Número de processos
workers = 4

# Auto-detecta CPUs
# workers = 0  # Usa todos os cores disponíveis
```

### Threads

```toml
# Threads por worker
threads = 2

# Para I/O-bound (banco, API)
threads = 4

# Para CPU-bound (cálculos)
threads = 1
```

### Backpressure

```toml
# Limite de conexões pendentes
backpressure = 1024

# Se atingir o limite, rejeita novas conexões
# Protege contra overload
```

### Graceful Shutdown

```toml
# Tempo para finalizar requests em andamento
graceful-timeout = 30

# Durante deploy, espera 30s antes de matar workers
```

### Respawn

```toml
# Reinicia workers que crasharam
respawn-failed-workers = true
respawn-interval = 3.5  # segundos
```

## Monitoramento

### Logs

```bash
# Info
uv run granian app.main:app --log-level info

# Debug
uv run granian app.main:app --log-level debug

# JSON (para ELK/Loki)
uv run granian app.main:app --log-dict-config '{"format": "json"}'
```

### Health Check

```bash
# Verificar se está rodando
curl http://localhost:8000/api/v1/health

# Docker
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## SSL/TLS

```toml
# granian.toml
ssl-certificate = "/path/to/cert.pem"
ssl-keyfile = "/path/to/key.pem"
```

Ou use um reverse proxy (nginx, Caddy) na frente.

## WebSocket

```toml
# Habilitar WebSocket
enable-websocket = true
```

Funciona automaticamente com FastAPI WebSocket endpoints.

## HTTP/2

```toml
# Auto-detecta HTTP/1 ou HTTP/2
http = "auto"

# Forçar HTTP/2
http = "2"
```

## Troubleshooting

### Worker crashando

```bash
# Aumentar logs
uv run granian app.main:app --log-level debug

# Verificar memory leak
# Usar memory_profiler
```

### Lentidão

```bash
# Aumentar workers
workers = 8

# Aumentar threads (para I/O)
threads = 4

# Verificar se uvloop está ativo
# Deve aparecer "uvloop=True" nos logs
```

### Conexões caindo

```bash
# Aumentar backpressure
backpressure = 2048

# Aumentar timeout
graceful-timeout = 60
```

## Produção

### Systemd Service

```ini
# /etc/systemd/system/async-poc.service
[Unit]
Description=Async POC
After=network.target

[Service]
User=www-data
WorkingDirectory=/app/backend
ExecStart=/usr/local/bin/uv run granian --interface asgi --config granian.toml app.main:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable async-poc
sudo systemctl start async-poc
sudo systemctl status async-poc
```

### Docker Compose

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - POC_DEBUG=false
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Nginx Reverse Proxy

```nginx
upstream async_poc {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://async_poc;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Links

- [Granian no GitHub](https://github.com/emmett-framework/granian)
- [Granian no PyPI](https://pypi.org/project/granian/)
- [uvloop no GitHub](https://github.com/MagicStack/uvloop)
- [Documentação](https://github.com/emmett-framework/granian#readme)
