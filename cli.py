import typer
import asyncio
import json
from rich.console import Console
from rich.table import Table
from core.orchestration import ScanOrchestrator

app = typer.Typer()
console = Console()

@app.command()
def scan(path: str = "."):
    """
    Run a security scan on the specified directory.
    """
    console.print(f"[bold green]SentinelAI Starting Scan on: {path}[/bold green]")
    
    orchestrator = ScanOrchestrator()
    findings = asyncio.run(orchestrator.scan_directory(path))
    
    # Display Results
    table = Table(title="Security Findings")
    table.add_column("Severity", style="bold")
    table.add_column("Issue")
    table.add_column("Location")
    table.add_column("AI Confidence")
    
    for f in findings:
        color = "red" if f.severity == "CRITICAL" else "yellow"
        table.add_row(
            f"[{color}]{f.severity}[/{color}]",
            f.title,
            f"{f.location.file_path}:{f.location.start_line}",
            str(f.confidence_score)
        )
    
    console.print(table)
    
    # Save Report
    with open("sentinel_report.json", "w") as f:
        f.write(json.dumps([x.dict() for x in findings], default=str, indent=2))
    console.print("[bold blue]Report saved to sentinel_report.json[/bold blue]")

if __name__ == "__main__":
    app()
