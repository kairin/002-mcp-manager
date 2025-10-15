"""CLI utilities for error handling and formatting."""

import functools
import logging
import traceback
from collections.abc import Callable
from typing import Any

import typer
from rich.console import Console
from rich.logging import RichHandler

from .exceptions import (
    ConfigurationError,
    FileSystemError,
    InvalidPathError,
    MCPManagerError,
    ServerNotFoundError,
    ShellProfileError,
    UpdateCheckError,
)

console = Console()

# Global verbose mode flag
_verbose_mode = False


def set_verbose_mode(enabled: bool) -> None:
    """Enable or disable verbose mode globally.

    Args:
        enabled: True to enable verbose mode, False to disable
    """
    global _verbose_mode
    _verbose_mode = enabled

    # Configure logging based on verbose mode
    if enabled:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True, show_path=True)],
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
        )


def is_verbose_mode() -> bool:
    """Check if verbose mode is enabled.

    Returns:
        True if verbose mode is enabled, False otherwise
    """
    return _verbose_mode


def debug_log(message: str) -> None:
    """Log a debug message (only shown in verbose mode).

    Args:
        message: Debug message to log

    Example:
        >>> from mcp_manager.cli_utils import debug_log
        >>> debug_log("Processing server configuration")
        # Only prints if --verbose flag is used
    """
    if _verbose_mode:
        logging.debug(message)


def verbose_print(message: str, style: str = "dim") -> None:
    """Print a message only in verbose mode.

    Args:
        message: Message to print
        style: Rich style to apply (default: "dim")

    Example:
        >>> from mcp_manager.cli_utils import verbose_print
        >>> verbose_print("Detailed operation info", "cyan")
        # Only prints if --verbose flag is used
    """
    if _verbose_mode:
        console.print(f"[{style}]{message}[/{style}]")


def handle_cli_errors(func: Callable) -> Callable:
    """Decorator for consistent CLI error handling.

    Catches exceptions and formats them nicely for CLI output:
    - MCPManagerError subclasses: Shows error message with context
    - Unexpected exceptions: Shows error + traceback in debug mode

    In verbose mode, shows additional debugging information.

    Usage:
        @handle_cli_errors
        def my_command():
            raise ConfigurationError("Invalid config")

    Args:
        func: CLI command function to wrap

    Returns:
        Wrapped function with error handling
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ServerNotFoundError as e:
            console.print(f"[red]❌ Server Not Found:[/red] {e}")
            console.print(
                "\n[cyan]💡 Hint:[/cyan] Run [bold]mcp-manager mcp status[/bold] to see available servers"
            )
            if is_verbose_mode():
                console.print("\n[dim]Debug traceback:[/dim]")
                console.print("[dim]" + traceback.format_exc() + "[/dim]")
            raise typer.Exit(1)
        except ConfigurationError as e:
            console.print(f"[red]❌ Configuration Error:[/red] {e}")
            console.print(
                "\n[cyan]💡 Hint:[/cyan] Check your ~/.claude.json configuration file"
            )
            if is_verbose_mode():
                console.print("\n[dim]Debug traceback:[/dim]")
                console.print("[dim]" + traceback.format_exc() + "[/dim]")
            raise typer.Exit(1)
        except InvalidPathError as e:
            console.print(f"[red]❌ Invalid Path:[/red] {e}")
            console.print(
                "\n[cyan]💡 Hint:[/cyan] Ensure the specified path exists and is accessible"
            )
            if is_verbose_mode():
                console.print("\n[dim]Debug traceback:[/dim]")
                console.print("[dim]" + traceback.format_exc() + "[/dim]")
            raise typer.Exit(1)
        except FileSystemError as e:
            console.print(f"[red]❌ File System Error:[/red] {e}")
            console.print(
                "\n[cyan]💡 Hint:[/cyan] Check file permissions and disk space"
            )
            if is_verbose_mode():
                console.print("\n[dim]Debug traceback:[/dim]")
                console.print("[dim]" + traceback.format_exc() + "[/dim]")
            raise typer.Exit(1)
        except ShellProfileError as e:
            console.print(f"[red]❌ Shell Profile Error:[/red] {e}")
            console.print(
                "\n[cyan]💡 Hint:[/cyan] Manually add environment variables to your shell profile"
            )
            if is_verbose_mode():
                console.print("\n[dim]Debug traceback:[/dim]")
                console.print("[dim]" + traceback.format_exc() + "[/dim]")
            raise typer.Exit(1)
        except UpdateCheckError as e:
            console.print(f"[yellow]⚠️ Update Check Failed:[/yellow] {e}")
            console.print(
                "\n[cyan]💡 Hint:[/cyan] Check your internet connection and npm installation"
            )
            if is_verbose_mode():
                console.print("\n[dim]Debug traceback:[/dim]")
                console.print("[dim]" + traceback.format_exc() + "[/dim]")
            raise typer.Exit(1)
        except MCPManagerError as e:
            # Generic MCP Manager error
            console.print(f"[red]❌ Error:[/red] {e}")
            if is_verbose_mode():
                console.print("\n[dim]Debug traceback:[/dim]")
                console.print("[dim]" + traceback.format_exc() + "[/dim]")
            raise typer.Exit(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️ Operation cancelled by user[/yellow]")
            raise typer.Exit(130)  # Standard exit code for SIGINT
        except Exception as e:
            # Unexpected error - always show detailed traceback
            console.print(f"[red]❌ Unexpected Error:[/red] {type(e).__name__}: {e}")
            console.print("\n[dim]Stack trace:[/dim]")
            console.print("[dim]" + traceback.format_exc() + "[/dim]")
            console.print("\n[cyan]💡 This is a bug! Please report it at:[/cyan]")
            console.print("   https://github.com/kairin/mcp-manager/issues")
            raise typer.Exit(1)

    return wrapper


def format_error_context(error: Exception) -> str:
    """Format error with additional context for debugging.

    Args:
        error: Exception to format

    Returns:
        Formatted error string with context
    """
    error_type = type(error).__name__
    error_msg = str(error)

    # Add context based on error type
    if isinstance(error, ConfigurationError):
        return f"{error_type}: {error_msg}\nCheck ~/.claude.json for syntax errors"
    elif isinstance(error, ServerNotFoundError):
        return f"{error_type}: {error_msg}\nRun 'mcp-manager mcp status' to see available servers"
    elif isinstance(error, InvalidPathError):
        return f"{error_type}: {error_msg}\nVerify the path exists and is accessible"
    else:
        return f"{error_type}: {error_msg}"


def get_error_suggestion(error: Exception) -> str | None:
    """Get helpful suggestion for resolving an error.

    Args:
        error: Exception to analyze

    Returns:
        Suggestion string or None if no specific suggestion available
    """
    if isinstance(error, ConfigurationError):
        if "missing" in str(error).lower():
            return "Run 'mcp-manager mcp init --global' to create a configuration"
        elif "invalid" in str(error).lower():
            return "Validate your configuration with 'mcp-manager mcp audit'"
    elif isinstance(error, ServerNotFoundError):
        return "Add the server with 'mcp-manager mcp add <name>'"
    elif isinstance(error, UpdateCheckError):
        if "npm" in str(error).lower():
            return "Install npm or check your npm installation"
        elif "timeout" in str(error).lower():
            return "Check your internet connection and try again"
    elif isinstance(error, FileSystemError):
        if "permission" in str(error).lower():
            return "Check file permissions or run with appropriate privileges"

    return None
