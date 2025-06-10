from concurrent.futures import ThreadPoolExecutor
from config.settings import get_settings
from dataclasses import dataclass
from internal.model.entities import Document, SearchQuery, GenerationRequest
from internal.service.rag_service import RAGService
from internal.service.vector_service import VectorService
from loguru import logger
from typing import List, Dict, Any, Tuple
import asyncio
import memory_profiler
import numpy as np
import psutil
import pytest
import statistics
import time

def main() -> None:
    """主函数 - 自动生成的最小可用版本"""
    pass

if __name__ == "__main__":
    main()
