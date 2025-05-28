"""
Pytest 配置文件

提供测试夹具和配置。
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
import tempfile
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from corn_maze_service.config import Settings, get_settings
from corn_maze_service.internal.delivery.http import create_app
from corn_maze_service.pkg.logging import setup_logging


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
def test_settings(temp_dir: Path) -> Settings:
    """测试设置"""
    return Settings(
        app_name="Corn Maze Service Test",
        app_version="0.2.0-test",
        debug=True,
        environment="testing",
        database={"url": f"sqlite:///{temp_dir}/test.db"},
        redis={"url": "redis://localhost:6379/15"},  # 使用测试数据库
        grpc={"port": 50058},  # 使用不同端口避免冲突
        http={"port": 51058},
        monitoring={"prometheus_port": 51059, "log_level": "DEBUG"},
    )


@pytest.fixture
def mock_settings(test_settings: Settings) -> Generator[Settings]:
    """模拟设置"""
    original_get_settings = get_settings

    def _get_test_settings():
        return test_settings

    # 替换设置函数
    import corn_maze_service.config
    corn_maze_service.config.get_settings = _get_test_settings

    yield test_settings

    # 恢复原始设置
    corn_maze_service.config.get_settings = original_get_settings


@pytest.fixture
def app(mock_settings: Settings) -> FastAPI:
    """创建测试应用"""
    setup_logging()
    return create_app()


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
async def sample_maze():
    """示例迷宫数据"""
    from uuid import uuid4

    from corn_maze_service.internal.model import (
        Maze,
        MazeDifficulty,
        MazeNode,
        MazeTheme,
        NodeType,
    )

    # 创建简单的 3x3 迷宫
    nodes = []
    for y in range(3):
        row = []
        for x in range(3):
            if x == 0 and y == 0:
                node_type = NodeType.START
            elif x == 2 and y == 2:
                node_type = NodeType.END
            elif (x + y) % 2 == 0:
                node_type = NodeType.PATH
            else:
                node_type = NodeType.WALL

            row.append(MazeNode(
                x=x,
                y=y,
                node_type=node_type
            ))
        nodes.append(row)

    return Maze(
        name="Test Maze",
        description="A test maze",
        size=3,
        theme=MazeTheme.HEALTH,
        difficulty=MazeDifficulty.EASY,
        creator_id=uuid4(),
        nodes=nodes,
        start_position=(0, 0),
        end_position=(2, 2),
        total_nodes=9,
        knowledge_nodes=0,
        challenge_nodes=0
    )


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
