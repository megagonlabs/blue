import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="blue-py",
    version="0.9",
    author="megagon labs",
    author_email="contact@megagon.ai",
    description="blue py - python library for blue streaming framework for agentic orchestration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/megagonlabs/blue",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD-3 Clause License",
        "Operating System :: OS Independent",
    ],
)

