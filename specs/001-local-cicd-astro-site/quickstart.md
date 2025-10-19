# Quickstart

This document provides instructions on how to set up and run the project.

## Prerequisites

-   Node.js and npm (or a similar package manager)
-   jq
-   ShellCheck
-   Prettier

## Setup

1.  Clone the repository:
    ```bash
    git clone https://github.com/kairin/002-mcp-manager.git
    ```
2.  Navigate to the project directory:
    ```bash
    cd 002-mcp-manager
    ```
3.  Install the dependencies for the website:
    ```bash
    cd web
    npm install
    ```

## Running the project

### Website

To start the development server for the website, run the following command from the `web` directory:
```bash
npm run dev
```

### Local CI/CD

To run the local CI/CD script, run the following command from the root of the project:
```bash
./scripts/local-ci/run.sh
```

### TUI

To start the TUI, run the following command from the root of the project:
```bash
./scripts/tui/run.sh
```
