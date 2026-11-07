"""Save and load a full run as local JSON, so analyses re-run without re-calling the APIs."""

from pathlib import Path

from evaluation.measurement.records import FullRun


def save_run(run: FullRun, path: Path) -> None:
    """Write the run to a JSON file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(run.model_dump_json(indent=2), encoding="utf-8")


def load_run(path: Path) -> FullRun:
    """Read a run back from a JSON file."""
    return FullRun.model_validate_json(path.read_text(encoding="utf-8"))
