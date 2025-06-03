"""
HTTP API 服务

使用 FastAPI 提供 RESTful API 接口。
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC
from typing import Any

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from corn_maze_service.config import get_settings
from corn_maze_service.pkg.logging import get_logger

logger = get_logger(__name__)

# API 模型定义
class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(description="服务状态")
    version: str = Field(description="服务版本")
    timestamp: str = Field(description="检查时间")

class MazeCreateRequest(BaseModel):
    """创建迷宫请求"""
    name: str = Field(description="迷宫名称", min_length=1, max_length=100)
    description: str | None = Field(default=None, description="迷宫描述", max_length=500)
    size: int = Field(default=20, description="迷宫大小", ge=5, le=100)
    theme: str = Field(default="health", description="迷宫主题")
    difficulty: str = Field(default="normal", description="难度级别")
    is_public: bool = Field(default=False, description="是否公开")

class MazeResponse(BaseModel):
    """迷宫响应"""
    id: str = Field(description="迷宫ID")
    name: str = Field(description="迷宫名称")
    description: str | None = Field(description="迷宫描述")
    size: int = Field(description="迷宫大小")
    theme: str = Field(description="迷宫主题")
    difficulty: str = Field(description="难度级别")
    is_public: bool = Field(description="是否公开")
    created_at: str = Field(description="创建时间")
    updated_at: str = Field(description="更新时间")

class MazeListResponse(BaseModel):
    """迷宫列表响应"""
    mazes: list[MazeResponse] = Field(description="迷宫列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页")
    size: int = Field(description="页大小")

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(description="错误类型")
    message: str = Field(description="错误消息")
    details: dict[str, Any] | None = Field(default=None, description="错误详情")

def create_app(lifespan: Any = None) -> FastAPI:
    """创建 FastAPI 应用"""
    settings = get_settings()

    if lifespan is None:
        @asynccontextmanager
        async def default_lifespan(_app: FastAPI) -> AsyncGenerator[None]:
            logger.info("HTTP API starting")
            yield
            logger.info("HTTP API shutting down")

        lifespan = default_lifespan

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
        from datetime import datetime
        settings = get_settings()

        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            timestamp=datetime.now(UTC).isoformat()
        )

    @app.get("/", tags=["根路径"])
    async def root() -> dict[str, str]:
        """根路径"""
        return {"message": "Corn Maze Service API"}

    # 迷宫相关路由
    @app.post("/api/v1/mazes", response_model=MazeResponse, status_code=status.HTTP_201_CREATED, tags=["迷宫管理"])
    async def create_maze(request: MazeCreateRequest) -> MazeResponse:
        """创建新迷宫"""
        # TODO: 实现迷宫创建逻辑
        logger.info("Creating maze", name=request.name, size=request.size)

        # 临时返回示例数据
        from datetime import datetime
        import uuid

        return MazeResponse(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            size=request.size,
            theme=request.theme,
            difficulty=request.difficulty,
            is_public=request.is_public,
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat()
        )

    @app.get("/api/v1/mazes", response_model=MazeListResponse, tags=["迷宫管理"])
    async def list_mazes(
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(10, ge=1, le=100, description="页大小"),
        theme: str | None = Query(None, description="主题过滤"),
        difficulty: str | None = Query(None, description="难度过滤"),
    ) -> MazeListResponse:
        """获取迷宫列表"""
        # TODO: 实现迷宫列表查询逻辑
        logger.info("Listing mazes", page=page, size=size, theme=theme, difficulty=difficulty)

        # 临时返回示例数据
        return MazeListResponse(
            mazes=[],
            total=0,
            page=page,
            size=size
        )

    @app.get("/api/v1/mazes/{maze_id}", response_model=MazeResponse, tags=["迷宫管理"])
    async def get_maze(maze_id: str) -> MazeResponse:
        """获取特定迷宫详情"""
        # TODO: 实现迷宫详情查询逻辑
        logger.info("Getting maze", maze_id=maze_id)

        # 临时抛出未找到错误
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maze {maze_id} not found"
        )

    @app.delete("/api/v1/mazes/{maze_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["迷宫管理"], response_model=None)
    async def delete_maze(maze_id: str) -> None:
        """删除迷宫"""
        # TODO: 实现迷宫删除逻辑
        logger.info("Deleting maze", maze_id=maze_id)

        # 临时抛出未找到错误
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maze {maze_id} not found"
        )

def setup_exception_handlers(app: FastAPI) -> None:
    """设置异常处理器"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Any, exc: HTTPException) -> JSONResponse:
        """HTTP 异常处理器"""
        logger.warning("HTTP exception", status_code=exc.status_code, detail=exc.detail)

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
        logger.error("Unhandled exception", error=str(exc), exc_info=True)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="INTERNAL_ERROR",
                message="Internal server error",
                details={"type": type(exc).__name__}
            ).model_dump()
        )
