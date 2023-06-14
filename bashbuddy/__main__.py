from typing import Annotated, Optional

import typer

from bashbuddy.agent import run_agent

app = typer.Typer()


@app.command()
def run_command(
    file: Annotated[Optional[typer.FileText], typer.Argument()] = None,
    command: Annotated[Optional[str], typer.Option("--command", "-c")] = None,
):
    if file is None and command is None:
        typer.echo("Please provide a command or a file.")
        raise typer.Exit(1)

    if file is not None:
        command = file.read()

    response = run_agent(command)  # type: ignore
    print(response)


if __name__ == "__main__":
    app()
