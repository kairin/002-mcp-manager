# T031: Verbose/Debug Mode Implementation - COMPLETED ✅

## Overview

Task T031 implements a comprehensive verbose/debug mode system for MCP Manager CLI, providing enhanced debugging capabilities and detailed output when needed.

## Implementation Details

### 1. Global Verbose Mode Flag

**File**: `src/mcp_manager/cli_utils.py`

Added global verbose mode management:

```python
# Global verbose mode flag
_verbose_mode = False

def set_verbose_mode(enabled: bool) -> None:
    """Enable or disable verbose mode globally."""
    global _verbose_mode
    _verbose_mode = enabled

    # Configure logging based on verbose mode
    if enabled:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True, show_path=True)]
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True, show_path=False)]
        )

def is_verbose_mode() -> bool:
    """Check if verbose mode is enabled."""
    return _verbose_mode
```

### 2. CLI Integration

**File**: `src/mcp_manager/cli.py`

Added global `--verbose/-v` flag using Typer callback:

```python
@app.callback()
def global_options(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output with debug information",
    ),
) -> None:
    """Global options for MCP Manager."""
    set_verbose_mode(verbose)
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")
```

### 3. Enhanced Error Handler

Updated `handle_cli_errors` decorator to show debug tracebacks in verbose mode:

```python
except ConfigurationError as e:
    console.print(f"[red]❌ Configuration Error:[/red] {e}")
    console.print(
        "\n[cyan]💡 Hint:[/cyan] Check your ~/.claude.json configuration file"
    )
    if is_verbose_mode():
        console.print("\n[dim]Debug traceback:[/dim]")
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
    raise typer.Exit(1)
```

This applies to all error types:
- ServerNotFoundError
- ConfigurationError
- InvalidPathError
- FileSystemError
- ShellProfileError
- UpdateCheckError
- Generic MCPManagerError

### 4. Debug Helper Functions

#### debug_log()

For logging debug messages:

```python
def debug_log(message: str) -> None:
    """Log a debug message (only shown in verbose mode)."""
    if _verbose_mode:
        logging.debug(message)
```

**Usage**:
```python
from mcp_manager.cli_utils import debug_log

debug_log("Processing server configuration...")
debug_log(f"Found {len(servers)} servers")
```

#### verbose_print()

For printing verbose messages with Rich formatting:

```python
def verbose_print(message: str, style: str = "dim") -> None:
    """Print a message only in verbose mode."""
    if _verbose_mode:
        console.print(f"[{style}]{message}[/{style}]")
```

**Usage**:
```python
from mcp_manager.cli_utils import verbose_print

verbose_print("Starting health check...", "cyan")
verbose_print(f"Checking server: {server_name}", "dim")
```

## Usage Examples

### Basic Usage

```bash
# Normal mode (no debug output)
mcp-manager mcp status

# Verbose mode (shows debug info)
mcp-manager --verbose mcp status
mcp-manager -v mcp status
```

### With Any Command

```bash
# Audit with verbose output
mcp-manager --verbose mcp audit

# Add server with debug logging
mcp-manager -v mcp add test-server --type stdio --command npx

# Status check with detailed errors
mcp-manager --verbose mcp status github
```

### Error Debugging

**Normal Mode**:
```bash
$ mcp-manager mcp status nonexistent-server
❌ Server Not Found: Server 'nonexistent-server' not found

💡 Hint: Run mcp-manager mcp status to see available servers
```

**Verbose Mode**:
```bash
$ mcp-manager --verbose mcp status nonexistent-server
Verbose mode enabled
❌ Server Not Found: Server 'nonexistent-server' not found

💡 Hint: Run mcp-manager mcp status to see available servers

Debug traceback:
Traceback (most recent call last):
  File ".../core.py", line 123, in check_server_health
    server_config = self.get_server_config(name)
  File ".../core.py", line 89, in get_server_config
    raise ServerNotFoundError(f"Server '{name}' not found")
ServerNotFoundError: Server 'nonexistent-server' not found
```

## Benefits

### 1. User Experience
- **Normal Mode**: Clean, user-friendly output for everyday use
- **Verbose Mode**: Detailed information for debugging and troubleshooting

### 2. Developer Experience
- **Easy Integration**: Simple `debug_log()` and `verbose_print()` functions
- **Consistent Behavior**: Global flag affects all commands uniformly
- **Rich Logging**: Leverages Rich library for beautiful debug output

### 3. Debugging
- **Stack Traces**: Full error context in verbose mode
- **Debug Logging**: Detailed execution flow visibility
- **File Paths**: Shows source file locations in tracebacks

## Integration Examples

### In Core Module

```python
from mcp_manager.cli_utils import debug_log, verbose_print

class MCPManager:
    def check_server_health(self, name: str) -> dict:
        debug_log(f"Checking health for server: {name}")

        config = self.get_server_config(name)
        verbose_print(f"Server config: {config}", "cyan")

        # ... health check logic ...

        debug_log(f"Health check completed: {result}")
        return result
```

### In CLI Commands

```python
@mcp_app.command("update")
@handle_cli_errors
def mcp_update(name: str) -> None:
    """Update MCP server."""
    verbose_print(f"Updating server: {name}", "cyan")

    manager = MCPManager()
    debug_log("Checking for updates...")

    result = manager.update_server(name)

    debug_log(f"Update result: {result}")
    rprint("[green]✅ Update complete![/green]")
```

## Testing

### Verification Tests

```python
# Test verbose mode state
from mcp_manager.cli_utils import set_verbose_mode, is_verbose_mode

assert is_verbose_mode() == False  # Default off
set_verbose_mode(True)
assert is_verbose_mode() == True   # Can be enabled
```

### CLI Tests

```bash
# Test help shows verbose flag
$ mcp-manager --help | grep verbose
--verbose             -v        Enable verbose output with debug information

# Test verbose flag works
$ mcp-manager --verbose mcp audit
Verbose mode enabled
{...audit results...}

# Test short flag works
$ mcp-manager -v mcp status
Verbose mode enabled
{...status results...}
```

## Files Modified

1. **src/mcp_manager/cli_utils.py**
   - Added: `set_verbose_mode()` function
   - Added: `is_verbose_mode()` function
   - Added: `debug_log()` helper
   - Added: `verbose_print()` helper
   - Updated: `handle_cli_errors()` with verbose traceback support

2. **src/mcp_manager/cli.py**
   - Added: Global `--verbose/-v` flag
   - Added: `global_options()` callback
   - Updated: Imports for verbose mode functions

## Logging Configuration

### Normal Mode
- **Level**: INFO
- **Rich Tracebacks**: Enabled
- **Show Path**: Disabled
- **Output**: User-friendly messages only

### Verbose Mode
- **Level**: DEBUG
- **Rich Tracebacks**: Enabled
- **Show Path**: Enabled (shows file:line)
- **Output**: All debug messages + detailed tracebacks

## Future Enhancements

Potential improvements for future iterations:

1. **Log File Output**: Option to write verbose logs to file
2. **Verbose Levels**: Multiple verbosity levels (-v, -vv, -vvv)
3. **Performance Timing**: Show execution times in verbose mode
4. **Network Debugging**: HTTP request/response logging
5. **Configuration Dump**: Show full config in verbose mode

## Completion Status

✅ **COMPLETE**: All T031 requirements implemented and tested

### Deliverables
- ✅ Global `--verbose/-v` flag
- ✅ Verbose mode state management
- ✅ Enhanced error handler with debug tracebacks
- ✅ Debug logging helpers (`debug_log`, `verbose_print`)
- ✅ Rich logging configuration
- ✅ CLI integration
- ✅ Testing and verification

## Related Tasks

- ✅ **T029**: Error handling decorator (uses verbose mode)
- ✅ **T030**: Exception formatting (enhanced in verbose mode)
- ✅ **T032**: Error recovery suggestions (shown with verbose traces)
- ⏳ **T033**: API documentation (will document verbose mode)

## Completion Date

2025-10-14
