#!/usr/bin/env python3
"""
Script de Desenvolvimento — Facilita o dia-a-dia
=================================================

Comandos úteis para desenvolvimento.

Uso:
    uv run python scripts/dev.py <comando>

Comandos:
    start       — Inicia a API em modo desenvolvimento
    seed        — Popula banco com dados de exemplo
    test        — Executa testes interativos
    benchmark   — Executa benchmark de performance
    reset       — Reseta banco de dados
    logs        — Mostra logs do banco
    shell       — Abre shell Python com contexto
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()


def cmd_start():
    """Inicia a API em modo desenvolvimento."""
    console.print(Panel("[bold cyan]🚀 Iniciando API (DEV)[/bold cyan]", expand=False))
    console.print("[dim]Ambiente: development[/dim]")
    console.print("[dim]Database: SQLite (dev_poc.db)[/dim]")
    console.print()
    
    os.environ["POC_ENV"] = "development"
    
    # Inicia a API
    subprocess.run([
        sys.executable, "-m", "app.main"
    ])


def cmd_seed():
    """Popula banco com dados de exemplo."""
    console.print(Panel("[bold cyan]🌱 Populando banco[/bold cyan]", expand=False))
    
    env = os.getenv("POC_ENV", "development")
    console.print(f"[dim]Ambiente: {env}[/dim]")
    console.print()
    
    subprocess.run([
        sys.executable, "scripts/seed_data.py"
    ])


def cmd_test():
    """Executa testes interativos."""
    console.print(Panel("[bold cyan]🧪 Executando testes[/bold cyan]", expand=False))
    console.print()
    
    subprocess.run([
        sys.executable, "scripts/test_interactive.py"
    ])


def cmd_benchmark():
    """Executa benchmark de performance."""
    console.print(Panel("[bold cyan]⚡ Executando benchmark[/bold cyan]", expand=False))
    console.print()
    
    subprocess.run([
        sys.executable, "scripts/benchmark.py",
        "--requests", "10"
    ])


def cmd_reset():
    """Reseta banco de dados."""
    console.print(Panel("[bold yellow]⚠️  Resetando banco[/bold yellow]", expand=False))
    
    env = os.getenv("POC_ENV", "development")
    console.print(f"[dim]Ambiente: {env}[/dim]")
    
    if env == "development":
        db_file = Path("dev_poc.db")
        if db_file.exists():
            db_file.unlink()
            console.print(f"[green]✓[/green] {db_file} removido")
        else:
            console.print("[yellow]⚠️[/yellow] Arquivo não encontrado")
    elif env == "production":
        console.print("[red]✗[/red] Não é possível resetar banco de produção")
        console.print("[dim]Use: docker exec -it poc-postgres psql -U poc -d poc_prod -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'[/dim]")
        return
    else:
        console.print("[yellow]⚠️[/yellow] Ambiente de teste usa banco em memória")
    
    console.print()
    console.print("[bold]Próximos passos:[/bold]")
    console.print("  1. Popule o banco: [cyan]uv run python scripts/dev.py seed[/cyan]")
    console.print("  2. Inicie a API: [cyan]uv run python scripts/dev.py start[/cyan]")


def cmd_logs():
    """Mostra logs do banco."""
    console.print(Panel("[bold cyan]📊 Logs do banco[/bold cyan]", expand=False))
    
    env = os.getenv("POC_ENV", "development")
    
    if env == "development":
        db_file = Path("dev_poc.db")
        if not db_file.exists():
            console.print("[red]✗[/red] Banco não encontrado. Execute seed primeiro.")
            return
        
        console.print(f"[dim]Database: {db_file}[/dim]")
        console.print()
        
        # Usa sqlite3 para mostrar stats
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            
            # Tasks por status
            console.print("[bold]Tasks por status:[/bold]")
            cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
            for row in cursor.fetchall():
                console.print(f"  {row[0]}: {row[1]}")
            
            console.print()
            
            # Queuefy runs
            console.print("[bold]Queuefy runs:[/bold]")
            cursor.execute("SELECT COUNT(*) FROM queuefy_runs")
            count = cursor.fetchone()[0]
            console.print(f"  Total: {count}")
            
            cursor.execute("SELECT status, COUNT(*) FROM queuefy_runs GROUP BY status")
            for row in cursor.fetchall():
                console.print(f"  {row[0]}: {row[1]}")
            
            conn.close()
            
        except Exception as e:
            console.print(f"[red]✗[/red] Erro: {e}")
    
    elif env == "production":
        console.print("[dim]Usando PostgreSQL[/dim]")
        console.print()
        console.print("[bold]Comandos úteis:[/bold]")
        console.print("  [cyan]docker exec -it poc-postgres psql -U poc -d poc_prod[/cyan]")
        console.print("  [cyan]SELECT status, COUNT(*) FROM tasks GROUP BY status;[/cyan]")


def cmd_shell():
    """Abre shell Python com contexto."""
    console.print(Panel("[bold cyan]🐍 Shell Python[/bold cyan]", expand=False))
    console.print("[dim]Contexto carregado: models, services, database[/dim]")
    console.print()
    
    # Prepara contexto
    code = """
import asyncio
from app.database import init_db, get_session, close_db
from app.models import Task, TaskStatus, Priority, save_task, get_task, list_tasks
from app.services import create_task, execute_task, get_task_by_id, get_all_tasks, get_stats
from app.config import get_settings

settings = get_settings()
print(f"Ambiente: {settings.environment}")
print(f"Database: {settings.db_url}")
print()
print("Funções disponíveis:")
print("  - create_task(name, payload, priority)")
print("  - execute_task(task_id)")
print("  - get_task_by_id(task_id)")
print("  - get_all_tasks(status, limit)")
print("  - get_stats()")
print()
print("Exemplo:")
print("  task = await create_task('test', {'foo': 'bar'})")
"""
    
    # Inicia IPython ou Python
    try:
        from IPython import embed
        embed(colors="neutral", banner1=code)
    except ImportError:
        import code as code_module
        code_module.interact(banner=code)


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Script de desenvolvimento",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Comandos:
  start       Inicia a API em modo desenvolvimento
  seed        Popula banco com dados de exemplo
  test        Executa testes interativos
  benchmark   Executa benchmark de performance
  reset       Reseta banco de dados
  logs        Mostra logs do banco
  shell       Abre shell Python com contexto

Exemplos:
  uv run python scripts/dev.py start
  uv run python scripts/dev.py seed
  uv run python scripts/dev.py test
  POC_ENV=production uv run python scripts/dev.py logs
        """
    )
    
    parser.add_argument(
        "command",
        choices=["start", "seed", "test", "benchmark", "reset", "logs", "shell"],
        help="Comando a executar"
    )
    
    args = parser.parse_args()
    
    # Executa comando
    commands = {
        "start": cmd_start,
        "seed": cmd_seed,
        "test": cmd_test,
        "benchmark": cmd_benchmark,
        "reset": cmd_reset,
        "logs": cmd_logs,
        "shell": cmd_shell,
    }
    
    commands[args.command]()


if __name__ == "__main__":
    main()
