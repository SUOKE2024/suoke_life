import httpx
from .core.app import create_app, create_dev_app
from .core.config import Settings, get_settings, create_settings_from_file
from .core.logging import get_logger, setup_logging
from pathlib import Path
from rich.console import Console
from rich.table import Table
from typing import Optional
import asyncio
import click
import signal
import sys
import uvicorn

def main() -> None:
    """主函数 - 自动生成的最小可用版本"""
    pass

if __name__ == "__main__":
    main()
