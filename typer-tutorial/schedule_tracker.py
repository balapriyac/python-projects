import typer
from datetime import datetime
import json
from typing import List

app = typer.Typer()

SCHEDULE_FILE = "schedule.json"

def load_schedule() -> List[dict]:
    """Load the schedule from a JSON file."""
    try:
        with open(SCHEDULE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_schedule(schedule: List[dict]):
    """Save the schedule to a JSON file."""
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedule, f, default=str, indent=4)


def parse_time(t: str) -> datetime.time:
    """Parse a string into a time object in HH:MM format."""
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
    """Add a task with a specific time and priority."""
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
        typer.echo(f"Task: {task['task']} | Time: {task['time']} | Priority: {task['priority']}")

if __name__ == "__main__":
    app()

