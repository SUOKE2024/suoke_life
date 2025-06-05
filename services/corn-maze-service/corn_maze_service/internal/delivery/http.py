"""
HTTP API 交付层

提供 FastAPI HTTP 接口。
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
import logging
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from corn_maze_service.config import get_settings
from corn_maze_service.internal.model.maze import (
    Maze,
    MazeDifficulty,
    MazeNode,
    MazeProgress,
    MazeTheme,
    NodeType,
    ProgressStatus,
)

logger = logging.getLogger(__name__)

# 内存存储（生产环境应使用数据库）
_maze_storage: dict[str, Maze] = {}
_progress_storage: dict[tuple[str, str], MazeProgress] = {}  # (user_id, maze_id) -> progress

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(description="服务状态")
    version: str = Field(description="服务版本")
    timestamp: str = Field(description="检查时间")

class ReadinessResponse(BaseModel):
    """就绪检查响应"""
    status: str = Field(description="就绪状态")
    checks: dict[str, str] = Field(description="检查项目")

class MazeCreateRequest(BaseModel):
    """创建迷宫请求"""
    name: str = Field(description="迷宫名称", min_length=1, max_length=100)
    description: str | None = Field(default=None, description="迷宫描述", max_length=500)
    size: int = Field(default=20, description="迷宫大小", ge=5, le=100)
    theme: str = Field(default="health", description="迷宫主题")
    difficulty: str = Field(default="normal", description="难度级别")

class MazeUpdateRequest(BaseModel):
    """更新迷宫请求"""
    name: str | None = Field(default=None, description="迷宫名称", min_length=1, max_length=100)
    description: str | None = Field(default=None, description="迷宫描述", max_length=500)
    difficulty: str | None = Field(default=None, description="难度级别")

class MazeResponse(BaseModel):
    """迷宫响应"""
    id: str = Field(description="迷宫ID")
    name: str = Field(description="迷宫名称")
    description: str | None = Field(description="迷宫描述")
    size: int = Field(description="迷宫大小")
    theme: str = Field(description="迷宫主题")
    difficulty: str = Field(description="难度级别")
    created_at: str = Field(description="创建时间")
    updated_at: str = Field(description="更新时间")

class MazeListResponse(BaseModel):
    """迷宫列表响应"""
    items: list[MazeResponse] = Field(description="迷宫列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页")
    size: int = Field(description="页大小")

class StartMazeRequest(BaseModel):
    """开始迷宫请求"""
    user_id: str = Field(description="用户ID")

class MoveRequest(BaseModel):
    """移动请求"""
    user_id: str = Field(description="用户ID")
    direction: str = Field(description="移动方向", pattern="^(up|down|left|right)$")

class MoveResponse(BaseModel):
    """移动响应"""
    current_position: tuple[int, int] = Field(description="当前位置")
    valid_move: bool = Field(description="是否有效移动")
    message: str | None = Field(default=None, description="移动消息")

class ProgressResponse(BaseModel):
    """进度响应"""
    user_id: str = Field(description="用户ID")
    maze_id: str = Field(description="迷宫ID")
    status: str = Field(description="进度状态")
    current_position: tuple[int, int] = Field(description="当前位置")
    visited_nodes: list[tuple[int, int]] = Field(description="已访问节点")
    collected_items: list[str] = Field(description="收集的物品")
    score: int = Field(description="得分")
    steps_count: int = Field(description="步数")

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(description="错误类型")
    message: str = Field(description="错误消息")
    details: dict[str, Any] | None = Field(default=None, description="错误详情")

def _create_simple_maze(name: str, description: str | None, size: int, theme: str, difficulty: str) -> Maze:
    """创建简单迷宫"""
    creator_id = uuid4()

    # 验证主题和难度
    try:
        maze_theme = MazeTheme(theme)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid theme: {theme}. Valid themes: {[t.value for t in MazeTheme]}"
        )

    try:
        maze_difficulty = MazeDifficulty(difficulty)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid difficulty: {difficulty}. Valid difficulties: {[d.value for d in MazeDifficulty]}"
        )

    # 创建节点矩阵
    nodes = []
    for y in range(size):
        row = []
        for x in range(size):
            if x == 0 and y == 0:
                node_type = NodeType.START
            elif x == size-1 and y == size-1:
                node_type = NodeType.END
            elif (x + y) % 4 == 0 and x > 0 and y > 0:
                node_type = NodeType.KNOWLEDGE
            elif (x + y) % 6 == 0 and x > 0 and y > 0:
                node_type = NodeType.CHALLENGE
            elif (x + y) % 3 == 0:
                node_type = NodeType.WALL
            else:
                node_type = NodeType.PATH

            node = MazeNode(x=x, y=y, node_type=node_type)
            row.append(node)
        nodes.append(row)

    return Maze(
        name=name,
        description=description,
        size=size,
        theme=maze_theme,
        difficulty=maze_difficulty,
        creator_id=creator_id,
        nodes=nodes,
        start_position=(0, 0),
        end_position=(size-1, size-1)
    )

def _maze_to_response(maze: Maze) -> MazeResponse:
    """将迷宫模型转换为响应"""
    return MazeResponse(
        id=str(maze.id),
        name=maze.name,
        description=maze.description,
        size=maze.size,
        theme=maze.theme.value if hasattr(maze.theme, 'value') else str(maze.theme),
        difficulty=maze.difficulty.value if hasattr(maze.difficulty, 'value') else str(maze.difficulty),
        created_at=maze.created_at.isoformat(),
        updated_at=maze.updated_at.isoformat()
    )

def _progress_to_response(progress: MazeProgress) -> ProgressResponse:
    """将进度模型转换为响应"""
    return ProgressResponse(
        user_id=str(progress.user_id),
        maze_id=str(progress.maze_id),
        status=progress.status.value if hasattr(progress.status, 'value') else str(progress.status),
        current_position=progress.current_position,
        visited_nodes=progress.visited_nodes,
        collected_items=progress.collected_items,
        score=progress.score,
        steps_count=progress.steps_count
    )

def create_app(settings: Any = None) -> FastAPI:
    """创建 FastAPI 应用"""
    if settings is None:
        settings = get_settings()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
        logger.info("HTTP API starting")
        yield
        logger.info("HTTP API shutting down")

    app = FastAPI(
        title="Corn Maze Service API",
        description="索克生活迷宫探索微服务 API",
        version=settings.app_version,
        docs_url="/docs" if settings.is_development() else None,
        redoc_url="/redoc" if settings.is_development() else None,
        openapi_url="/openapi.json" if settings.is_development() else None,
        lifespan=lifespan,
    )

    # 添加中间件
    setup_middleware(app, settings)

    # 添加路由
    setup_routes(app)

    # 添加异常处理器
    setup_exception_handlers(app)

    return app

def setup_middleware(app: FastAPI, settings: Any) -> None:
    """设置中间件"""
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.cors_origins,
        allow_credentials=True,
        allow_methods=settings.security.cors_methods,
        allow_headers=settings.security.cors_headers,
    )

    # 可信主机中间件
    if settings.is_production():
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # 在生产环境中应该配置具体的主机
        )

def setup_routes(app: FastAPI) -> None:
    """设置路由"""

    @app.get("/health", response_model=HealthResponse, tags=["健康检查"])
    async def health_check() -> HealthResponse:
        """健康检查端点"""
        settings = get_settings()
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            timestamp=datetime.now(UTC).isoformat()
        )

    @app.get("/ready", response_model=ReadinessResponse, tags=["健康检查"])
    async def readiness_check() -> ReadinessResponse:
        """就绪检查端点"""
        return ReadinessResponse(
            status="ready",
            checks={
                "storage": "ok",
                "api": "ok"
            }
        )

    @app.get("/", tags=["根路径"])
    async def root() -> dict[str, str]:
        """根路径"""
        return {"message": "Corn Maze Service API"}

    # 迷宫相关路由
    @app.post("/api/v1/mazes", response_model=MazeResponse, status_code=status.HTTP_201_CREATED, tags=["迷宫管理"])
    async def create_maze(request: MazeCreateRequest) -> MazeResponse:
        """创建新迷宫"""
        logger.info("Creating maze: %s (size: %d)", request.name, request.size)

        maze = _create_simple_maze(
            name=request.name,
            description=request.description,
            size=request.size,
            theme=request.theme,
            difficulty=request.difficulty
        )

        _maze_storage[str(maze.id)] = maze
        return _maze_to_response(maze)

    @app.get("/api/v1/mazes", response_model=MazeListResponse, tags=["迷宫管理"])
    async def list_mazes(
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(10, ge=1, le=100, description="页大小"),
        theme: str | None = Query(None, description="主题过滤"),
        difficulty: str | None = Query(None, description="难度过滤"),
    ) -> MazeListResponse:
        """获取迷宫列表"""
        logger.info("Listing mazes: page=%d, size=%d, theme=%s, difficulty=%s", page, size, theme, difficulty)

        # 过滤迷宫
        filtered_mazes = []
        for maze in _maze_storage.values():
            maze_theme = maze.theme.value if hasattr(maze.theme, 'value') else str(maze.theme)
            maze_difficulty = maze.difficulty.value if hasattr(maze.difficulty, 'value') else str(maze.difficulty)

            if theme and maze_theme != theme:
                continue
            if difficulty and maze_difficulty != difficulty:
                continue
            filtered_mazes.append(maze)

        # 分页
        total = len(filtered_mazes)
        start = (page - 1) * size
        end = start + size
        page_mazes = filtered_mazes[start:end]

        return MazeListResponse(
            items=[_maze_to_response(maze) for maze in page_mazes],
            total=total,
            page=page,
            size=size
        )

    @app.get("/api/v1/mazes/{maze_id}", response_model=MazeResponse, tags=["迷宫管理"])
    async def get_maze(maze_id: str) -> MazeResponse:
        """获取特定迷宫详情"""
        logger.info("Getting maze: %s", maze_id)

        if maze_id not in _maze_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Maze {maze_id} not found"
            )

        return _maze_to_response(_maze_storage[maze_id])

    @app.put("/api/v1/mazes/{maze_id}", response_model=MazeResponse, tags=["迷宫管理"])
    async def update_maze(maze_id: str, request: MazeUpdateRequest) -> MazeResponse:
        """更新迷宫"""
        logger.info("Updating maze: %s", maze_id)

        if maze_id not in _maze_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Maze {maze_id} not found"
            )

        maze = _maze_storage[maze_id]

        # 更新字段
        if request.name is not None:
            maze.name = request.name
        if request.description is not None:
            maze.description = request.description
        if request.difficulty is not None:
            try:
                maze.difficulty = MazeDifficulty(request.difficulty)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid difficulty: {request.difficulty}. Valid difficulties: {[d.value for d in MazeDifficulty]}"
                )

        maze.updated_at = datetime.now(UTC)
        return _maze_to_response(maze)

    @app.delete("/api/v1/mazes/{maze_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["迷宫管理"])
    async def delete_maze(maze_id: str) -> None:
        """删除迷宫"""
        logger.info("Deleting maze: %s", maze_id)

        if maze_id not in _maze_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Maze {maze_id} not found"
            )

        del _maze_storage[maze_id]

    # 进度相关路由
    @app.post("/api/v1/mazes/{maze_id}/start", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED, tags=["进度管理"])
    async def start_maze(maze_id: str, request: StartMazeRequest) -> ProgressResponse:
        """开始迷宫"""
        logger.info("Starting maze: %s for user: %s", maze_id, request.user_id)

        if maze_id not in _maze_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Maze {maze_id} not found"
            )

        maze = _maze_storage[maze_id]
        progress = MazeProgress(
            user_id=request.user_id,
            maze_id=maze_id,
            current_position=maze.start_position,
            status=ProgressStatus.IN_PROGRESS
        )
        progress.add_visited_node(*maze.start_position)

        _progress_storage[(request.user_id, maze_id)] = progress
        return _progress_to_response(progress)

    @app.post("/api/v1/mazes/{maze_id}/move", response_model=MoveResponse, tags=["进度管理"])
    async def move_in_maze(maze_id: str, request: MoveRequest) -> MoveResponse:
        """在迷宫中移动"""
        logger.info("Moving in maze: %s, user: %s, direction: %s", maze_id, request.user_id, request.direction)

        if maze_id not in _maze_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Maze {maze_id} not found"
            )

        progress_key = (request.user_id, maze_id)
        if progress_key not in _progress_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Progress not found for user {request.user_id} in maze {maze_id}"
            )

        maze = _maze_storage[maze_id]
        progress = _progress_storage[progress_key]
        current_x, current_y = progress.current_position

        # 计算新位置
        direction_map = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0)
        }

        dx, dy = direction_map[request.direction]
        new_x, new_y = current_x + dx, current_y + dy

        # 检查边界
        if not (0 <= new_x < maze.size and 0 <= new_y < maze.size):
            return MoveResponse(
                current_position=progress.current_position,
                valid_move=False,
                message="Cannot move outside maze boundaries"
            )

        # 检查是否是墙
        node = maze.get_node(new_x, new_y)
        if node and node.node_type == NodeType.WALL:
            return MoveResponse(
                current_position=progress.current_position,
                valid_move=False,
                message="Cannot move through wall"
            )

        # 有效移动
        progress.current_position = (new_x, new_y)
        progress.add_visited_node(new_x, new_y)

        # 检查是否到达终点
        if (new_x, new_y) == maze.end_position:
            progress.complete_maze()

        return MoveResponse(
            current_position=progress.current_position,
            valid_move=True,
            message="Move successful"
        )

    @app.get("/api/v1/mazes/{maze_id}/progress/{user_id}", response_model=ProgressResponse, tags=["进度管理"])
    async def get_progress(maze_id: str, user_id: str) -> ProgressResponse:
        """获取进度"""
        logger.info("Getting progress: maze=%s, user=%s", maze_id, user_id)

        progress_key = (user_id, maze_id)
        if progress_key not in _progress_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Progress not found for user {user_id} in maze {maze_id}"
            )

        return _progress_to_response(_progress_storage[progress_key])

def setup_exception_handlers(app: FastAPI) -> None:
    """设置异常处理器"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Any, exc: HTTPException) -> JSONResponse:
        """HTTP 异常处理器"""
        logger.warning("HTTP exception: %s (status: %d)", exc.detail, exc.status_code)

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error="HTTP_ERROR",
                message=exc.detail,
                details={"status_code": exc.status_code}
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(_request: Any, exc: Exception) -> JSONResponse:
        """通用异常处理器"""
        logger.error("Unhandled exception: %s", str(exc), exc_info=True)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Internal server error",
                details={"type": type(exc).__name__}
            ).model_dump()
        )
