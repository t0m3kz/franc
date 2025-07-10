# Copyright (c) 2024 FRANC Service Portal
# All rights reserved.

"""Build and development tasks for the FRANC Service Portal."""

from pathlib import Path

from invoke import Context, task

CURRENT_DIRECTORY = Path(__file__).resolve()

MAIN_DIRECTORY_PATH = Path(__file__).parent


@task(name="format")
def format_all(context: Context) -> None:
    """Run RUFF to format all Python files."""
    exec_cmds = ["ruff format .", "ruff check . --fix"]
    with context.cd(MAIN_DIRECTORY_PATH):
        for cmd in exec_cmds:
            context.run(cmd, pty=True)


@task
def lint_yaml(context: Context) -> None:
    """Run Linter to check all Python files."""
    exec_cmd = "yamllint ."
    with context.cd(MAIN_DIRECTORY_PATH):
        context.run(exec_cmd, pty=True)


@task
def lint_ruff(context: Context) -> None:
    """Run Linter to check all Python files."""
    exec_cmd = "ruff check ."
    with context.cd(MAIN_DIRECTORY_PATH):
        context.run(exec_cmd, pty=True)


@task(name="start")
def start(context: Context) -> None:
    """Run streamlit application."""
    exec_cmd = "streamlit run src/main.py"
    with context.cd(MAIN_DIRECTORY_PATH):
        context.run(exec_cmd, pty=True)


@task(name="lint")
def lint_all(context: Context) -> None:
    """Run all linters."""
    lint_yaml(context)
    lint_ruff(context)


@task(name="protocols")
def update_protocols(context: Context) -> None:
    """Regenerate Infrahub schema protocols from remote instance."""
    exec_cmd = "infrahubctl protocols"
    with context.cd(MAIN_DIRECTORY_PATH):
        context.run(exec_cmd, pty=True)
