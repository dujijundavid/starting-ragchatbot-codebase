#!/bin/bash

# Script to sync Python version from .python-version file to uv
# Run this after switching branches if the Python version seems wrong

if [ -f .python-version ]; then
    PYTHON_VERSION=$(cat .python-version | tr -d '\n')
    if [ -n "$PYTHON_VERSION" ]; then
        echo "Syncing Python version to $PYTHON_VERSION..."
        uv python pin "$PYTHON_VERSION"
        echo "Done! Python version is now set to $PYTHON_VERSION"
    else
        echo "Error: .python-version file is empty"
        exit 1
    fi
else
    echo "Error: .python-version file not found"
    exit 1
fi

