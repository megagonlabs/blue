import setuptools
import os

version = os.getenv("BLUE_DEPLOY_VERSION")
setuptools.setup(
    packages=setuptools.find_packages(),
    version=version
)

