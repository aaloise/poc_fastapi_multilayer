#!/usr/bin/env python3
"""
Dashboard de Testes — NiceGUI
==============================

Dashboard interativo que mostra o status de todos os testes
e permite executar testes individuais.

Uso:
    # Inicie a API primeiro
    uv run python -m app.main
    
    # Depois acesse: http://localhost:8000/ui/tests
"""

import asyncio
import time
from datetime import datetime
from typing import Any

import httpx
from nicegui import ui

BASE_URL = "http://localhost:8000/api/v1"


class TestDashboard:
    """Dashboard de testes interativo."""
    
    def __init__(self):
        self.results: dict[str, dict[str, Any]] = {}
        self.is_running = False
    
    async def run_test(self, test_name: str, test_func, status_label, result_area):
        """Executa um teste e atualiza a UI."""
        status_label.text = "⏳ Executando..."
        status_label.classes("text-yellow-500")
        result_area.clear()
        
        start = time.time()
        try:
            result = await test_func()
            duration = time.time() - start
            
            if result["success"]:
                status_label.text = "✓ Passou"
                status_label.classes("text-green-500", remove="text-yellow-500 text-red-500")
                result_area.push(f"✓ {result['message']}")
                if result.get("data"):
                    result_area.push(f"  Data: {result['data']}")
            else:
                status_label.text = "✗ Falhou"
                status_label.classes("text-red-500", remove="text-yellow-500 text-green-500")
                result_area.push(f"✗ {result['message']}")
            
            self.results[test_name] = {
                "success": result["success"],
                "duration": duration,
                "message": result["message"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            duration = time.time() - start
            status_label.text = "✗ Erro"
            status_label.classes("text-red-500", remove="text-yellow-500 text-green-500")
            result_area.push(f"✗ Erro: {str(e)}")
            
            self.results[test_name] = {
                "success": False,
                "duration": duration,
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_health(self, status_label, result_area):
        """Teste: Health Check."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": "API está saudável",
                    "data": data
                }
            else:
                return {
                    "success": False,
                    "message": f"Status code: {response.status_code}"
                }
    
    async def test_create_task(self, status_label, result_area):
        """Teste: Criar Task."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/tasks",
                json={
                    "name": "test_from_dashboard",
                    "payload": {"test": True},
                    "priority": "medium"
                }
            )
            if response.status_code == 201:
                data = response.json()
                return {
                    "success": True,
                    "message": "Task criada com sucesso",
                    "data": data
                }
            else:
                return {
                    "success": False,
                    "message": f"Status code: {response.status_code}"
                }
    
    async def test_list_tasks(self, status_label, result_area):
        """Teste: Listar Tasks."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/tasks")
            if response.status_code == 200:
                tasks = response.json()
                return {
                    "success": True,
                    "message": f"Encontradas {len(tasks)} tasks",
                    "data": {"count": len(tasks)}
                }
            else:
                return {
                    "success": False,
                    "message": f"Status code: {response.status_code}"
                }
    
    async def test_get_stats(self, status_label, result_area):
        """Teste: Estatísticas."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/tasks/stats")
            if response.status_code == 200:
                stats = response.json()
                return {
                    "success": True,
                    "message": "Estatísticas obtidas",
                    "data": stats
                }
            else:
                return {
                    "success": False,
                    "message": f"Status code: {response.status_code}"
                }
    
    async def run_all_tests(self, tests_ui):
        """Executa todos os testes."""
        if self.is_running:
            return
        
        self.is_running = True
        
        for test_name, test_ui in tests_ui.items():
            test_func = getattr(self, f"test_{test_name}")
            await self.run_test(
                test_name,
                test_func,
                test_ui["status"],
                test_ui["result"]
            )
        
        self.is_running = False


def setup_test_dashboard():
    """Configura o dashboard de testes."""
    
    dashboard = TestDashboard()
    
    @ui.page("/ui/tests")
    async def test_dashboard_page():
        """Página do dashboard de testes."""
        ui.dark_mode().enable()
        
        with ui.header().classes("bg-gray-900 text-white"):
            ui.label("🧪 Test Dashboard").classes("text-xl font-bold")
            ui.space()
            ui.link("← Voltar", "/ui/")
        
        with ui.column().classes("w-full p-4 gap-4"):
            # Título
            ui.label("Dashboard de Testes").classes("text-2xl font-bold")
            ui.label("Execute testes individuais ou todos de uma vez").classes("text-slate-400")
            
            # Botão para executar todos
            run_all_btn = ui.button("🚀 Executar Todos os Testes", on_click=lambda: dashboard.run_all_tests(tests_ui))
            
            ui.separator()
            
            # Tests
            tests_ui = {}
            
            # Test 1: Health Check
            with ui.card().classes("w-full p-4"):
                with ui.row().classes("w-full items-center"):
                    ui.label("🏥 Health Check").classes("text-lg font-bold flex-1")
                    status1 = ui.label("Aguardando...").classes("text-slate-400")
                
                result1 = ui.log(max_lines=10).classes("w-full h-24 mt-2")
                
                ui.button(
                    "Executar",
                    on_click=lambda: dashboard.run_test("health", dashboard.test_health, status1, result1)
                )
                
                tests_ui["health"] = {"status": status1, "result": result1}
            
            # Test 2: Create Task
            with ui.card().classes("w-full p-4"):
                with ui.row().classes("w-full items-center"):
                    ui.label("📝 Create Task").classes("text-lg font-bold flex-1")
                    status2 = ui.label("Aguardando...").classes("text-slate-400")
                
                result2 = ui.log(max_lines=10).classes("w-full h-24 mt-2")
                
                ui.button(
                    "Executar",
                    on_click=lambda: dashboard.run_test("create_task", dashboard.test_create_task, status2, result2)
                )
                
                tests_ui["create_task"] = {"status": status2, "result": result2}
            
            # Test 3: List Tasks
            with ui.card().classes("w-full p-4"):
                with ui.row().classes("w-full items-center"):
                    ui.label("📋 List Tasks").classes("text-lg font-bold flex-1")
                    status3 = ui.label("Aguardando...").classes("text-slate-400")
                
                result3 = ui.log(max_lines=10).classes("w-full h-24 mt-2")
                
                ui.button(
                    "Executar",
                    on_click=lambda: dashboard.run_test("list_tasks", dashboard.test_list_tasks, status3, result3)
                )
                
                tests_ui["list_tasks"] = {"status": status3, "result": result3}
            
            # Test 4: Get Stats
            with ui.card().classes("w-full p-4"):
                with ui.row().classes("w-full items-center"):
                    ui.label("📊 Get Stats").classes("text-lg font-bold flex-1")
                    status4 = ui.label("Aguardando...").classes("text-slate-400")
                
                result4 = ui.log(max_lines=10).classes("w-full h-24 mt-2")
                
                ui.button(
                    "Executar",
                    on_click=lambda: dashboard.run_test("get_stats", dashboard.test_get_stats, status4, result4)
                )
                
                tests_ui["get_stats"] = {"status": status4, "result": result4}
            
            ui.separator()
            
            # Resumo
            with ui.card().classes("w-full p-4"):
                ui.label("📈 Resumo").classes("text-lg font-bold mb-2")
                
                summary_table = ui.table(
                    columns=[
                        {"name": "test", "label": "Teste", "field": "test"},
                        {"name": "status", "label": "Status", "field": "status"},
                        {"name": "duration", "label": "Duração", "field": "duration"},
                        {"name": "timestamp", "label": "Timestamp", "field": "timestamp"},
                    ],
                    rows=[],
                    row_key="test",
                ).classes("w-full")
                
                async def update_summary():
                    rows = []
                    for test_name, result in dashboard.results.items():
                        rows.append({
                            "test": test_name,
                            "status": "✓" if result["success"] else "✗",
                            "duration": f"{result['duration']:.3f}s",
                            "timestamp": result["timestamp"][:19]
                        })
                    summary_table.rows = rows
                    summary_table.update()
                
                ui.button("Atualizar Resumo", on_click=update_summary)
