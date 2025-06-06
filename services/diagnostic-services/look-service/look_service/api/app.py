"""
app - 索克生活项目模块
"""

        from .models import ComplexionAnalysis
        from .models import TongueAnalysis
    from datetime import datetime
    import uuid
from ..core.config import settings
from ..core.logging import get_logger
from ..exceptions import setup_exception_handlers
from ..middleware import (
from .models import FHIRObservationResponse, LookDiagnosisRequest, LookDiagnosisResult
from .routes import api_router
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import make_asgi_app

"""FastAPI application factory."""



    LoggingMiddleware,
    MetricsMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Look Service")

    # Initialize services, connections, etc.
    # TODO: Add database connections, ML model loading, etc.

    logger.info("Look Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Look Service")

    # Cleanup resources
    # TODO: Close database connections, cleanup ML models, etc.

    logger.info("Look Service shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Look Service",
        description="索克生活望诊微服务 - 基于计算机视觉的中医望诊智能分析系统",
        version=settings.service.service_version,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # Setup exception handlers
    setup_exception_handlers(app)

    # Add middleware
    setup_middleware(app)

    # Include routers
    app.include_router(api_router, prefix="/api/v1")

    # Add metrics endpoint
    if settings.monitoring.enable_metrics:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "service": "look-service"}

    # Readiness check endpoint
    @app.get("/ready")
    async def readiness_check() -> dict[str, str]:
        """Readiness check endpoint."""
        # TODO: Add actual readiness checks (database, ML models, etc.)
        return {"status": "ready", "service": "look-service"}

    # 仅暴露标准化诊断API，不处理前端交互
    @app.post("/api/v1/diagnose/look", response_model=FHIRObservationResponse)
    def diagnose_look(data: LookDiagnosisRequest):
        """望诊分析，返回FHIR Observation格式"""
        # 只做算法分析和标准化结果封装
        result = look_diagnosis_algorithm(data)
        fhir_obs = to_fhir_observation_look(data.user_id, result)
        return FHIRObservationResponse(**fhir_obs)

    logger.info("FastAPI application created")
    return app


def setup_middleware(app: FastAPI) -> None:
    """Setup middleware for the application.

    Args:
        app: FastAPI application instance
    """
    # Security middleware (should be first)
    app.add_middleware(SecurityMiddleware)

    # Trusted host middleware
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Configure based on your needs
        )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.service.cors_origins,
        allow_credentials=True,
        allow_methods=settings.service.cors_methods,
        allow_headers=settings.service.cors_headers,
    )

    # Rate limiting middleware
    app.add_middleware(RateLimitMiddleware)

    # Metrics middleware
    if settings.monitoring.enable_metrics:
        app.add_middleware(MetricsMiddleware)

    # Logging middleware (should be last)
    app.add_middleware(LoggingMiddleware)

    logger.info("Middleware configured")


def look_diagnosis_algorithm(data: LookDiagnosisRequest) -> LookDiagnosisResult:
    """
    望诊分析算法（占位符实现）
    
    Args:
        data: 望诊请求数据
        
    Returns:
        望诊分析结果
    """
    
    # 这是一个占位符实现，实际应该调用真正的望诊算法
    result = LookDiagnosisResult(
        analysis_id=str(uuid.uuid4()),
        user_id=data.user_id,
        timestamp=datetime.now(),
        image_type=data.image_type,
        overall_score=75.0,
        health_status="正常",
        recommendations=["保持良好作息", "均衡饮食"]
    )
    
    # 根据分析类型添加具体分析结果
    if "complexion" in data.analysis_type:
        result.complexion = ComplexionAnalysis(
            color_type="正常",
            confidence=0.8,
            characteristics=["面色红润"],
            health_implications=["气血充足"]
        )
    
    if "tongue" in data.analysis_type:
        result.tongue = TongueAnalysis(
            tongue_body={"color": "淡红", "texture": "正常"},
            tongue_coating={"color": "薄白", "texture": "润泽"},
            overall_assessment="舌象正常",
            confidence=0.75
        )
    
    return result


def to_fhir_observation_look(user_id: str, result: LookDiagnosisResult) -> dict:
    """
    将望诊结果转换为FHIR Observation格式
    
    Args:
        user_id: 用户ID
        result: 望诊分析结果
        
    Returns:
        FHIR Observation格式的数据
    """
    components = []
    
    # 添加面色分析组件
    if result.complexion:
        components.append({
            "code": {
                "coding": [{
                    "system": "http://suoke.life/fhir/CodeSystem/tcm-look",
                    "code": "complexion",
                    "display": "面色"
                }]
            },
            "valueCodeableConcept": {
                "coding": [{
                    "system": "http://suoke.life/fhir/CodeSystem/tcm-complexion",
                    "code": result.complexion.color_type.lower(),
                    "display": result.complexion.color_type
                }]
            }
        })
    
    # 添加舌诊分析组件
    if result.tongue:
        components.append({
            "code": {
                "coding": [{
                    "system": "http://suoke.life/fhir/CodeSystem/tcm-look",
                    "code": "tongue",
                    "display": "舌诊"
                }]
            },
            "valueString": result.tongue.overall_assessment
        })
    
    return {
        "resourceType": "Observation",
        "id": result.analysis_id,
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "survey",
                "display": "Survey"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://suoke.life/fhir/CodeSystem/tcm-observation",
                "code": "look-diagnosis",
                "display": "中医望诊"
            }]
        },
        "subject": {
            "reference": f"Patient/{user_id}"
        },
        "effectiveDateTime": result.timestamp.isoformat(),
        "component": components,
        "note": [{
            "text": f"健康状态: {result.health_status}, 评分: {result.overall_score}"
        }]
    }
