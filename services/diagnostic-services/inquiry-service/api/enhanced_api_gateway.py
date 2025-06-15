"""
增强的API网关 - 提供REST API接口
"""

from contextlib import asynccontextmanager
import logging
import os
import time
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import yaml

# 导入内部模块
from internal.dialogue.dialogue_manager import DialogueManager
from internal.extractors.symptom_extractor import OptimizedSymptomExtractor
from internal.knowledge.tcm_knowledge_base import TCMKnowledgeBase
from internal.llm.health_risk_assessor import HealthRiskAssessor
from internal.llm.llm_client import LLMClient
from internal.llm.tcm_pattern_mapper import TCMPatternMapper
from internal.repository.session_repository import SessionRepository
from internal.repository.user_repository import UserRepository

logger = logging.getLogger(__name__)

# 全局变量存储服务组件
app_state = {}

# Pydantic模型定义
class StartSessionRequest(BaseModel):
    user_id: str = Field(..., description="用户ID")
    session_type: str = Field(default="general", description="会话类型")
    language_preference: str = Field(default="zh-CN", description="语言偏好")
    context_data: dict[str, str] | None = Field(default_factory=dict, description="上下文数据")

class SessionResponse(BaseModel):
    session_id: str
    welcome_message: str
    suggested_questions: list[str]
    timestamp: int

class InteractionRequest(BaseModel):
    session_id: str = Field(..., description="会话ID")
    user_message: str = Field(..., description="用户消息")
    attached_data_urls: list[str] | None = Field(default_factory=list, description="附加数据URL")

class InteractionResponse(BaseModel):
    response_text: str
    response_type: str
    detected_symptoms: list[str]
    follow_up_questions: list[str]
    timestamp: int

class EndSessionRequest(BaseModel):
    session_id: str = Field(..., description="会话ID")
    feedback: str | None = Field(default="", description="用户反馈")

class SymptomInfo(BaseModel):
    symptom_name: str
    severity: str
    onset_time: int
    duration: int
    description: str
    confidence: float

class TCMPattern(BaseModel):
    pattern_name: str
    category: str
    match_score: float
    related_symptoms: list[str]
    description: str

class HealthProfile(BaseModel):
    user_id: str
    constitution_type: str

class FollowUpRecommendation(BaseModel):
    type: str
    description: str
    rationale: str
    suggested_timeframe: int

class InquirySummary(BaseModel):
    session_id: str
    user_id: str
    detected_symptoms: list[SymptomInfo]
    tcm_patterns: list[TCMPattern]
    health_profile: HealthProfile
    recommendations: list[FollowUpRecommendation]
    session_duration: int
    session_end_time: int

class SymptomsExtractionRequest(BaseModel):
    text_content: str = Field(..., description="需要分析的文本内容")
    user_id: str | None = Field(default="", description="用户ID")
    language: str = Field(default="zh-CN", description="文本语言")

class SymptomsResponse(BaseModel):
    symptoms: list[SymptomInfo]
    body_locations: list[dict[str, Any]]
    temporal_factors: list[dict[str, Any]]
    confidence_score: float

class TCMPatternMappingRequest(BaseModel):
    symptoms: list[dict[str, Any]] = Field(..., description="症状列表")
    user_constitution: str | None = Field(default="", description="用户体质")
    body_locations: list[dict[str, Any]] | None = Field(default_factory=list)
    temporal_factors: list[dict[str, Any]] | None = Field(default_factory=list)

class TCMPatternResponse(BaseModel):
    primary_patterns: list[TCMPattern]
    secondary_patterns: list[TCMPattern]
    interpretation: str
    confidence_score: float

class HealthRiskRequest(BaseModel):
    user_id: str = Field(..., description="用户ID")
    current_symptoms: list[dict[str, Any]] = Field(..., description="当前症状")
    medical_history: dict[str, Any] | None = Field(default_factory=dict)
    health_profile: dict[str, Any] | None = Field(default_factory=dict)

class HealthRisk(BaseModel):
    risk_name: str
    probability: float
    severity: str
    timeframe: str
    contributing_factors: list[str]

class PreventionStrategy(BaseModel):
    strategy_name: str
    description: str
    action_items: list[str]
    targets: list[str]
    effectiveness_score: float

class HealthRiskResponse(BaseModel):
    immediate_risks: list[HealthRisk]
    long_term_risks: list[HealthRisk]
    prevention_strategies: list[PreventionStrategy]
    overall_risk_score: float

# 异常处理
class InquiryServiceException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

async def load_config() -> dict[str, Any]:
    """加载配置文件"""
    config_path = os.getenv("CONFIG_PATH", "./config/config.yaml")

    try:
        with open(config_path, encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        raise

async def initialize_services():
    """初始化所有服务组件"""
    logger.info("正在初始化服务组件...")

    # 加载配置
    config = await load_config()

    # 初始化存储库
    session_repository = SessionRepository(config)
    user_repository = UserRepository(config)

    # 初始化LLM客户端
    llm_client = LLMClient(config)

    # 初始化中医知识库
    tcm_knowledge_base = TCMKnowledgeBase(config)
    await tcm_knowledge_base.initialize()

    # 初始化症状提取器
    symptom_extractor = OptimizedSymptomExtractor(config)
    await symptom_extractor.initialize()

    # 初始化TCM证型映射器
    tcm_pattern_mapper = TCMPatternMapper(config)

    # 初始化健康风险评估器
    health_risk_assessor = HealthRiskAssessor(config)
    await health_risk_assessor.initialize()

    # 初始化对话管理器
    dialogue_manager = DialogueManager(
        llm_client=llm_client,
        session_repository=session_repository,
        user_repository=user_repository,
        config=config
    )

    # 存储到全局状态
    app_state.update({
        'config': config,
        'dialogue_manager': dialogue_manager,
        'symptom_extractor': symptom_extractor,
        'tcm_pattern_mapper': tcm_pattern_mapper,
        'health_risk_assessor': health_risk_assessor,
        'tcm_knowledge_base': tcm_knowledge_base
    })

    logger.info("所有服务组件初始化完成")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    await initialize_services()
    yield
    # 关闭时清理
    logger.info("正在清理资源...")

# 创建FastAPI应用
app = FastAPI(
    title="问诊服务 API",
    description="索克生活智能健康管理平台的问诊服务REST API",
    version="1.0.0",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# 异常处理器
@app.exception_handler(InquiryServiceException)
async def inquiry_service_exception_handler(request: Request, exc: InquiryServiceException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "timestamp": int(time.time())}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "内部服务器错误", "timestamp": int(time.time())}
    )

# 依赖注入
def get_dialogue_manager() -> DialogueManager:
    return app_state['dialogue_manager']

def get_symptom_extractor() -> OptimizedSymptomExtractor:
    return app_state['symptom_extractor']

def get_tcm_pattern_mapper() -> TCMPatternMapper:
    return app_state['tcm_pattern_mapper']

def get_health_risk_assessor() -> HealthRiskAssessor:
    return app_state['health_risk_assessor']

def get_tcm_knowledge_base() -> TCMKnowledgeBase:
    return app_state['tcm_knowledge_base']

# API路由
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": int(time.time())}

@app.post("/api/v1/sessions/start", response_model=SessionResponse)
async def start_inquiry_session(
    request: StartSessionRequest,
    dialogue_manager: DialogueManager = Depends(get_dialogue_manager)
):
    """开始问诊会话"""
    try:
        session_id, welcome_message, suggested_questions = await dialogue_manager.start_session(
            user_id=request.user_id,
            session_type=request.session_type,
            language=request.language_preference,
            context_data=request.context_data
        )

        return SessionResponse(
            session_id=session_id,
            welcome_message=welcome_message,
            suggested_questions=suggested_questions,
            timestamp=int(time.time())
        )
    except Exception as e:
        logger.error(f"开始会话失败: {e}")
        raise InquiryServiceException(f"开始会话失败: {e!s}", 500)

@app.post("/api/v1/sessions/interact", response_model=InteractionResponse)
async def interact_with_user(
    request: InteractionRequest,
    dialogue_manager: DialogueManager = Depends(get_dialogue_manager)
):
    """与用户交互"""
    try:
        response_dict = await dialogue_manager.interact(
            session_id=request.session_id,
            user_message=request.user_message,
            timestamp=int(time.time()),
            attached_data_urls=request.attached_data_urls
        )

        return InteractionResponse(
            response_text=response_dict.get("response_text", ""),
            response_type=response_dict.get("response_type", "TEXT"),
            detected_symptoms=response_dict.get("detected_symptoms", []),
            follow_up_questions=response_dict.get("follow_up_questions", []),
            timestamp=response_dict.get("timestamp", int(time.time()))
        )
    except ValueError as e:
        raise InquiryServiceException(f"会话不存在或已过期: {e!s}", 404)
    except Exception as e:
        logger.error(f"用户交互失败: {e}")
        raise InquiryServiceException(f"用户交互失败: {e!s}", 500)

@app.post("/api/v1/sessions/end", response_model=InquirySummary)
async def end_inquiry_session(
    request: EndSessionRequest,
    dialogue_manager: DialogueManager = Depends(get_dialogue_manager)
):
    """结束问诊会话"""
    try:
        summary_dict = await dialogue_manager.end_session(
            session_id=request.session_id,
            feedback=request.feedback
        )

        # 转换症状信息
        symptoms = [
            SymptomInfo(
                symptom_name=s.get("symptom_name", ""),
                severity=s.get("severity", "MODERATE"),
                onset_time=int(s.get("onset_time", 0)),
                duration=int(s.get("duration", 0)),
                description=s.get("description", ""),
                confidence=float(s.get("confidence", 0.8))
            )
            for s in summary_dict.get("detected_symptoms", [])
        ]

        # 转换TCM证型
        tcm_patterns = [
            TCMPattern(
                pattern_name=p.get("pattern_name", ""),
                category=p.get("category", ""),
                match_score=float(p.get("match_score", 0.0)),
                related_symptoms=p.get("related_symptoms", []),
                description=p.get("description", "")
            )
            for p in summary_dict.get("tcm_patterns", [])
        ]

        # 转换健康档案
        health_profile_data = summary_dict.get("health_profile", {})
        health_profile = HealthProfile(
            user_id=health_profile_data.get("user_id", ""),
            constitution_type=health_profile_data.get("constitution_type", "BALANCED")
        )

        # 转换建议
        recommendations = [
            FollowUpRecommendation(
                type=r.get("type", "MONITORING"),
                description=r.get("description", ""),
                rationale=r.get("rationale", ""),
                suggested_timeframe=int(r.get("suggested_timeframe", 0))
            )
            for r in summary_dict.get("recommendations", [])
        ]

        return InquirySummary(
            session_id=summary_dict.get("session_id", ""),
            user_id=summary_dict.get("user_id", ""),
            detected_symptoms=symptoms,
            tcm_patterns=tcm_patterns,
            health_profile=health_profile,
            recommendations=recommendations,
            session_duration=int(summary_dict.get("session_duration", 0)),
            session_end_time=int(summary_dict.get("session_end_time", 0))
        )
    except ValueError as e:
        raise InquiryServiceException(f"会话不存在或已过期: {e!s}", 404)
    except Exception as e:
        logger.error(f"结束会话失败: {e}")
        raise InquiryServiceException(f"结束会话失败: {e!s}", 500)

@app.post("/api/v1/symptoms/extract", response_model=SymptomsResponse)
async def extract_symptoms(
    request: SymptomsExtractionRequest,
    symptom_extractor: OptimizedSymptomExtractor = Depends(get_symptom_extractor)
):
    """提取症状信息"""
    try:
        result = await symptom_extractor.extract(request.text_content)

        # 转换症状信息
        symptoms = [
            SymptomInfo(
                symptom_name=s.get("name", ""),
                severity=s.get("severity", "MODERATE"),
                onset_time=0,  # 从提取结果中获取
                duration=int(s.get("duration", 0)),
                description=f"从文本中提取的症状：{s.get('name', '')}",
                confidence=float(s.get("confidence", 0.8))
            )
            for s in result.get("symptoms", [])
        ]

        return SymptomsResponse(
            symptoms=symptoms,
            body_locations=result.get("body_locations", []),
            temporal_factors=result.get("temporal_factors", []),
            confidence_score=result.get("confidence_score", 0.0)
        )
    except Exception as e:
        logger.error(f"症状提取失败: {e}")
        raise InquiryServiceException(f"症状提取失败: {e!s}", 500)

@app.post("/api/v1/tcm/patterns", response_model=TCMPatternResponse)
async def map_to_tcm_patterns(
    request: TCMPatternMappingRequest,
    tcm_pattern_mapper: TCMPatternMapper = Depends(get_tcm_pattern_mapper)
):
    """中医证型映射"""
    try:
        result = await tcm_pattern_mapper.map_to_tcm_patterns(
            symptoms=request.symptoms,
            user_constitution=request.user_constitution,
            body_locations=request.body_locations,
            temporal_factors=request.temporal_factors
        )

        # 转换主证
        primary_patterns = [
            TCMPattern(
                pattern_name=p.get("pattern_name", ""),
                category=p.get("category", ""),
                match_score=float(p.get("match_score", 0.0)),
                related_symptoms=p.get("related_symptoms", []),
                description=p.get("description", "")
            )
            for p in result.get("primary_patterns", [])
        ]

        # 转换次证
        secondary_patterns = [
            TCMPattern(
                pattern_name=p.get("pattern_name", ""),
                category=p.get("category", ""),
                match_score=float(p.get("match_score", 0.0)),
                related_symptoms=p.get("related_symptoms", []),
                description=p.get("description", "")
            )
            for p in result.get("secondary_patterns", [])
        ]

        return TCMPatternResponse(
            primary_patterns=primary_patterns,
            secondary_patterns=secondary_patterns,
            interpretation=result.get("interpretation", ""),
            confidence_score=result.get("confidence_score", 0.0)
        )
    except Exception as e:
        logger.error(f"中医证型映射失败: {e}")
        raise InquiryServiceException(f"中医证型映射失败: {e!s}", 500)

@app.post("/api/v1/health/risks", response_model=HealthRiskResponse)
async def assess_health_risks(
    request: HealthRiskRequest,
    health_risk_assessor: HealthRiskAssessor = Depends(get_health_risk_assessor)
):
    """健康风险评估"""
    try:
        result = await health_risk_assessor.assess_health_risks(
            user_id=request.user_id,
            current_symptoms=request.current_symptoms,
            medical_history=request.medical_history,
            health_profile=request.health_profile
        )

        # 转换即时风险
        immediate_risks = [
            HealthRisk(
                risk_name=r.get("risk_name", ""),
                probability=float(r.get("probability", 0.0)),
                severity=r.get("severity", "low"),
                timeframe=r.get("timeframe", "unknown"),
                contributing_factors=r.get("contributing_factors", [])
            )
            for r in result.get("immediate_risks", [])
        ]

        # 转换长期风险
        long_term_risks = [
            HealthRisk(
                risk_name=r.get("risk_name", ""),
                probability=float(r.get("probability", 0.0)),
                severity=r.get("severity", "low"),
                timeframe=r.get("timeframe", "unknown"),
                contributing_factors=r.get("contributing_factors", [])
            )
            for r in result.get("long_term_risks", [])
        ]

        # 转换预防策略
        prevention_strategies = [
            PreventionStrategy(
                strategy_name=s.get("strategy_name", ""),
                description=s.get("description", ""),
                action_items=s.get("action_items", []),
                targets=s.get("targets", []),
                effectiveness_score=float(s.get("effectiveness_score", 0.0))
            )
            for s in result.get("prevention_strategies", [])
        ]

        return HealthRiskResponse(
            immediate_risks=immediate_risks,
            long_term_risks=long_term_risks,
            prevention_strategies=prevention_strategies,
            overall_risk_score=result.get("overall_risk_score", 0.0)
        )
    except Exception as e:
        logger.error(f"健康风险评估失败: {e}")
        raise InquiryServiceException(f"健康风险评估失败: {e!s}", 500)

def main() -> None:
    """主函数"""
    # 加载配置
    config_path = os.getenv("CONFIG_PATH", "./config/config.yaml")
    try:
        with open(config_path, encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return

    # 启动服务器
    server_config = config.get("server", {})
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 8000)  # REST API使用不同端口

    uvicorn.run(
        "api.enhanced_api_gateway:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
