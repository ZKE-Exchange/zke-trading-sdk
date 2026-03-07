from setuptools import setup, find_packages

setup(
    name="zke-trading",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "websocket-client"
    ],
    entry_points={
        "console_scripts": [
            "zke=zke_trading.cli:main"
        ]
    },
)
