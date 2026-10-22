"""
Presentation Layer — NiceGUI Pages
====================================

Interactive web UI built with NiceGUI, mounted on the same FastAPI app.
"""

from __future__ import annotations

import asyncio
from datetime import datetime

from nicegui import ui


def setup_nicegui_pages(prefix: str = "/ui") -> None:
    """Register all NiceGUI pages."""

    @ui.page(f"{prefix}/")
    async def dashboard_page():
        """Main dashboard page."""
        ui.dark_mode().enable()

        with ui.header().classes("bg-gray-900 text-white"):
            ui.label("⚡ Async POC Dashboard").classes("text-xl font-bold")
            ui.space()
            ui.label(f"🕐 {datetime.utcnow().strftime('%H:%M:%S')}").classes("text-sm")

        with ui.row().classes("w-full gap-4 p-4"):
            # Stats cards
            with ui.card().classes("flex-1"):
                ui.label("📊 Tasks").classes("text-lg font-bold")
                stats_label = ui.label("Loading...")

            with ui.card().classes("flex-1"):
                ui.label("⚡ Queue").classes("text-lg font-bold")
                queue_label = ui.label("Active")

            with ui.card().classes("flex-1"):
                ui.label("🔄 Prefect").classes("text-lg font-bold")
                prefect_label = ui.label("Connected")

            with ui.card().classes("flex-1"):
                ui.label("🖥️ Server").classes("text-lg font-bold")
                server_label = ui.label("Granian + uvloop")

        # Task creation form
        with ui.card().classes("w-full p-4 mt-4"):
            ui.label("🚀 Create New Task").classes("text-lg font-bold mb-2")

            with ui.row().classes("w-full gap-2"):
                task_name = ui.input("Task Name", value="demo_task").classes("flex-1")
                priority_select = ui.select(
                    ["low", "medium", "high", "critical"],
                    value="medium",
                    label="Priority",
                )
                create_btn = ui.button("Create", on_click=lambda: create_task_action(
                    task_name.value, priority_select.value, result_label
                ))

            result_label = ui.label("").classes("mt-2 text-sm")

        # Task list
        with ui.card().classes("w-full p-4 mt-4"):
            ui.label("📋 Recent Tasks").classes("text-lg font-bold mb-2")
            task_table = ui.table(
                columns=[
                    {"name": "id", "label": "ID", "field": "id", "align": "left"},
                    {"name": "name", "label": "Name", "field": "name", "align": "left"},
                    {"name": "status", "label": "Status", "field": "status", "align": "left"},
                    {"name": "priority", "label": "Priority", "field": "priority", "align": "left"},
                    {"name": "created", "label": "Created", "field": "created_at", "align": "left"},
                ],
                rows=[],
                row_key="id",
            ).classes("w-full")

        # Refresh button
        with ui.row().classes("mt-4"):
            ui.button("🔄 Refresh", on_click=lambda: refresh_tasks(task_table, stats_label))
            ui.button("▶️ Run Pipeline", on_click=lambda: run_pipeline_action(result_label))

        # Initial load
        await refresh_tasks(task_table, stats_label)

    @ui.page(f"{prefix}/architecture")
    async def architecture_page():
        """Architecture overview page."""
        ui.dark_mode().enable()

        with ui.header().classes("bg-gray-900 text-white"):
            ui.label("🏗️ Architecture").classes("text-xl font-bold")
            ui.space()
            ui.link("← Dashboard", f"{prefix}/")

        with ui.column().classes("w-full p-4 gap-4"):
            ui.label("Layered Architecture").classes("text-2xl font-bold")

            with ui.card().classes("w-full p-4"):
                ui.label("📡 Presentation Layer").classes("text-lg font-bold text-blue-400")
                ui.label("FastAPI REST API + NiceGUI Interactive UI")
                ui.label("• /api/v1/* — REST endpoints").classes("ml-4")
                ui.label("• /ui/* — NiceGUI pages").classes("ml-4")

            with ui.card().classes("w-full p-4"):
                ui.label("⚙️ Application Layer").classes("text-lg font-bold text-green-400")
                ui.label("Use Cases & Orchestrators")
                ui.label("• TaskService — create, execute, list tasks").classes("ml-4")
                ui.label("• Coordinates domain logic with infrastructure").classes("ml-4")

            with ui.card().classes("w-full p-4"):
                ui.label("🧱 Domain Layer").classes("text-lg font-bold text-yellow-400")
                ui.label("Entities, Value Objects & Repository Ports")
                ui.label("• Task, TaskResult, TaskStatus").classes("ml-4")
                ui.label("• TaskRepository (Protocol)").classes("ml-4")
                ui.label("• ZERO infrastructure dependencies").classes("ml-4")

            with ui.card().classes("w-full p-4"):
                ui.label("🔧 Infrastructure Layer").classes("text-lg font-bold text-purple-400")
                ui.label("Adapters & External Integrations")
                ui.label("• SQLAlchemyTaskRepository — async DB").classes("ml-4")
                ui.label("• QueueManager — Queuefy integration").classes("ml-4")
                ui.label("• Prefect Flows — workflow orchestration").classes("ml-4")

            ui.label("Server Stack").classes("text-2xl font-bold mt-4")

            with ui.row().classes("w-full gap-4"):
                with ui.card().classes("flex-1 p-4"):
                    ui.label("🦀 Granian").classes("font-bold text-orange-400")
                    ui.label("Rust-based ASGI server")
                    ui.label("HTTP/1, HTTP/2, WebSocket")

                with ui.card().classes("flex-1 p-4"):
                    ui.label("🔄 uvloop").classes("font-bold text-cyan-400")
                    ui.label("Fast asyncio event loop")
                    ui.label("Drop-in replacement")

                with ui.card().classes("flex-1 p-4"):
                    ui.label("📊 Queuefy").classes("font-bold text-emerald-400")
                    ui.label("Async task queue")
                    ui.label("No broker, pure asyncio")

    @ui.page(f"{prefix}/monitor")
    async def monitor_page():
        """Real-time monitoring page."""
        ui.dark_mode().enable()

        with ui.header().classes("bg-gray-900 text-white"):
            ui.label("📈 Monitor").classes("text-xl font-bold")
            ui.space()
            ui.link("← Dashboard", f"{prefix}/")

        with ui.column().classes("w-full p-4 gap-4"):
            ui.label("System Monitor").classes("text-2xl font-bold")

            with ui.row().classes("w-full gap-4"):
                # System metrics
                with ui.card().classes("flex-1 p-4"):
                    ui.label("🖥️ System").classes("font-bold")
                    cpu_chart = ui.chart({
                        'title': False,
                        'series': [{'name': 'CPU', 'data': [30, 45, 28, 52, 38, 41, 55]}],
                        'chart': {'type': 'line', 'height': 200},
                        'xaxis': {'categories': ['1m', '2m', '3m', '4m', '5m', '6m', '7m']},
                    }).classes("w-full")

                with ui.card().classes("flex-1 p-4"):
                    ui.label("📊 Queue Depth").classes("font-bold")
                    queue_chart = ui.chart({
                        'title': False,
                        'series': [{'name': 'Tasks', 'data': [5, 12, 8, 3, 15, 7, 2]}],
                        'chart': {'type': 'bar', 'height': 200},
                        'xaxis': {'categories': ['default', 'priority', 'reports', 'notify', 'batch', 'cleanup', 'other']},
                    }).classes("w-full")

            with ui.card().classes("w-full p-4"):
                ui.label("📝 Event Log").classes("font-bold mb-2")
                log_area = ui.log(max_lines=20).classes("w-full h-48")
                log_area.push("System started — Granian + uvloop")
                log_area.push("Queuefy worker initialized (concurrency=8)")
                log_area.push("Database connected (SQLite async)")
                log_area.push("NiceGUI mounted at /ui/")
                log_area.push("Prefect flows registered")


# ── Helper actions ───────────────────────────────────────────────────

async def create_task_action(name: str, priority: str, label) -> None:
    """Create a task via the API."""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "http://localhost:8000/api/v1/tasks",
                json={"name": name, "priority": priority},
            )
            if resp.status_code == 201:
                data = resp.json()
                label.text = f"✅ Task created: {data['id'][:8]}..."
            else:
                label.text = f"❌ Error: {resp.text}"
    except Exception as e:
        label.text = f"❌ Connection error: {e}"


async def refresh_tasks(table, stats_label) -> None:
    """Refresh the task list from the API."""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            # Get tasks
            resp = await client.get("http://localhost:8000/api/v1/tasks?limit=10")
            if resp.status_code == 200:
                tasks = resp.json()
                table.rows = [
                    {
                        "id": t["id"][:8] + "...",
                        "name": t["name"],
                        "status": t["status"],
                        "priority": t["priority"],
                        "created_at": t["created_at"][:19],
                    }
                    for t in tasks
                ]
                table.update()

            # Get stats
            stats_resp = await client.get("http://localhost:8000/api/v1/tasks/stats")
            if stats_resp.status_code == 200:
                stats = stats_resp.json()
                stats_label.text = f"Total: {stats['total']} | Pending: {stats['pending']} | Running: {stats['running']}"
    except Exception as e:
        stats_label.text = f"Error: {e}"


async def run_pipeline_action(label) -> None:
    """Trigger the data pipeline flow."""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://localhost:8000/api/v1/flows/data-pipeline")
            if resp.status_code == 200:
                label.text = f"✅ Pipeline completed: {resp.json()}"
            else:
                label.text = f"❌ Pipeline error: {resp.status_code}"
    except Exception as e:
        label.text = f"❌ Error: {e}"
