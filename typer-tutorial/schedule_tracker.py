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

