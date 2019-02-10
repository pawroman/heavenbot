#!/usr/bin/env sh

CONFIG_FILE="/heavenbot/data/config.ini"

# exit immediately if any command fails
set -e

# echo off
set +x

CONFIG_FILE_EXISTS=true

if ! [ -f "$CONFIG_FILE" ]; then
    echo "Doesn't exist"
    CONFIG_FILE_EXISTS=false
fi

if [ "$#" -eq 1 ] && [ "$1" == "generate-config" ]; then
    if [ "$CONFIG_FILE_EXISTS" = true ]; then
        echo "Config file at: '$CONFIG_FILE' already exists. Refusing to overwrite."
        exit 1
    else
        cp sample-config.ini "$CONFIG_FILE"
        echo "Generated sample config file at: '$CONFIG_FILE'."
        exit 0
    fi
fi

if [ "$#" -eq 0 ] && [ "$CONFIG_FILE_EXISTS" = false ]; then
    echo "Cannot access config file at: '$CONFIG_FILE'. Abort."
    exit 2
fi

exec "$@"
