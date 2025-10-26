# Research: TUI Library for Profile Management

**Date**: 2025-10-26
**Author**: Gemini

## 1. Research Task

Investigate TUI (Text-based User Interface) libraries for Bash for implementing profile management (create, edit, delete), as required by the clarified feature specification.

**Context**: The feature specification was updated to include a TUI for managing the lifecycle of MCP profiles. The current TUI is minimal, and this new functionality requires a more robust solution.

## 2. Findings

A web search was conducted to evaluate different approaches for building TUIs in Bash scripts. The primary candidates are `dialog`, `whiptail`, and custom implementations.

### `dialog`
- **Description**: A mature and feature-rich utility for creating professional-looking dialog boxes from shell scripts. It is based on the `ncurses` library.
- **Pros**:
    - Offers a wide variety of dialog boxes, including menus, input boxes, checklists, forms, and calendars.
    - Highly customizable (colors, titles, button labels).
    - Well-documented and widely used, with many examples available.
- **Cons**:
    - May not be installed by default on all systems (though it is widely available in package managers).

### `whiptail`
- **Description**: A lightweight alternative to `dialog`, designed as a drop-in replacement for many common use cases. It is based on the `newt` library.
- **Pros**:
    - Simpler and more lightweight than `dialog`.
    - Often pre-installed on Debian-based systems.
- **Cons**:
    - Fewer box types and customization options compared to `dialog`.

### `gum`
- **Description**: A modern tool for creating glamorous shell scripts with a focus on user experience.
- **Pros**:
    - Produces aesthetically pleasing, modern-looking prompts.
    - Simple to use for common interactive tasks.
- **Cons**:
    - A newer tool, may not be as widely available or as stable as `dialog`.
    - Introduces another dependency.

### Custom Implementation
- **Description**: Using built-in Bash commands like `read`, `select`, and `case`, along with `tput` for terminal manipulation.
- **Pros**:
    - No external dependencies.
    - Maximum control over the UI.
- **Cons**:
    - Significantly more complex to implement and maintain.
    - Difficult to create complex UIs like forms or checklists.

## 3. Decision

**Decision**: Use `dialog` for implementing the TUI-based profile management features.

**Rationale**:

The new requirement for creating, editing, and deleting profiles will likely involve forms and complex interactions. `dialog` provides the most comprehensive set of tools for this purpose out of the box. Its extensive documentation and wide availability make it a robust and reliable choice that aligns with the project's need for a verifiable and functional user interface.

While `whiptail` is a good lightweight option, its limited feature set might hinder the development of a user-friendly profile editor. `gum` is interesting but adds a newer, less-established dependency. A custom implementation would be too time-consuming and complex for this project.

## 4. Alternatives Considered

- **`whiptail`**: Rejected due to its limited feature set compared to `dialog`.
- **`gum`**: Rejected to avoid adding a newer, less common dependency.
- **Custom Implementation**: Rejected due to high complexity and maintenance overhead.
