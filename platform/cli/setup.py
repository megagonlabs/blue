import setuptools
import os
version = os.getenv("BLUE_DEPLOY_VERSION")

setuptools.setup(
    entry_points={'console_scripts': ['blue = blue_cli.blue:cli']},
    packages=setuptools.find_packages(),
    version=version,
    install_requires=[
        "blue-platform==" + str(version),
        "click==8.2.1",
        "tabulate==0.9.0",
        "requests==2.31.0",
        "websockets==11.0.3",
        "nest_asyncio==1.6.0",
        "traitlets==5.14.3",
        "pydash==7.0.6",
        "pandas==2.2.3",
        "jsonmerge==1.9.2",
        "jsonpath-ng==1.5.3",
        "jsonschema==4.21.1",
        "redis==5.2.0",
        "docker==7.0.0",
        "uuid==1.30",
    ],
)
