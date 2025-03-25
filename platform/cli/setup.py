import setuptools

setuptools.setup(
    entry_points={
    'console_scripts': [
        'blue = blue_cli.blue:cli'
    ]
    },
    packages=setuptools.find_packages(),
    install_requires = [
        "blue-platform==0.8.13",
        "click==8.1.7",
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
    ]
)