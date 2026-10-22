"""NiceGUI — Dashboard interativo."""

from datetime import datetime
from nicegui import ui


def setup_ui(prefix: str = "/ui") -> None:
    """Registra páginas NiceGUI."""

    @ui.page(f"{prefix}/")
    async def dashboard():
        ui.dark_mode().enable()

        with ui.header().classes("bg-gray-900 text-white"):
            ui.label("⚡ Async POC Dashboard").classes("text-xl font-bold")
            ui.space()
            ui.label(datetime.utcnow().strftime("%H:%M:%S")).classes("text-sm")

        with ui.row().classes("w-full gap-4 p-4"):
            with ui.card().classes("flex-1 p-4"):
                ui.label("📊 Tasks").classes("text-lg font-bold")
                stats = ui.label("Loading...")

            with ui.card().classes("flex-1 p-4"):
                ui.label("⚡ Queue").classes("text-lg font-bold")
                ui.label("Queuefy Active").classes("text-green-400")

            with ui.card().classes("flex-1 p-4"):
                ui.label("🔄 Prefect").classes("text-lg font-bold")
                ui.label("Connected").classes("text-blue-400")

        # Create task
        with ui.card().classes("w-full p-4 mt-4"):
            ui.label("🚀 Create Task").classes("text-lg font-bold mb-2")
            with ui.row().classes("w-full gap-2"):
                name_input = ui.input("Name", value="demo_task").classes("flex-1")
                priority = ui.select(["low", "medium", "high"], value="medium", label="Priority")
                create_btn = ui.button("Create")

            result = ui.label("").classes("mt-2 text-sm")

            async def on_create():
                try:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(
                            "http://localhost:8000/api/v1/tasks",
                            json={"name": name_input.value, "priority": priority.value},
                        )
                        if resp.status_code == 201:
                            data = resp.json()
                            result.text = f"✅ Created: {data['id'][:8]}..."
                        else:
                            result.text = f"❌ Error: {resp.text}"
                except Exception as e:
                    result.text = f"❌ {e}"

            create_btn.on_click(on_create)

        # Task list
        with ui.card().classes("w-full p-4 mt-4"):
            ui.label("📋 Recent Tasks").classes("text-lg font-bold mb-2")
            table = ui.table(
                columns=[
                    {"name": "id", "label": "ID", "field": "id"},
                    {"name": "name", "label": "Name", "field": "name"},
                    {"name": "status", "label": "Status", "field": "status"},
                    {"name": "priority", "label": "Priority", "field": "priority"},
                ],
                rows=[],
                row_key="id",
            ).classes("w-full")

        async def refresh():
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    resp = await client.get("http://localhost:8000/api/v1/tasks?limit=10")
                    if resp.status_code == 200:
                        tasks = resp.json()
                        table.rows = [
                            {"id": t["id"][:8], "name": t["name"], "status": t["status"], "priority": t["priority"]}
                            for t in tasks
                        ]
                        table.update()

                    stats_resp = await client.get("http://localhost:8000/api/v1/tasks/stats")
                    if stats_resp.status_code == 200:
                        s = stats_resp.json()
                        stats.text = f"Total: {s['total']} | Pending: {s['pending']} | Done: {s['completed']}"
            except Exception as e:
                stats.text = f"Error: {e}"

        ui.button("🔄 Refresh", on_click=refresh)
        await refresh()

    @ui.page(f"{prefix}/architecture")
    async def architecture():
        ui.dark_mode().enable()

        with ui.header().classes("bg-gray-900 text-white"):
            ui.label("🏗️ Architecture").classes("text-xl font-bold")
            ui.space()
            ui.link("← Dashboard", f"{prefix}/")

        with ui.column().classes("w-full p-4 gap-4"):
            ui.label("Simple Flat Architecture").classes("text-2xl font-bold")

            with ui.card().classes("w-full p-4"):
                ui.label("📁 Structure").classes("font-bold text-blue-400")
                ui.code("""
backend/src/app/
├── main.py          # Entry point + lifespan
├── config.py        # Settings (pydantic)
├── models.py        # Domain + DB models
├── services.py      # Business logic
├── routes.py        # FastAPI routes
├── ui.py            # NiceGUI pages
├── queue.py         # Queuefy integration
├── flows.py         # Prefect flows
└── database.py      # DB setup
                """).classes("w-full")

            with ui.card().classes("w-full p-4"):
                ui.label("🔄 Flow").classes("font-bold text-green-400")
                ui.label("HTTP → FastAPI → Service → DB/Queue → Worker → Result")
