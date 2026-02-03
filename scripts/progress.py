#!/usr/bin/env python3
"""Script de utilidad para gestionar el progreso del proyecto."""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class ProgressTracker:
    """Gestor de progreso del proyecto."""

    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.plan_file = self.root / "docs" / "IMPROVEMENT_PLAN.md"
        self.progress_file = self.root / "docs" / "PROGRESS.md"

    def parse_tasks(self) -> Dict[str, List[Dict]]:
        """Parsea las tareas del plan de mejoras."""
        if not self.plan_file.exists():
            return {}

        content = self.plan_file.read_text(encoding="utf-8")
        phases = {}
        current_phase = None

        # Buscar tablas de tareas
        for line in content.split("\n"):
            if line.startswith("### **FASE"):
                match = re.search(r"FASE (\d+)", line)
                if match:
                    current_phase = f"FASE_{match.group(1)}"
                    phases[current_phase] = []

            elif current_phase and "|" in line and "Tarea" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 5:
                    task = {
                        "id": parts[1],
                        "name": parts[2],
                        "priority": parts[3],
                        "effort": parts[4],
                        "status": parts[5] if len(parts) > 5 else "⏳ Pendiente",
                    }
                    if task["id"] and task["id"] != "---":
                        phases[current_phase].append(task)

        return phases

    def calculate_progress(self) -> Tuple[int, int, float]:
        """Calcula el progreso total."""
        phases = self.parse_tasks()
        total_tasks = 0
        completed_tasks = 0

        for phase_tasks in phases.values():
            for task in phase_tasks:
                total_tasks += 1
                if "✅" in task["status"] or "Completado" in task["status"]:
                    completed_tasks += 1

        percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        return completed_tasks, total_tasks, percentage

    def generate_progress_bar(self, percentage: float, width: int = 10) -> str:
        """Genera una barra de progreso visual."""
        filled = int(percentage / 10)
        empty = width - filled
        return "#" * filled + "-" * empty

    def update_progress_file(self):
        """Actualiza el archivo de progreso."""
        completed, total, percentage = self.calculate_progress()

        print(f"\nProgreso del Proyecto")
        print(f"{'=' * 50}")
        print(f"Tareas completadas: {completed}/{total}")
        print(f"Porcentaje: {percentage:.1f}%")
        print(f"Barra: [{self.generate_progress_bar(percentage)}]")
        print(f"{'=' * 50}\n")

    def mark_task_complete(self, task_id: str):
        """Marca una tarea como completada."""
        if not self.plan_file.exists():
            print("[ERROR] Archivo de plan no encontrado")
            return

        content = self.plan_file.read_text(encoding="utf-8")
        
        # Buscar la línea de la tarea
        pattern = rf"(\| {task_id} \|[^|]+\|[^|]+\|[^|]+\|) ⏳ Pendiente"
        replacement = rf"\1 ✅ Completado"
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            self.plan_file.write_text(new_content, encoding="utf-8")
            print(f"[OK] Tarea {task_id} marcada como completada")
            self.update_progress_file()
        else:
            print(f"[ERROR] No se encontro la tarea {task_id}")

    def list_pending_tasks(self, phase: str = None):
        """Lista las tareas pendientes."""
        phases = self.parse_tasks()
        
        print(f"\nTareas Pendientes")
        print(f"{'=' * 70}\n")

        for phase_name, tasks in phases.items():
            if phase and phase_name != phase:
                continue

            pending = [t for t in tasks if "⏳" in t["status"] or "Pendiente" in t["status"]]
            
            if pending:
                print(f"### {phase_name}")
                for task in pending:
                    priority_mark = "[ALTA]" if "Alta" in task["priority"] else "[MEDIA]" if "Media" in task["priority"] else "[BAJA]"
                    print(f"  {priority_mark} {task['id']}: {task['name']} ({task['effort']})")
                print()

    def add_log_entry(self, message: str):
        """Agrega una entrada al log de trabajo."""
        if not self.progress_file.exists():
            print("[ERROR] Archivo de progreso no encontrado")
            return

        content = self.progress_file.read_text(encoding="utf-8")
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Buscar la sección de log
        log_section = f"### {today}"
        
        if log_section not in content:
            # Crear nueva entrada
            new_entry = f"\n{log_section}\n**Notas**: {message}\n"
            # Insertar después de "## 📅 Log de Trabajo"
            content = content.replace(
                "## 📅 Log de Trabajo\n",
                f"## 📅 Log de Trabajo\n{new_entry}"
            )
        else:
            # Agregar a entrada existente
            content = content.replace(
                f"{log_section}\n",
                f"{log_section}\n- {message}\n"
            )
        
        self.progress_file.write_text(content, encoding="utf-8")
        print(f"[OK] Entrada agregada al log: {message}")


def main():
    """Función principal."""
    import sys

    tracker = ProgressTracker()

    if len(sys.argv) < 2:
        print("Uso:")
        print("  python progress.py status              - Ver progreso actual")
        print("  python progress.py list [fase]         - Listar tareas pendientes")
        print("  python progress.py complete <task_id>  - Marcar tarea como completada")
        print("  python progress.py log <mensaje>       - Agregar entrada al log")
        return

    command = sys.argv[1]

    if command == "status":
        tracker.update_progress_file()
    
    elif command == "list":
        phase = sys.argv[2] if len(sys.argv) > 2 else None
        tracker.list_pending_tasks(phase)
    
    elif command == "complete":
        if len(sys.argv) < 3:
            print("[ERROR] Especifica el ID de la tarea")
            return
        task_id = sys.argv[2]
        tracker.mark_task_complete(task_id)
    
    elif command == "log":
        if len(sys.argv) < 3:
            print("[ERROR] Especifica el mensaje")
            return
        message = " ".join(sys.argv[2:])
        tracker.add_log_entry(message)
    
    else:
        print(f"[ERROR] Comando desconocido: {command}")


if __name__ == "__main__":
    main()
