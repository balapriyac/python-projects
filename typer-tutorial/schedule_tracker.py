import typer
from datetime import datetime, time

app = typer.Typer()
schedule = []

def parse_time(t: str) -> time:
    """Parse a string into a time object in HH:MM format."""
    try:
        return datetime.strptime(t, "%H:%M").time()
    except ValueError:
        typer.echo("Invalid time format. Please use HH:MM.")
        raise typer.Exit()

@app.command()
def add_task(task: str, time: str = typer.Option(..., help="Time in HH:MM format"), priority: int = typer.Option(1, help="Task priority")):
    """Add a task with a valid time (HH:MM) and optional priority."""
    task_time = parse_time(time)
    schedule.append({"task": task, "time": task_time, "priority": priority})
    typer.echo(f"Task '{task}' added at {task_time.strftime('%H:%M')} with priority {priority}")

if __name__ == "__main__":
    app()
