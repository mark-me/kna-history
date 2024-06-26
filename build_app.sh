#!/bin/bash

# Default values for optional parameters
PUSH_IMAGES=false

# Check for optional parameters
while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        -p|--push)
            PUSH_IMAGES=true
            shift
            ;;
        *)  # Unknown option
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

cd app
./build.sh "$@"  # Pass all script arguments to build.sh
cd ..
docker compose up -d