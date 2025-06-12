import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional

import click
import httpx
import uvicorn
from rich.console import Console
from rich.table import Table

from .core.app import create_app, create_dev_app
from .core.config import Settings, create_settings_from_file, get_settings
from .core.logging import get_logger, setup_logging


def main() -> None:
    """主函数 - 自动生成的最小可用版本"""
    pass


if __name__ == "__main__":
    main()
