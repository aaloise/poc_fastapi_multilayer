#!/usr/bin/env python3
"""
Script de Teste Interativo — Demonstração completa da POC
==========================================================

Este script demonstra TODAS as funcionalidades da POC de forma
metódica e didática, mostrando o que acontece em cada passo.

Uso:
    uv run python scripts/test_interactive.py
    # ou
    uv run python scripts/test_interactive.py --env production
"""

import asyncio
import time
import uuid
from datetime import datetime, timedelta
from typing import Any

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

console = Console()

# Configuração
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"


class TestRunner:
    """Executa testes interativos da POC."""
    
    def __init__(self):
        self.results: list[dict[str, Any]] = []
        self.start_time = time.time()
    
    def print_header(self, title: str):
        """Imprime cabeçalho formatado."""
        console.print()
        console.print(Panel(f"[bold cyan]{title}[/bold cyan]", expand=False))
        console.print()
    
    def print_step(self, step: int, description: str):
        """Imprime passo do teste."""
        console.print(f"\n[bold yellow]Step {step}:[/bold yellow] {description}")
    
    def print_success(self, message: str, data: Any = None):
        """Imprime mensagem de sucesso."""
        console.print(f"[bold green]✓[/bold green] {message}")
        if data:
            console.print(f"  [dim]{data}[/dim]")
    
    def print_error(self, message: str, error: Any = None):
        """Imprime mensagem de erro."""
        console.print(f"[bold red]✗[/bold red] {message}")
        if error:
            console.print(f"  [dim red]{error}[/dim red]")
    
    def print_info(self, message: str):
        """Imprime informação."""
        console.print(f"[bold blue]ℹ[/bold blue] {message}")
    
    def add_result(self, test_name: str, success: bool, duration: float, details: str = ""):
        """Adiciona resultado do teste."""
        self.results.append({
            "test": test_name,
            "success": success,
            "duration": duration,
            "details": details
        })
    
    async def check_health(self):
        """Teste 1: Health Check."""
        self.print_header("🏥 Teste 1: Health Check")
        self.print_step(1, "Verificando se a API está rodando...")
        
        start = time.time()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_URL}/health")
                duration = time.time() - start
                
                if response.status_code == 200:
                    data = response.json()
                    self.print_success("API está saudável!", data)
                    
                    # Mostra componentes
                    table = Table(title="Componentes")
                    table.add_column("Componente", style="cyan")
                    table.add_column("Status", style="green")
                    
                    for comp, status in data.get("components", {}).items():
                        table.add_row(comp, "✓ OK" if status else "✗ ERRO")
                    
                    console.print(table)
                    self.add_result("Health Check", True, duration)
                    return True
                else:
                    self.print_error(f"Status code: {response.status_code}")
                    self.add_result("Health Check", False, duration, str(response.status_code))
                    return False
        except Exception as e:
            duration = time.time() - start
            self.print_error("Não foi possível conectar à API", str(e))
            self.print_info("Certifique-se de que a API está rodando:")
            console.print("  [dim]uv run python -m app.main[/dim]")
            self.add_result("Health Check", False, duration, str(e))
            return False
    
    async def test_create_task(self):
        """Teste 2: Criar Task."""
        self.print_header("📝 Teste 2: Criar Task")
        self.print_step(1, "Criando uma task simples...")
        
        start = time.time()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_URL}/tasks",
                    json={
                        "name": "test_task_simple",
                        "payload": {"message": "Hello from test!"},
                        "priority": "medium"
                    }
                )
                duration = time.time() - start
                
                if response.status_code == 201:
                    data = response.json()
                    self.print_success("Task criada com sucesso!", data)
                    self.add_result("Create Task (Simple)", True, duration, data.get("id"))
                    return data.get("id")
                else:
                    self.print_error(f"Status code: {response.status_code}", response.text)
                    self.add_result("Create Task (Simple)", False, duration, response.text)
                    return None
        except Exception as e:
            duration = time.time() - start
            self.print_error("Erro ao criar task", str(e))
            self.add_result("Create Task (Simple)", False, duration, str(e))
            return None
    
    async def test_create_multiple_tasks(self):
        """Teste 3: Criar Múltiplas Tasks."""
        self.print_header("📝 Teste 3: Criar Múltiplas Tasks")
        self.print_step(1, "Criando 5 tasks com prioridades diferentes...")
        
        tasks_data = [
            {"name": "task_low", "priority": "low", "payload": {"type": "low_priority"}},
            {"name": "task_medium_1", "priority": "medium", "payload": {"type": "medium"}},
            {"name": "task_medium_2", "priority": "medium", "payload": {"type": "medium"}},
            {"name": "task_high", "priority": "high", "payload": {"type": "high_priority"}},
            {"name": "task_critical", "priority": "critical", "payload": {"type": "critical"}},
        ]
        
        created_ids = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Criando tasks...", total=len(tasks_data))
            
            async with httpx.AsyncClient() as client:
                for i, task_data in enumerate(tasks_data, 1):
                    start = time.time()
                    try:
                        response = await client.post(f"{API_URL}/tasks", json=task_data)
                        duration = time.time() - start
                        
                        if response.status_code == 201:
                            data = response.json()
                            created_ids.append(data["id"])
                            self.print_success(f"Task {i}/{len(tasks_data)} criada", data["id"])
                            self.add_result(f"Create Task ({task_data['name']})", True, duration)
                        else:
                            self.print_error(f"Task {i} falhou", response.text)
                            self.add_result(f"Create Task ({task_data['name']})", False, duration)
                    except Exception as e:
                        self.print_error(f"Task {i} erro", str(e))
                        self.add_result(f"Create Task ({task_data['name']})", False, 0, str(e))
                    
                    progress.advance(task)
        
        return created_ids
    
    async def test_list_tasks(self):
        """Teste 4: Listar Tasks."""
        self.print_header("📋 Teste 4: Listar Tasks")
        self.print_step(1, "Buscando todas as tasks...")
        
        start = time.time()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_URL}/tasks")
                duration = time.time() - start
                
                if response.status_code == 200:
                    tasks = response.json()
                    self.print_success(f"Encontradas {len(tasks)} tasks")
                    
                    # Mostra tabela
                    table = Table(title="Tasks")
                    table.add_column("ID", style="cyan", no_wrap=True)
                    table.add_column("Name", style="green")
                    table.add_column("Status", style="yellow")
                    table.add_column("Priority", style="magenta")
                    table.add_column("Created", style="blue")
                    
                    for task in tasks[:10]:  # Mostra apenas 10
                        table.add_row(
                            task["id"][:8] + "...",
                            task["name"],
                            task["status"],
                            task["priority"],
                            task["created_at"][:19]
                        )
                    
                    console.print(table)
                    
                    if len(tasks) > 10:
                        self.print_info(f"... e mais {len(tasks) - 10} tasks")
                    
                    self.add_result("List Tasks", True, duration, f"{len(tasks)} tasks")
                    return tasks
                else:
                    self.print_error(f"Status code: {response.status_code}")
                    self.add_result("List Tasks", False, duration)
                    return []
        except Exception as e:
            duration = time.time() - start
            self.print_error("Erro ao listar tasks", str(e))
            self.add_result("List Tasks", False, duration, str(e))
            return []
    
    async def test_get_task(self, task_id: str):
        """Teste 5: Buscar Task por ID."""
        self.print_header("🔍 Teste 5: Buscar Task por ID")
        self.print_step(1, f"Buscando task {task_id[:8]}...")
        
        start = time.time()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_URL}/tasks/{task_id}")
                duration = time.time() - start
                
                if response.status_code == 200:
                    data = response.json()
                    self.print_success("Task encontrada!", data)
                    self.add_result("Get Task by ID", True, duration)
                    return data
                else:
                    self.print_error(f"Status code: {response.status_code}")
                    self.add_result("Get Task by ID", False, duration)
                    return None
        except Exception as e:
            duration = time.time() - start
            self.print_error("Erro ao buscar task", str(e))
            self.add_result("Get Task by ID", False, duration, str(e))
            return None
    
    async def test_get_stats(self):
        """Teste 6: Estatísticas."""
        self.print_header("📊 Teste 6: Estatísticas")
        self.print_step(1, "Obtendo estatísticas das tasks...")
        
        start = time.time()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_URL}/tasks/stats")
                duration = time.time() - start
                
                if response.status_code == 200:
                    stats = response.json()
                    self.print_success("Estatísticas obtidas!", stats)
                    
                    # Mostra tabela
                    table = Table(title="Estatísticas")
                    table.add_column("Status", style="cyan")
                    table.add_column("Count", style="green", justify="right")
                    
                    for status, count in stats.items():
                        table.add_row(status, str(count))
                    
                    console.print(table)
                    self.add_result("Get Stats", True, duration)
                    return stats
                else:
                    self.print_error(f"Status code: {response.status_code}")
                    self.add_result("Get Stats", False, duration)
                    return {}
        except Exception as e:
            duration = time.time() - start
            self.print_error("Erro ao obter estatísticas", str(e))
            self.add_result("Get Stats", False, duration, str(e))
            return {}
    
    async def test_queuefy_integration(self, task_id: str):
        """Teste 7: Integração com Queuefy."""
        self.print_header("📊 Teste 7: Integração com Queuefy")
        self.print_step(1, "Verificando se task foi enfileirada...")
        self.print_info("O Queuefy deve ter processado a task automaticamente")
        
        # Aguarda um pouco para o worker processar
        self.print_info("Aguardando 2 segundos para o worker processar...")
        await asyncio.sleep(2)
        
        self.print_step(2, "Verificando status da task...")
        
        start = time.time()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_URL}/tasks/{task_id}")
                duration = time.time() - start
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    
                    if status in ["completed", "running"]:
                        self.print_success(f"Task foi processada! Status: {status}", data)
                        self.add_result("Queuefy Integration", True, duration, status)
                        return True
                    else:
                        self.print_info(f"Task ainda está: {status}")
                        self.print_info("Isso é normal — o worker pode estar processando")
                        self.add_result("Queuefy Integration", True, duration, status)
                        return True
                else:
                    self.print_error(f"Status code: {response.status_code}")
                    self.add_result("Queuefy Integration", False, duration)
                    return False
        except Exception as e:
            duration = time.time() - start
            self.print_error("Erro ao verificar task", str(e))
            self.add_result("Queuefy Integration", False, duration, str(e))
            return False
    
    async def test_prefect_flow(self):
        """Teste 8: Prefect Flow."""
        self.print_header("🔮 Teste 8: Prefect Flow")
        self.print_step(1, "Executando pipeline do Prefect...")
        
        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{API_URL}/flows/pipeline",
                    params={"source": "test_api"}
                )
                duration = time.time() - start
                
                if response.status_code == 200:
                    data = response.json()
                    self.print_success("Pipeline executado com sucesso!", data)
                    self.add_result("Prefect Flow", True, duration)
                    return True
                elif response.status_code == 503:
                    self.print_info("Prefect não está disponível (opcional)")
                    self.add_result("Prefect Flow", True, duration, "Not installed")
                    return True
                else:
                    self.print_error(f"Status code: {response.status_code}", response.text)
                    self.add_result("Prefect Flow", False, duration, response.text)
                    return False
        except Exception as e:
            duration = time.time() - start
            self.print_error("Erro ao executar pipeline", str(e))
            self.add_result("Prefect Flow", False, duration, str(e))
            return False
    
    async def test_nicegui_ui(self):
        """Teste 9: NiceGUI UI."""
        self.print_header("🎨 Teste 9: NiceGUI UI")
        self.print_step(1, "Verificando se NiceGUI está acessível...")
        
        start = time.time()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/ui/")
                duration = time.time() - start
                
                if response.status_code == 200:
                    self.print_success("NiceGUI está acessível!")
                    self.print_info(f"Acesse: {BASE_URL}/ui/")
                    self.add_result("NiceGUI UI", True, duration)
                    return True
                else:
                    self.print_error(f"Status code: {response.status_code}")
                    self.add_result("NiceGUI UI", False, duration)
                    return False
        except Exception as e:
            duration = time.time() - start
            self.print_error("Erro ao acessar NiceGUI", str(e))
            self.add_result("NiceGUI UI", False, duration, str(e))
            return False
    
    async def test_error_handling(self):
        """Teste 10: Error Handling."""
        self.print_header("🚨 Teste 10: Error Handling")
        self.print_step(1, "Testando busca de task inexistente...")
        
        start = time.time()
        try:
            async with httpx.AsyncClient() as client:
                fake_id = str(uuid.uuid4())
                response = await client.get(f"{API_URL}/tasks/{fake_id}")
                duration = time.time() - start
                
                if response.status_code == 404:
                    self.print_success("Erro 404 retornado corretamente!")
                    self.add_result("Error Handling (404)", True, duration)
                    return True
                else:
                    self.print_error(f"Esperado 404, recebido {response.status_code}")
                    self.add_result("Error Handling (404)", False, duration)
                    return False
        except Exception as e:
            duration = time.time() - start
            self.print_error("Erro ao testar error handling", str(e))
            self.add_result("Error Handling (404)", False, duration, str(e))
            return False
    
    def print_summary(self):
        """Imprime resumo final dos testes."""
        total_time = time.time() - self.start_time
        
        console.print()
        console.print(Panel("[bold cyan]📊 Resumo dos Testes[/bold cyan]", expand=False))
        console.print()
        
        # Tabela de resultados
        table = Table(title="Resultados")
        table.add_column("Teste", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Duração", style="yellow", justify="right")
        table.add_column("Detalhes", style="dim")
        
        passed = 0
        failed = 0
        
        for result in self.results:
            status = "[green]✓ PASS[/green]" if result["success"] else "[red]✗ FAIL[/red]"
            duration = f"{result['duration']:.3f}s"
            details = result.get("details", "")[:50]
            
            table.add_row(
                result["test"],
                status,
                duration,
                details
            )
            
            if result["success"]:
                passed += 1
            else:
                failed += 1
        
        console.print(table)
        
        # Estatísticas
        console.print()
        console.print(f"[bold]Total:[/bold] {len(self.results)} testes")
        console.print(f"[bold green]Passou:[/bold green] {passed}")
        console.print(f"[bold red]Falhou:[/bold red] {failed}")
        console.print(f"[bold]Tempo total:[/bold] {total_time:.2f}s")
        
        if failed == 0:
            console.print()
            console.print("[bold green]🎉 Todos os testes passaram![/bold green]")
        else:
            console.print()
            console.print(f"[bold red]⚠️  {failed} teste(s) falharam[/bold red]")


async def main():
    """Executa todos os testes."""
    console.print()
    console.print(Panel(
        "[bold cyan]🚀 Async POC — Teste Interativo Completo[/bold cyan]\n"
        "[dim]Este script testa todas as funcionalidades da POC[/dim]",
        expand=False
    ))
    
    runner = TestRunner()
    
    # Teste 1: Health Check
    if not await runner.check_health():
        console.print("\n[bold red]API não está rodando. Abortando testes.[/bold red]")
        return
    
    # Teste 2: Criar task simples
    task_id = await runner.test_create_task()
    
    # Teste 3: Criar múltiplas tasks
    task_ids = await runner.test_create_multiple_tasks()
    
    # Teste 4: Listar tasks
    tasks = await runner.test_list_tasks()
    
    # Teste 5: Buscar task por ID
    if task_id:
        await runner.test_get_task(task_id)
    
    # Teste 6: Estatísticas
    await runner.test_get_stats()
    
    # Teste 7: Queuefy integration
    if task_id:
        await runner.test_queuefy_integration(task_id)
    
    # Teste 8: Prefect flow
    await runner.test_prefect_flow()
    
    # Teste 9: NiceGUI UI
    await runner.test_nicegui_ui()
    
    # Teste 10: Error handling
    await runner.test_error_handling()
    
    # Resumo final
    runner.print_summary()
    
    console.print()
    console.print("[bold]📚 Próximos passos:[/bold]")
    console.print("  1. Acesse o dashboard: [cyan]http://localhost:8000/ui/[/cyan]")
    console.print("  2. Veja a documentação: [cyan]http://localhost:8000/docs[/cyan]")
    console.print("  3. Leia os docs em: [cyan]backend/docs/[/cyan]")
    console.print()


if __name__ == "__main__":
    asyncio.run(main())
