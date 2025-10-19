#!/bin/bash

# Simple TUI for the project

PS3="Please enter your choice: "
options=("Run Local CI/CD" "Start Astro Dev Server" "Exit")
select opt in "${options[@]}"
do
    case $opt in
        "Run Local CI/CD")
            echo "Running local CI/CD..."
            /home/kkk/Apps/002-mcp-manager/scripts/local-ci/run.sh
            ;;
        "Start Astro Dev Server")
            echo "Starting Astro dev server..."
            cd /home/kkk/Apps/002-mcp-manager/web && npm run dev
            ;;
        "Exit")
            break
            ;;
        *)
            echo "invalid option $REPLY"
            ;;
    esac
done