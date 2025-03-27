## Installation
- Install `locust` by following its official [documentation](https://locust.io/#install) for installation.
    - If the installation runs into this error: `ERROR Could not build wheels for greenlet which is required to install pyproject toml-based projects`, try the following command:
      - `pip install --only-binary :all: locust`
## Testing
- Go into `locust/` directory, make sure `locustfile.py` file is under the current directory, then run `locust`.