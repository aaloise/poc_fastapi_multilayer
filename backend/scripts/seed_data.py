#!/usr/bin/env python3
"""
Script de Seed — Popula o banco com dados de exemplo
=====================================================

Cria tasks de exemplo para demonstrar todas as funcionalidades.

Uso:
    uv run python scripts/seed_data.py
    # ou com ambiente específico
    POC_ENV=production uv run python scripts/seed_data.py
"""

import sys
from pathlib import Path

# Adiciona o diretório src ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import asyncio
import random
import uuid
from datetime import datetime, timedelta

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

console = Console()


async def seed_database():
    """Popula o banco com dados de exemplo."""
    from app.database import init_db, get_session, close_db
    from app.models import Task, TaskStatus, Priority, save_task
    from app.config import get_settings
    
    settings = get_settings()
    
    console.print()
    console.print(Panel(
        f"[bold cyan]🌱 Seed Data — {settings.environment.upper()}[/bold cyan]\n"
        f"[dim]Database: {settings.db_url}[/dim]",
        expand=False
    ))
    console.print()
    
    # Inicializa banco
    console.print("[bold]Inicializando banco de dados...[/bold]")
    await init_db(settings.db_url)
    console.print("[green]✓[/green] Banco inicializado")
    
    # Dados de exemplo
    tasks_data = [
        # Tasks pendentes
        {"name": "send_welcome_email", "payload": {"to": "user1@example.com"}, "priority": Priority.HIGH},
        {"name": "process_image", "payload": {"file": "photo.jpg"}, "priority": Priority.MEDIUM},
        {"name": "generate_report", "payload": {"type": "monthly"}, "priority": Priority.LOW},
        
        # Tasks em execução
        {"name": "sync_data", "payload": {"source": "api"}, "priority": Priority.HIGH, "status": TaskStatus.RUNNING},
        {"name": "backup_database", "payload": {"full": True}, "priority": Priority.CRITICAL, "status": TaskStatus.RUNNING},
        
        # Tasks completadas
        {"name": "send_notification", "payload": {"msg": "Hello"}, "priority": Priority.MEDIUM, "status": TaskStatus.COMPLETED},
        {"name": "cleanup_temp", "payload": {"older_than": "7d"}, "priority": Priority.LOW, "status": TaskStatus.COMPLETED},
        {"name": "validate_data", "payload": {"schema": "v2"}, "priority": Priority.MEDIUM, "status": TaskStatus.COMPLETED},
        
        # Tasks falhadas
        {"name": "external_api_call", "payload": {"url": "https://api.example.com"}, "priority": Priority.HIGH, "status": TaskStatus.FAILED, "error": "Connection timeout"},
        {"name": "parse_file", "payload": {"file": "data.csv"}, "priority": Priority.MEDIUM, "status": TaskStatus.FAILED, "error": "Invalid format"},
    ]
    
    console.print(f"\n[bold]Criando {len(tasks_data)} tasks de exemplo...[/bold]")
    
    created_tasks = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Criando tasks...", total=len(tasks_data))
        
        session = await get_session()
        async with session:
            for i, data in enumerate(tasks_data, 1):
                # Cria task
                task_obj = Task(
                    name=data["name"],
                    payload=data.get("payload", {}),
                    priority=data.get("priority", Priority.MEDIUM),
                    status=data.get("status", TaskStatus.PENDING),
                    error=data.get("error"),
                )
                
                # Adiciona timestamps
                if task_obj.status == TaskStatus.RUNNING:
                    task_obj.started_at = datetime.utcnow() - timedelta(minutes=random.randint(1, 30))
                
                if task_obj.status == TaskStatus.COMPLETED:
                    task_obj.started_at = datetime.utcnow() - timedelta(minutes=random.randint(10, 60))
                    task_obj.completed_at = task_obj.started_at + timedelta(seconds=random.randint(1, 30))
                
                if task_obj.status == TaskStatus.FAILED:
                    task_obj.started_at = datetime.utcnow() - timedelta(minutes=random.randint(5, 30))
                    task_obj.completed_at = task_obj.started_at + timedelta(seconds=random.randint(1, 10))
                    task_obj.attempts = random.randint(1, 3)
                
                # Salva
                saved = await save_task(session, task_obj)
                created_tasks.append(saved)
                
                progress.advance(task)
    
    console.print(f"[green]✓[/green] {len(created_tasks)} tasks criadas")
    
    # Mostra resumo
    console.print()
    console.print("[bold]Resumo:[/bold]")
    
    from rich.table import Table
    
    table = Table(title="Tasks Criadas")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Priority", style="yellow")
    table.add_column("ID", style="dim")
    
    for task in created_tasks:
        table.add_row(
            task.name,
            task.status,
            task.priority,
            str(task.id)[:8] + "..."
        )
    
    console.print(table)
    
    # Fecha banco
    await close_db()
    
    console.print()
    console.print("[bold green]🎉 Seed concluído![/bold green]")
    console.print()
    console.print("[bold]Próximos passos:[/bold]")
    console.print("  1. Inicie a API: [cyan]uv run python -m app.main[/cyan]")
    console.print("  2. Acesse o dashboard: [cyan]http://localhost:8000/ui/[/cyan]")
    console.print("  3. Execute os testes: [cyan]uv run python scripts/test_interactive.py[/cyan]")
    console.print()


if __name__ == "__main__":
    asyncio.run(seed_database())
