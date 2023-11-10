find . -maxdepth 1 -type d \( ! -name . \) -exec bash -c "cd '{}' && ./docker_build_agent.sh" \;
