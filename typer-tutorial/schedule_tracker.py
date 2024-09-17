import typer
from datetime import datetime
import json
from typing import List

app = typer.Typer()

SCHEDULE_FILE = "schedule.json"

def load_schedule() -> List[dict]:
    try:
        with open(SCHEDULE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_schedule(schedule: List[dict]):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule, f, default=str, indent=4)

def parse_time(t: str) -> datetime.time:
    try:
        return datetime.strptime(t, "%H:%M").time()
    except ValueError:
        typer.echo("Invalid time format. Please use HH:MM.")
        raise typer.Exit()


@app.command()
def add_task(
	task: str,
	time: str = typer.Option(..., help="Time in HH:MM format"),
	priority: int = typer.Option(1, help="Priority of the task")
):
    schedule = load_schedule()
    task_time = parse_time(time)
    schedule.append({"task": task, "time": task_time.strftime("%H:%M"), "priority": priority})
    save_schedule(schedule)
    typer.echo(f"Task '{task}' added at {task_time.strftime('%H:%M')} with priority {priority}")

@app.command()
def list_tasks():
    """List all scheduled tasks."""
    schedule = load_schedule()
    if not schedule:
        typer.echo("No tasks found.")
        return
    for task in sorted(schedule, key=lambda x: x["time"]):
        @app.command()
        print(f"Task {i}: {task['task']}")
        print(f"  Time: {task['time']}")
        print(f"  Priority: {task['priority']}")
        print("-" * 40)  # Add a separator line for better readability

@app.command()
def remove_task(task_number: int):
    """Remove a task by its number."""
    schedule = load_schedule()
    if 0 < task_number <= len(schedule):
        removed_task = schedule.pop(task_number - 1)
        save_schedule(schedule)  # Save the updated schedule
        typer.echo(f"Removed task '{removed_task['task']}' scheduled at {removed_task['time']}") 
    else: 
        typer.echo(f"Invalid task number. Choose a number between 1 and {len(schedule)}.")

if __name__ == "__main__":
	app()


