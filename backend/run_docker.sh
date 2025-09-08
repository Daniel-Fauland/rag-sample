# !/usr/bin/env sh
#
# Build and run the example Docker image.
#
# Mounts the local project directory to reflect a common development workflow.
#
# The `docker run` command uses the following options:
#
#   --rm                        Remove the container after exiting
#   --volume .:/app             Mount the current directory to `/app` so code changes don't require an image rebuild
#   --volume /app/.venv         Mount the virtual environment separately, so the developer's environment doesn't end up in the container
#   --publish 8000:8000         Expose the web server port 8000 to the host
#   -it $(docker build -q .)    Build the image, then use it as a run target
#   $@                          Pass any arguments to the container

if [ -t 1 ]; then
    INTERACTIVE="-it"
else
    INTERACTIVE=""
fi

# Check if running in Git Bash on Windows
if [[ -n "$MSYSTEM" ]]; then
    echo "Building and running docker container for windows..."
    # Windows needs to use the absolute path or it will fail to start the container
    VOLUME_PATH="${CURRENT_DIR}:/app"
else
    echo "Building and running docker container for linux/macOS..."
    VOLUME_PATH=".:/app"
fi

docker run \
    --rm \
    --volume "$VOLUME_PATH" \
    --volume /app/.venv \
    --publish 8000:8000 \
    -e IS_DOCKER=True \
    -e DB_HOST=host.docker.internal \
    -e REDIS_HOST=host.docker.internal \
    -e WORKERS=4 \
    $INTERACTIVE \
    $(docker build -q .) \
    "$@"
