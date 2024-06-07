from pathlib import Path

from setuptools import find_packages, setup

version = Path("./blue/version").read_text().strip()
package = {
    "name": "blue",
    "version": version,
    "description": "Blue CLI",
    "packages": find_packages(),
    "entry_points": {"console_scripts": ["blue = blue.blue:cli"]},
    "install_requires": [
        "python-dotenv==1.0.0",
        "click==8.1.7",
        "tabulate==0.9.0",
        "requests==2.31.0",
        "websockets==11.0.3",
        "nest_asyncio",
        "pandas"
    ],
    "python_requires": ">=3.9",  
}
setup(**package)
