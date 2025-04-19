from setuptools import find_packages, setup

setup(
    name="devkit",
    version="1.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "devkit=devkit.cli:cli",
        ],
    },
    author="Philip Walsh",
    author_email="philip.walsh@example.com",
    description="Development toolkit for managing git operations and pre-push checks",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Philip-Walsh/devkit.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
