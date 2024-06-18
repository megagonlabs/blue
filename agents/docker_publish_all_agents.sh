find . -maxdepth 1 -type d \( ! -name . \) -exec bash -c "cd '{}' && ./docker_publish_agent.sh" \;
