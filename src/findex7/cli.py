import click
import uvicorn


@click.group()
def cli():
    """Findex search engine CLI."""
    pass


@cli.command()
@click.option("--port", default=8000, help="Port to bind the server to.", show_default=True)
@click.option("--workers", default=1, help="Number of worker processes.", show_default=True)
@click.option("--host", default="127.0.0.1", help="Bind socket to this host.", show_default=True)
def serve(port: int, workers: int, host: str):
    """Start the Findex FastAPI web server."""
    click.echo(f"Starting Findex server at http://{host}:{port} with {workers} worker(s)...")
    uvicorn.run(
        "findex.web.app:app",
        host=host,
        port=port,
        workers=workers,
        reload=False,
    )


if __name__ == "__main__":
    cli()