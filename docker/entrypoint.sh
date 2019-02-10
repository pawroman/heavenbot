#!/usr/bin/env sh

CONFIG_FILE="/heavenbot/data/config.ini"

# exit immediately if any command fails
set -e

# echo off
set +x

CONFIG_FILE_EXISTS=true

if ! [ -f "$CONFIG_FILE" ]; then
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

if [ "$1" == "irc3" ] && [ "$CONFIG_FILE_EXISTS" = false ]; then
    echo "Cannot access config file at: '$CONFIG_FILE'."
    echo "Hint: you can generate one using 'generate-config', e.g. 'docker run heavenbot generate-config'."
    echo "Abort."
    exit 2
fi

exec "$@"
