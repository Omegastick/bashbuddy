import typer

from bashbuddy.agent import run_agent

app = typer.Typer()


@app.command()
def run_command(command: str) -> None:
    response = run_agent(command)
    print(response)


if __name__ == "__main__":
    app()
