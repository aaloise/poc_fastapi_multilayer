# 🎨 NiceGUI — Interface Web

## O que é?

NiceGUI é um **framework UI baseado em FastAPI e Vue.js** que permite criar interfaces web interativas diretamente do Python, sem precisar escrever HTML/CSS/JavaScript.

## Por que NiceGUI?

### Comparação com outras opções

| Opção | Complexidade | Velocidade | Python Only |
|-------|--------------|------------|-------------|
| **React + FastAPI** | Alta | Média | ❌ |
| **Streamlit** | Baixa | Alta | ✅ |
| **Gradio** | Baixa | Alta | ✅ |
| **NiceGUI** | **Média** | **Alta** | **✅** |

### Vantagens

1. **Python Only** — Tudo em Python, sem frontend separado
2. **Montado no FastAPI** — Mesma aplicação, mesma porta
3. **Vue.js internamente** — Componentes modernos
4. **WebSocket** — Real-time updates automáticos
5. **Dark Mode** — Suporte nativo
6. **Componentes ricos** — Charts, tables, forms, etc.

## Instalação

```bash
# Com uv
uv add nicegui

# Com pip
pip install nicegui
```

## Estrutura Básica

### Criando páginas

```python
# ui.py
from nicegui import ui

def setup_ui(prefix: str = "/ui"):
    """Registra páginas NiceGUI."""
    
    @ui.page(f"{prefix}/")
    async def dashboard():
        ui.dark_mode().enable()
        
        with ui.header().classes("bg-gray-900 text-white"):
            ui.label("⚡ Async POC Dashboard").classes("text-xl font-bold")
        
        with ui.row().classes("w-full gap-4 p-4"):
            with ui.card().classes("flex-1"):
                ui.label("📊 Tasks").classes("text-lg font-bold")
                stats = ui.label("Loading...")
        
        # Task list
        table = ui.table(
            columns=[
                {"name": "id", "label": "ID", "field": "id"},
                {"name": "name", "label": "Name", "field": "name"},
                {"name": "status", "label": "Status", "field": "status"},
            ],
            rows=[],
            row_key="id",
        )
        
        async def refresh():
            # Fetch from API
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get("http://localhost:8000/api/v1/tasks")
                if resp.status_code == 200:
                    table.rows = resp.json()
                    table.update()
        
        ui.button("🔄 Refresh", on_click=refresh)
        await refresh()
```

### Montando no FastAPI

```python
# main.py
from nicegui import ui
from app.ui import setup_ui

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db(settings.db_url)
    
    # Mount NiceGUI
    setup_ui(settings.ui_prefix)
    ui.run(
        title="Async POC",
        port=settings.port,
        reload=settings.debug,
        show=False,
        fastapi_app=app,  # Monta no mesmo FastAPI
    )
    
    yield
```

## Componentes

### Layout

```python
# Header
with ui.header().classes("bg-gray-900 text-white"):
    ui.label("Title").classes("text-xl")
    ui.space()
    ui.button("Action")

# Row (horizontal)
with ui.row().classes("gap-4"):
    ui.label("Item 1")
    ui.label("Item 2")

# Column (vertical)
with ui.column().classes("gap-2"):
    ui.label("Item 1")
    ui.label("Item 2")

# Card
with ui.card().classes("p-4"):
    ui.label("Content")
```

### Inputs

```python
# Text input
name = ui.input("Name", value="default")

# Select
priority = ui.select(["low", "medium", "high"], value="medium")

# Checkbox
enabled = ui.checkbox("Enable", value=True)

# Slider
volume = ui.slider(min=0, max=100, value=50)

# Date picker
date = ui.date()

# File upload
upload = ui.upload(on_upload=handle_upload)
```

### Buttons

```python
# Simple button
ui.button("Click me", on_click=handle_click)

# Button with icon
ui.button("Save", icon="save")

# Button group
with ui.button_group():
    ui.button("Left")
    ui.button("Right")
```

### Display

```python
# Label
ui.label("Text")

# Icon
ui.icon("home")

# Image
ui.image("https://example.com/image.png")

# Link
ui.link("Click here", "/target")

# Code
ui.code("print('hello')")

# Markdown
ui.markdown("# Title\n\n**Bold** text")
```

### Data Display

```python
# Table
table = ui.table(
    columns=[
        {"name": "id", "label": "ID", "field": "id"},
        {"name": "name", "label": "Name", "field": "name"},
    ],
    rows=[
        {"id": 1, "name": "Task 1"},
        {"id": 2, "name": "Task 2"},
    ],
    row_key="id",
)

# Update table
table.rows = new_rows
table.update()

# Chart
ui.chart({
    'title': 'My Chart',
    'series': [{'name': 'Sales', 'data': [10, 20, 30]}],
    'chart': {'type': 'line'},
    'xaxis': {'categories': ['Jan', 'Feb', 'Mar']},
})

# Log
log = ui.log(max_lines=20)
log.push("New log message")
```

### Dialogs

```python
# Alert
ui.alert("Warning!", "Something went wrong")

# Confirm
async def handle_delete():
    confirmed = await ui.confirm("Delete this item?")
    if confirmed:
        # Delete
        pass

# Dialog
with ui.dialog() as dialog, ui.card():
    ui.label("Dialog content")
    ui.button("Close", on_click=dialog.close)

ui.button("Open", on_click=dialog.open)
```

## Real-time Updates

### Timer

```python
# Update every 5 seconds
ui.timer(5.0, lambda: refresh_data())

# Update every second
ui.timer(1.0, lambda: update_clock())
```

### Auto-refresh

```python
@ui.page("/dashboard")
async def dashboard():
    stats = ui.label("Loading...")
    
    async def refresh():
        data = await get_stats()
        stats.text = f"Total: {data['total']}"
    
    # Refresh every 5 seconds
    ui.timer(5.0, refresh)
    
    # Initial load
    await refresh()
```

## Styling

### Tailwind CSS

```python
# Classes Tailwind
ui.label("Text").classes("text-xl font-bold text-blue-500")

# Responsive
ui.label("Text").classes("text-sm md:text-lg lg:text-xl")

# Spacing
ui.label("Text").classes("p-4 m-2")

# Flexbox
with ui.row().classes("flex items-center justify-between"):
    ...
```

### Dark Mode

```python
# Enable dark mode
ui.dark_mode().enable()

# Toggle
dark_mode = ui.dark_mode()
ui.button("Toggle", on_click=dark_mode.toggle)
```

## Events

### Click

```python
def handle_click():
    print("Clicked!")

ui.button("Click me", on_click=handle_click)
```

### Change

```python
def handle_change(e):
    print(f"Value: {e.value}")

ui.input("Name", on_change=handle_change)
```

### Async handlers

```python
async def handle_async_click():
    await asyncio.sleep(1)
    print("Done!")

ui.button("Async", on_click=handle_async_click)
```

## Integração com FastAPI

### Mesma aplicação

```python
# FastAPI routes
@app.get("/api/v1/tasks")
async def get_tasks():
    ...

# NiceGUI pages
@ui.page("/ui/dashboard")
async def dashboard():
    ...

# Ambas rodam na mesma porta
# http://localhost:8000/api/v1/tasks
# http://localhost:8000/ui/dashboard
```

### Chamando API do NiceGUI

```python
@ui.page("/ui/dashboard")
async def dashboard():
    async def fetch_tasks():
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8000/api/v1/tasks")
            return resp.json()
    
    tasks = await fetch_tasks()
    # Display tasks
```

## Exemplos Práticos

### Dashboard com Stats

```python
@ui.page("/ui/dashboard")
async def dashboard():
    ui.dark_mode().enable()
    
    with ui.header().classes("bg-gray-900 text-white"):
        ui.label("⚡ Dashboard").classes("text-xl")
    
    # Stats cards
    with ui.row().classes("w-full gap-4 p-4"):
        with ui.card().classes("flex-1 p-4"):
            ui.label("Total").classes("text-lg font-bold")
            total = ui.label("0")
        
        with ui.card().classes("flex-1 p-4"):
            ui.label("Pending").classes("text-lg font-bold")
            pending = ui.label("0")
        
        with ui.card().classes("flex-1 p-4"):
            ui.label("Completed").classes("text-lg font-bold")
            completed = ui.label("0")
    
    async def refresh():
        stats = await get_stats()
        total.text = str(stats["total"])
        pending.text = str(stats["pending"])
        completed.text = str(stats["completed"])
    
    ui.button("🔄 Refresh", on_click=refresh)
    ui.timer(5.0, refresh)
    await refresh()
```

### Task Creator

```python
@ui.page("/ui/create")
async def create_task_page():
    ui.dark_mode().enable()
    
    with ui.card().classes("w-full max-w-md p-6"):
        ui.label("Create Task").classes("text-xl font-bold mb-4")
        
        name = ui.input("Name").classes("w-full")
        priority = ui.select(
            ["low", "medium", "high"],
            value="medium",
            label="Priority"
        ).classes("w-full")
        
        result = ui.label("").classes("mt-4")
        
        async def create():
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "http://localhost:8000/api/v1/tasks",
                    json={"name": name.value, "priority": priority.value}
                )
                if resp.status_code == 201:
                    result.text = f"✅ Created: {resp.json()['id']}"
                    result.classes("text-green-500")
                else:
                    result.text = f"❌ Error: {resp.text}"
                    result.classes("text-red-500")
        
        ui.button("Create", on_click=create).classes("w-full mt-4")
```

### Task List with Actions

```python
@ui.page("/ui/tasks")
async def tasks_page():
    ui.dark_mode().enable()
    
    table = ui.table(
        columns=[
            {"name": "id", "label": "ID", "field": "id"},
            {"name": "name", "label": "Name", "field": "name"},
            {"name": "status", "label": "Status", "field": "status"},
            {"name": "actions", "label": "Actions", "field": "actions"},
        ],
        rows=[],
        row_key="id",
    ).classes("w-full")
    
    async def refresh():
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8000/api/v1/tasks")
            if resp.status_code == 200:
                table.rows = resp.json()
                table.update()
    
    ui.button("🔄 Refresh", on_click=refresh)
    await refresh()
```

## Produção

### Desabilitar em produção?

```python
# main.py
if settings.debug:
    setup_ui(settings.ui_prefix)
    ui.run(...)
```

Ou mantenha sempre ativo para monitoring.

### Performance

- NiceGUI é leve — não impacta performance
- WebSocket é eficiente
- Use `ui.timer()` com cuidado (não abuse)

### Security

```python
# Adicionar autenticação
from nicegui import app

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/ui/"):
        # Check auth
        if not is_authenticated(request):
            return RedirectResponse("/login")
    return await call_next(request)
```

## Links

- [NiceGUI no GitHub](https://github.com/zauberzeug/nicegui)
- [Documentação Oficial](https://nicegui.io/documentation)
- [Exemplos](https://nicegui.io/examples)
- [NiceGUI + FastAPI](https://nicegui.io/documentation/section_foundations)
