#!/bin/sh

base=$(dirname "$(realpath "${0}")")

export GIDEX_INDEX_PATH=${base}/index
export DEBUG=1

exec uvicorn --reload gidex.asgi:app
