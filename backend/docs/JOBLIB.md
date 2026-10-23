# Joblib - Processamento Paralelo

## O que é?

Joblib é uma biblioteca para **processamento paralelo** em Python, otimizada para tarefas **CPU-bound**.

## Quando usar?

### Joblib vs Queuefy vs Prefect

| Componente | Tipo | Use para |
|-----------|------|----------|
| **Joblib** | CPU-bound | Cálculos pesados, ML, data processing |
| **Queuefy** | I/O-bound | API calls, DB queries, file I/O |
| **Prefect** | Orchestration | Workflows complexos, ETL pipelines |

### Exemplos de uso

**Joblib (CPU-bound):**
- Treinamento de modelos de ML
- Processamento de imagens/vídeo
- Cálculos matemáticos intensivos
- Feature engineering
- Simulações numéricas

**Queuefy (I/O-bound):**
- Enviar emails
- Fazer requests HTTP
- Ler/escrever arquivos
- Consultar banco de dados
- Processar filas de mensagens

**Prefect (Orchestration):**
- Pipeline ETL completo
- Workflow multi-step
- Agendamento de tarefas
- Monitoramento de jobs

## Como funciona?

### Arquitetura

```
┌─────────────────────────────────────────┐
│         FastAPI Request                  │
│   POST /api/v1/parallel/compute         │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│         routes.py                        │
│   await parallel_map(func, items)       │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│         parallel.py                      │
│   loop.run_in_executor(_executor, ...)  │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│    ProcessPoolExecutor (multiprocessing) │
│                                          │
│  ┌────────┐ ┌────────┐ ┌────────┐      │
│  │Worker 1│ │Worker 2│ │Worker 3│ ...  │
│  │(CPU)   │ │(CPU)   │ │(CPU)   │      │
│  └────────┘ └────────┘ └────────┘      │
│                                          │
│  Joblib.Parallel(n_jobs=-1)             │
└─────────────────────────────────────────┘
```

## Uso

### 1. Processamento paralelo simples

```python
from app.parallel import parallel_map, heavy_computation

# Processa 1000 itens em paralelo
results = await parallel_map(
    heavy_computation,
    list(range(1000)),
    n_jobs=4  # 4 processos paralelos
)
```

### 2. Processamento em lotes

```python
from app.parallel import parallel_batch, process_data_batch

# Processa lotes de dados em paralelo
batches = [
    [{"id": 1, "value": 10}],
    [{"id": 2, "value": 20}],
    [{"id": 3, "value": 30}],
]

results = await parallel_batch(
    process_data_batch,
    batches,
    n_jobs=3
)
```

### 3. Via API

```bash
# Executa computação paralela
curl -X POST "http://localhost:8000/api/v1/parallel/compute?items=1000&n_jobs=4"

# Resposta
{
  "items": 1000,
  "n_jobs": 4,
  "results": 1000,
  "duration_seconds": 2.345,
  "throughput": 426.44
}
```

## Configuração

### Inicialização

```python
# main.py
from app.parallel import init_parallel, shutdown_parallel

@nicegui_app.on_event("startup")
async def startup_event():
    init_parallel(n_jobs=-1)  # -1 = usa todos os cores

@nicegui_app.on_event("shutdown")
async def shutdown_event():
    shutdown_parallel()
```

### Parâmetros

```python
# n_jobs: número de processos paralelos
n_jobs=4    # 4 processos
n_jobs=-1   # todos os cores disponíveis
n_jobs=-2   # todos menos 1 core
```

## Exemplos Práticos

### 1. Treinamento de ML distribuído

```python
from app.parallel import parallel_map

def train_model_chunk(chunk):
    """Treina modelo em um chunk de dados."""
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(chunk["X"], chunk["y"])
    return {"coefficients": model.coef_.tolist()}

# Divide dados em chunks
chunks = split_data(data, n_chunks=8)

# Treina em paralelo
results = await parallel_map(
    train_model_chunk,
    chunks,
    n_jobs=8
)
```

### 2. Processamento de imagens

```python
from app.parallel import parallel_map
from PIL import Image

def process_image(image_path):
    """Processa uma imagem (CPU-bound)."""
    img = Image.open(image_path)
    img = img.resize((800, 600))
    img = img.convert("L")  # grayscale
    img.save(f"processed_{image_path}")
    return image_path

# Processa 100 imagens em paralelo
results = await parallel_map(
    process_image,
    image_paths,
    n_jobs=4
)
```

### 3. Feature engineering

```python
from app.parallel import parallel_map
import numpy as np

def compute_features(data):
    """Computa features (CPU-bound)."""
    features = {
        "mean": np.mean(data),
        "std": np.std(data),
        "max": np.max(data),
        "min": np.min(data),
    }
    return features

# Computa features para 1000 séries temporais
results = await parallel_map(
    compute_features,
    time_series_list,
    n_jobs=-1
)
```

## Performance

### Benchmark

```bash
# Executa benchmark
uv run python scripts/benchmark.py

# Ou testa diretamente
curl -X POST "http://localhost:8000/api/v1/parallel/compute?items=10000&n_jobs=4"
```

### Comparação

| Cenário | Sequencial | Paralelo (4 cores) | Speedup |
|---------|------------|-------------------|---------|
| 1000 cálculos | 10s | 2.5s | 4x |
| 10000 cálculos | 100s | 25s | 4x |
| ML training | 60s | 15s | 4x |

**Nota:** Speedup máximo teórico = número de cores (Lei de Amdahl)

## Boas Práticas

### 1. Use para CPU-bound, não I/O-bound

```python
# ✅ Correto - CPU-bound
def heavy_computation(n):
    result = 0
    for i in range(n * 1000):
        result += i * i
    return result

# ❌ Errado - I/O-bound (use Queuefy)
async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        return await client.get(url)
```

### 2. Evite overhead de serialização

```python
# ✅ Correto - dados pequenos
results = await parallel_map(func, small_items, n_jobs=4)

# ❌ Errado - dados grandes (overhead de serialização)
results = await parallel_map(func, huge_dataframes, n_jobs=4)
```

### 3. Escolha n_jobs adequadamente

```python
# CPU-bound puro
n_jobs = -1  # usa todos os cores

# Misto CPU + I/O
n_jobs = cpu_count() // 2  # deixa cores para I/O

# Servidor compartilhado
n_jobs = 2  # não sobrecarrega o servidor
```

### 4. Monitore uso de CPU

```python
import psutil

# Verifica uso de CPU
cpu_percent = psutil.cpu_percent(interval=1)
print(f"CPU usage: {cpu_percent}%")
```

## Troubleshooting

### Problema: Processamento lento

**Causa:** Overhead de serialização de dados grandes

**Solução:**
- Reduza tamanho dos dados
- Use shared memory (advanced)
- Aumente `n_jobs`

### Problema: MemoryError

**Causa:** Muitos processos alocando memória

**Solução:**
- Reduza `n_jobs`
- Processe em lotes menores
- Use `max_nbytes` no Joblib

### Problema: Deadlock

**Causa:** Processos esperando uns pelos outros

**Solução:**
- Evite shared state
- Use queues para comunicação
- Simplifique lógica paralela

## Integração com outros componentes

### Joblib + Queuefy

```python
# Queuefy gerencia a task (I/O-bound)
@_queuefy.task("process_batch")
async def handle_process_batch(batch_id: str):
    # Busca dados do banco (I/O-bound)
    data = await fetch_batch_data(batch_id)
    
    # Processa em paralelo (CPU-bound)
    results = await parallel_map(
        heavy_computation,
        data,
        n_jobs=4
    )
    
    # Salva resultados (I/O-bound)
    await save_results(results)
```

### Joblib + Prefect

```python
# Prefect orquestra o workflow
@flow(name="ml-training")
async def ml_training_flow():
    # Busca dados
    data = await fetch_data_task()
    
    # Treina em paralelo (Joblib)
    models = await parallel_map(
        train_model,
        data_chunks,
        n_jobs=8
    )
    
    # Avalia modelos
    results = await evaluate_models_task(models)
    
    return results
```

## Links

- [Joblib Documentation](https://joblib.readthedocs.io/)
- [Joblib Parallel](https://joblib.readthedocs.io/en/latest/parallel.html)
- [Python Multiprocessing](https://docs.python.org/3/library/multiprocessing.html)
