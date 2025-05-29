"""
Pytest 配置文件

提供测试夹具和配置。
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
import sys
import tempfile
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from corn_maze_service.config import Settings, get_settings
from corn_maze_service.constants import MAZE_END_X, MAZE_END_Y
from corn_maze_service.internal.delivery.http import create_app
from corn_maze_service.internal.model.maze import Maze, MazeNode, NodeType
from corn_maze_service.pkg.logging import setup_logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def temp_dir() -> Generator[Path]:
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def settings():
    """测试设置"""
    return Settings(
        environment="test",
        database={"url": "sqlite:///:memory:"},
        redis={"url": "redis://localhost:6379/1"},
    )


@pytest.fixture
def mock_settings(settings: Settings) -> Generator[Settings]:
    """模拟设置"""
    original_get_settings = get_settings

    def _get_test_settings():
        return settings

    # 替换设置函数
    import corn_maze_service.config
    corn_maze_service.config.get_settings = _get_test_settings

    yield settings

    # 恢复原始设置
    corn_maze_service.config.get_settings = original_get_settings


@pytest.fixture
def app(mock_settings: Settings) -> FastAPI:
    """创建测试应用"""
    setup_logging()
    return create_app(mock_settings)


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[TestClient]:
    """创建异步测试客户端"""
    async with TestClient(app) as client:
        yield client


# 数据库相关夹具
@pytest.fixture
async def db_session():
    """数据库会话"""
    # TODO: 实现数据库会话创建
    pass


@pytest.fixture
def sample_maze():
    """示例迷宫"""
    # 创建一个简单的3x3迷宫
    nodes = []
    for x in range(3):
        for y in range(3):
            if x == 0 and y == 0:
                node_type = NodeType.START
            elif x == MAZE_END_X and y == MAZE_END_Y:
                node_type = NodeType.END
            elif (x + y) % 2 == 0:
                node_type = NodeType.PATH
            else:
                node_type = NodeType.WALL

            node = MazeNode(
                x=x,
                y=y,
                type=node_type,
                connections=[]
            )
            nodes.append(node)

    maze = Maze(
        id="test-maze-1",
        name="测试迷宫",
        description="用于测试的简单迷宫",
        theme="health",
        difficulty="easy",
        size_x=3,
        size_y=3,
        nodes=nodes,
        start_x=0,
        start_y=0,
        end_x=MAZE_END_X,
        end_y=MAZE_END_Y
    )

    return maze


# Mock 相关夹具
@pytest.fixture
def mock_openai():
    """模拟 OpenAI 客户端"""
    mock = AsyncMock()
    mock.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content="Mock AI response"
                )
            )
        ]
    )
    return mock


@pytest.fixture
def mock_redis():
    """模拟 Redis 客户端"""
    mock = AsyncMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = 1
    return mock


# 标记定义
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.slow = pytest.mark.slow
