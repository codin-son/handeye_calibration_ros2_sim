#!/bin/bash
# Start (or attach to) the handeye_sim container with X11 GUI support.
set -e
cd "$(dirname "$0")/.."

# Allow the container to talk to the host X server
xhost +local:docker > /dev/null

if [ "$(docker ps -q -f name=handeye_sim)" ]; then
    exec docker exec -it handeye_sim /entrypoint.sh bash
else
    exec docker compose run --rm --name handeye_sim handeye_sim
fi
