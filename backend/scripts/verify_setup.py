#!/usr/bin/env python3
"""
Script de Verificação — Diagnostica problemas de configuração
==============================================================

Executa uma série de checks para verificar se o ambiente está configurado corretamente.

Uso:
    uv run python scripts/verify_setup.py
"""

import sys
import subprocess
from pathlib import Path


def check(name: str, condition: bool, success_msg: str, error_msg: str) -> bool:
    """Verifica uma condição e mostra o resultado."""
    if condition:
        print(f"✅ {name}: {success_msg}")
        return True
    else:
        print(f"❌ {name}: {error_msg}")
        return False


def main():
    print("=" * 60)
    print("🔍 Verificação de Configuração")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # 1. Verifica se está no diretório correto
    print("📁 Verificando estrutura de diretórios...")
    backend_dir = Path.cwd()
    all_passed &= check(
        "Diretório backend",
        (backend_dir / "pyproject.toml").exists(),
        "pyproject.toml encontrado",
        "pyproject.toml não encontrado. Execute este script do diretório backend/"
    )
    
    all_passed &= check(
        "Diretório src/app",
        (backend_dir / "src" / "app").exists(),
        "src/app/ encontrado",
        "src/app/ não encontrado"
    )
    
    all_passed &= check(
        "Arquivo __init__.py",
        (backend_dir / "src" / "app" / "__init__.py").exists(),
        "__init__.py encontrado",
        "__init__.py não encontrado em src/app/"
    )
    
    all_passed &= check(
        "Arquivo main.py",
        (backend_dir / "src" / "app" / "main.py").exists(),
        "main.py encontrado",
        "main.py não encontrado em src/app/"
    )
    
    print()
    
    # 2. Verifica configuração do pyproject.toml
    print("📋 Verificando pyproject.toml...")
    pyproject_path = backend_dir / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        
        all_passed &= check(
            "Build system",
            "[build-system]" in content,
            "[build-system] configurado",
            "[build-system] não encontrado no pyproject.toml"
        )
        
        all_passed &= check(
            "Hatchling",
            "hatchling" in content,
            "hatchling configurado",
            "hatchling não encontrado no pyproject.toml"
        )
        
        all_passed &= check(
            "Tool hatch",
            "[tool.hatch.build.targets.wheel]" in content,
            "[tool.hatch.build.targets.wheel] configurado",
            "[tool.hatch.build.targets.wheel] não encontrado no pyproject.toml"
        )
        
        all_passed &= check(
            "Packages path",
            'packages = ["src/app"]' in content,
            'packages = ["src/app"] configurado',
            'packages = ["src/app"] não encontrado no pyproject.toml'
        )
    else:
        all_passed &= check("pyproject.toml", False, "", "pyproject.toml não encontrado")
    
    print()
    
    # 3. Verifica instalação do pacote
    print("📦 Verificando instalação do pacote...")
    try:
        result = subprocess.run(
            ["uv", "pip", "show", "async-poc"],
            capture_output=True,
            text=True,
            cwd=backend_dir
        )
        
        all_passed &= check(
            "Pacote instalado",
            result.returncode == 0,
            "async-poc está instalado",
            "async-poc não está instalado. Execute: uv sync"
        )
    except Exception as e:
        all_passed &= check("Pacote instalado", False, "", f"Erro ao verificar: {e}")
    
    print()
    
    # 4. Verifica importação
    print("🐍 Verificando importação...")
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-c", "import app; print(app.__version__)"],
            capture_output=True,
            text=True,
            cwd=backend_dir
        )
        
        all_passed &= check(
            "Import app",
            result.returncode == 0,
            f"import app funciona (versão: {result.stdout.strip()})",
            f"import app falhou: {result.stderr}"
        )
    except Exception as e:
        all_passed &= check("Import app", False, "", f"Erro ao testar import: {e}")
    
    print()
    
    # 5. Verifica dependências principais
    print("🔧 Verificando dependências principais...")
    deps = ["fastapi", "pydantic", "sqlalchemy", "nicegui", "structlog"]
    for dep in deps:
        try:
            result = subprocess.run(
                ["uv", "run", "python", "-c", f"import {dep}"],
                capture_output=True,
                text=True,
                cwd=backend_dir
            )
            
            all_passed &= check(
                f"Dependência: {dep}",
                result.returncode == 0,
                f"{dep} instalado",
                f"{dep} não instalado. Execute: uv sync"
            )
        except Exception as e:
            all_passed &= check(f"Dependência: {dep}", False, "", f"Erro: {e}")
    
    print()
    
    # 6. Verifica scripts
    print("📜 Verificando scripts...")
    scripts = ["seed_data.py", "test_interactive.py", "benchmark.py", "dev.py"]
    for script in scripts:
        script_path = backend_dir / "scripts" / script
        all_passed &= check(
            f"Script: {script}",
            script_path.exists(),
            f"{script} encontrado",
            f"{script} não encontrado em scripts/"
        )
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("✅ Todas as verificações passaram!")
        print()
        print("🚀 Próximo passo:")
        print("   uv run python -m app.main")
        print()
        print("📚 Documentação:")
        print("   - SETUP.md — Guia de configuração")
        print("   - QUICKSTART.md — Guia rápido")
        print("   - TROUBLESHOOTING.md — Solução de problemas")
        return 0
    else:
        print("❌ Algumas verificações falharam!")
        print()
        print("🔧 Soluções:")
        print("   1. Reinstale as dependências:")
        print("      rm -rf .venv && uv sync")
        print()
        print("   2. Ou consulte:")
        print("      SETUP.md — Guia de configuração")
        print("      TROUBLESHOOTING.md — Solução de problemas")
        return 1


if __name__ == "__main__":
    sys.exit(main())
