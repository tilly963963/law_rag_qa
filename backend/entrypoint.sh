#!/bin/bash

LISTEN=${LISTEN:-"0.0.0.0:15012"}
TIMEOUT=${TIMEOUT:-0}
WORKERS=${WORKERS:-1}

exec gunicorn --bind "$LISTEN" --timeout="$TIMEOUT" --workers="$WORKERS" --reload web.server:api
