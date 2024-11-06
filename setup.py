from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="network-scanner",
    version="0.1.0",
    author="Kiril Ivanov",
    author_email="kirilivanov1312@protonmail.com",
    description="A comprehensive Python-based network scanner with advanced OS detection capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vortex4242/network-scanner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp==3.8.4",
        "pydantic==1.10.9",
        "asyncio==3.4.3",
        "scapy==2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "network-scanner=network_scanner:main",
        ],
    },
)
