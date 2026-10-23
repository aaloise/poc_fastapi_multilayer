#!/usr/bin/env python3
"""
Script de Benchmark — Mede performance da API
==============================================

Testa performance de diferentes operações.

Uso:
    uv run python scripts/benchmark.py
    # ou com mais requests
    uv run python scripts/benchmark.py --requests 100
"""

import sys
from pathlib import Path

# Adiciona o diretório src ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import asyncio
import time
import statistics
from typing import Callable, Awaitable

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()

BASE_URL = "http://localhost:8000/api/v1"


class Benchmark:
    """Executa benchmarks da API."""
    
    def __init__(self):
        self.results: dict[str, list[float]] = {}
    
    async def run_test(
        self,
        name: str,
        func: Callable[[], Awaitable],
        iterations: int = 10
    ) -> dict:
        """Executa um teste de performance."""
        console.print(f"\n[bold cyan]Test:[/bold cyan] {name}")
        console.print(f"[dim]Iterations: {iterations}[/dim]")
        
        times = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Running {name}...", total=iterations)
            
            for i in range(iterations):
                start = time.perf_counter()
                try:
                    await func()
                    elapsed = time.perf_counter() - start
                    times.append(elapsed)
                except Exception as e:
                    console.print(f"[red]Error in iteration {i+1}: {e}[/red]")
                
                progress.advance(task)
        
        if times:
            stats = {
                "min": min(times),
                "max": max(times),
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                "p95": sorted(times)[int(len(times) * 0.95)] if len(times) >= 20 else max(times),
                "p99": sorted(times)[int(len(times) * 0.99)] if len(times) >= 100 else max(times),
                "total": sum(times),
                "count": len(times),
            }
            
            self.results[name] = times
            
            # Mostra resultados
            table = Table(show_header=False, box=None)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green", justify="right")
            
            table.add_row("Min", f"{stats['min']*1000:.2f}ms")
            table.add_row("Max", f"{stats['max']*1000:.2f}ms")
            table.add_row("Mean", f"{stats['mean']*1000:.2f}ms")
            table.add_row("Median", f"{stats['median']*1000:.2f}ms")
            table.add_row("Std Dev", f"{stats['stdev']*1000:.2f}ms")
            if len(times) >= 20:
                table.add_row("P95", f"{stats['p95']*1000:.2f}ms")
            if len(times) >= 100:
                table.add_row("P99", f"{stats['p99']*1000:.2f}ms")
            table.add_row("Total", f"{stats['total']:.2f}s")
            table.add_row("Requests/s", f"{stats['count']/stats['total']:.1f}")
            
            console.print(table)
            
            return stats
        else:
            console.print("[red]No successful requests[/red]")
            return {}
    
    def print_summary(self):
        """Imprime resumo de todos os testes."""
        console.print()
        console.print(Panel("[bold cyan]📊 Benchmark Summary[/bold cyan]", expand=False))
        console.print()
        
        table = Table(title="Results")
        table.add_column("Test", style="cyan")
        table.add_column("Requests", style="green", justify="right")
        table.add_column("Avg Time", style="yellow", justify="right")
        table.add_column("Min", style="blue", justify="right")
        table.add_column("Max", style="magenta", justify="right")
        table.add_column("Req/s", style="white", justify="right")
        
        for name, times in self.results.items():
            if times:
                avg = statistics.mean(times)
                min_t = min(times)
                max_t = max(times)
                req_per_sec = len(times) / sum(times)
                
                table.add_row(
                    name,
                    str(len(times)),
                    f"{avg*1000:.2f}ms",
                    f"{min_t*1000:.2f}ms",
                    f"{max_t*1000:.2f}ms",
                    f"{req_per_sec:.1f}"
                )
        
        console.print(table)


async def benchmark_health_check(iterations: int = 10):
    """Benchmark do health check."""
    benchmark = Benchmark()
    
    async def health_check():
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            response.raise_for_status()
    
    await benchmark.run_test("Health Check", health_check, iterations)
    
    return benchmark


async def benchmark_create_task(iterations: int = 10):
    """Benchmark de criação de tasks."""
    benchmark = Benchmark()
    
    async def create_task():
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/tasks",
                json={
                    "name": f"benchmark_task_{time.time()}",
                    "payload": {"benchmark": True},
                    "priority": "medium"
                }
            )
            response.raise_for_status()
    
    await benchmark.run_test("Create Task", create_task, iterations)
    
    return benchmark


async def benchmark_list_tasks(iterations: int = 10):
    """Benchmark de listagem de tasks."""
    benchmark = Benchmark()
    
    async def list_tasks():
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/tasks")
            response.raise_for_status()
    
    await benchmark.run_test("List Tasks", list_tasks, iterations)
    
    return benchmark


async def benchmark_get_task(iterations: int = 10):
    """Benchmark de busca de task por ID."""
    # Primeiro, cria uma task
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/tasks",
            json={"name": "benchmark_get", "payload": {}}
        )
        task_id = response.json()["id"]
    
    benchmark = Benchmark()
    
    async def get_task():
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/tasks/{task_id}")
            response.raise_for_status()
    
    await benchmark.run_test("Get Task by ID", get_task, iterations)
    
    return benchmark


async def benchmark_get_stats(iterations: int = 10):
    """Benchmark de estatísticas."""
    benchmark = Benchmark()
    
    async def get_stats():
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/tasks/stats")
            response.raise_for_status()
    
    await benchmark.run_test("Get Stats", get_stats, iterations)
    
    return benchmark


async def main(iterations: int = 10):
    """Executa todos os benchmarks."""
    console.print()
    console.print(Panel(
        "[bold cyan]⚡ Async POC — Benchmark[/bold cyan]\n"
        f"[dim]Iterations per test: {iterations}[/dim]",
        expand=False
    ))
    
    all_results = {}
    
    # Health Check
    benchmark = await benchmark_health_check(iterations)
    all_results.update(benchmark.results)
    
    # Create Task
    benchmark = await benchmark_create_task(iterations)
    all_results.update(benchmark.results)
    
    # List Tasks
    benchmark = await benchmark_list_tasks(iterations)
    all_results.update(benchmark.results)
    
    # Get Task
    benchmark = await benchmark_get_task(iterations)
    all_results.update(benchmark.results)
    
    # Get Stats
    benchmark = await benchmark_get_stats(iterations)
    all_results.update(benchmark.results)
    
    # Summary
    final_benchmark = Benchmark()
    final_benchmark.results = all_results
    final_benchmark.print_summary()
    
    console.print()
    console.print("[bold green]✓ Benchmark completo![/bold green]")
    console.print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark da API")
    parser.add_argument(
        "--requests",
        type=int,
        default=10,
        help="Número de requests por teste (default: 10)"
    )
    
    args = parser.parse_args()
    
    asyncio.run(main(args.requests))
