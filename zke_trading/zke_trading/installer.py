import os
import subprocess
import json
from pathlib import Path


INSTALL_DIR = Path.home() / ".zke-trading"
PLUGIN_DIR = Path.home() / ".openclaw/plugins/zke-trading"


def install():

    print("Installing ZKE Trading Skill")

    api_key = input("ZKE API Key: ")
    api_secret = input("ZKE API Secret: ")

    config = {
        "spot": {
            "base_url": "https://openapi.zke.com",
            "api_key": api_key,
            "api_secret": api_secret,
            "recv_window": 5000,
        },
        "futures": {
            "base_url": "https://futuresopenapi.zke.com",
            "api_key": api_key,
            "api_secret": api_secret,
            "recv_window": 5000,
        },
        "ws": {"url": "wss://ws.zke.com/kline-api/ws"},
    }

    INSTALL_DIR.mkdir(exist_ok=True)

    config_path = INSTALL_DIR / "config.json"

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print("config.json written:", config_path)

    print("Copying OpenClaw plugin")

    os.makedirs(PLUGIN_DIR, exist_ok=True)

    subprocess.run(
        f"cp -r openclaw/* {PLUGIN_DIR}",
        shell=True,
    )

    start = input("Start MCP server now? (y/n): ")

    if start.lower() == "y":
        subprocess.Popen(
            ["python", "mcp_server.py"],
            cwd=INSTALL_DIR,
        )

        print("MCP server started")

    print("Done.")
