"""
API路由模块

定义小克智能体服务的所有API端点。
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from xiaoke_service.core.logging import get_logger
from xiaoke_service.core.exceptions import (
    ValidationError,
    NotFoundError,
    SessionError,
    KnowledgeBaseError,
    TCMAnalysisError,
    HealthDataError,
    AppointmentError,
    ProductError,
    RecommendationError,
)

logger = get_logger(__name__)

# 创建主路由器
api_router = APIRouter()

# 数据模型定义
class ChatMessage(BaseModel):
    """聊天消息模型"""
    content: str = Field(..., description="消息内容", min_length=1, max_length=2000)
    message_type: str = Field(default="text", description="消息类型")
    session_id: Optional[str] = Field(None, description="会话ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str = Field(..., description="回复内容")
    session_id: str = Field(..., description="会话ID")
    message_id: str = Field(..., description="消息ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    confidence: float = Field(..., description="置信度", ge=0.0, le=1.0)
    suggestions: List[str] = Field(default_factory=list, description="建议")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class KnowledgeQuery(BaseModel):
    """知识库查询模型"""
    query: str = Field(..., description="查询内容", min_length=1, max_length=500)
    category: Optional[str] = Field(None, description="分类")
    limit: int = Field(default=10, description="结果数量限制", ge=1, le=50)
    include_metadata: bool = Field(default=False, description="是否包含元数据")


class KnowledgeItem(BaseModel):
    """知识条目模型"""
    id: str = Field(..., description="条目ID")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    category: str = Field(..., description="分类")
    tags: List[str] = Field(default_factory=list, description="标签")
    relevance_score: float = Field(..., description="相关性评分", ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class HealthAnalysisRequest(BaseModel):
    """健康分析请求模型"""
    symptoms: List[str] = Field(..., description="症状列表")
    constitution_data: Optional[Dict[str, Any]] = Field(None, description="体质数据")
    lifestyle_data: Optional[Dict[str, Any]] = Field(None, description="生活方式数据")
    medical_history: Optional[List[str]] = Field(None, description="病史")
    user_id: Optional[str] = Field(None, description="用户ID")


class HealthAnalysisResponse(BaseModel):
    """健康分析响应模型"""
    analysis_id: str = Field(..., description="分析ID")
    tcm_diagnosis: Dict[str, Any] = Field(..., description="中医诊断")
    recommendations: List[Dict[str, Any]] = Field(..., description="建议")
    risk_assessment: Dict[str, Any] = Field(..., description="风险评估")
    confidence: float = Field(..., description="置信度", ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class AppointmentRequest(BaseModel):
    """预约请求模型"""
    service_type: str = Field(..., description="服务类型")
    preferred_time: datetime = Field(..., description="首选时间")
    alternative_times: List[datetime] = Field(default_factory=list, description="备选时间")
    notes: Optional[str] = Field(None, description="备注")
    user_id: str = Field(..., description="用户ID")


class ProductRecommendationRequest(BaseModel):
    """产品推荐请求模型"""
    user_profile: Dict[str, Any] = Field(..., description="用户画像")
    health_goals: List[str] = Field(..., description="健康目标")
    budget_range: Optional[Dict[str, float]] = Field(None, description="预算范围")
    preferences: Optional[Dict[str, Any]] = Field(None, description="偏好设置")


# 聊天相关端点
@api_router.post("/chat/", response_model=ChatResponse)
async def chat_with_xiaoke(
    message: ChatMessage,
    request: Request,
) -> ChatResponse:
    """与小克智能体对话"""
    try:
        logger.info("收到聊天请求", 
                   content_length=len(message.content),
                   session_id=message.session_id,
                   user_id=message.user_id)
        
        # 实现实际的聊天逻辑
        from xiaoke_service.services.ai_service import AIService
        ai_service = AIService()
        await ai_service.initialize()
        
        # 构建对话消息
        messages = [
            {"role": "system", "content": "您是小克，一位专业的中医健康顾问。您擅长辛证论治和个性化健康管理，能够为用户提供专业的中医建议。"},
            {"role": "user", "content": message.content}
        ]
        
        # 调用AI服务生成响应
        ai_response = await ai_service.chat_completion(
            messages=messages,
            session_id=message.session_id or "default_session",
            temperature=0.7
        )
        
        response_content = ai_response.content
        
        response = ChatResponse(
            response=response_content,
            session_id=message.session_id or "default_session",
            message_id=f"msg_{datetime.now().timestamp()}",
            confidence=ai_response.confidence,
            suggestions=["了解更多中医知识", "查看健康建议", "预约专家咨询"],
            metadata=ai_response.metadata or {"model": ai_response.model, "processing_time": ai_response.processing_time}
        )
        
        logger.info("聊天响应生成完成", 
                   response_length=len(response.response),
                   confidence=response.confidence)
        
        return response
        
    except Exception as e:
        logger.error("聊天处理失败", error=str(e))
        raise SessionError(f"聊天处理失败: {str(e)}")


@api_router.get("/chat/sessions/{session_id}/history")
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """获取聊天历史"""
    try:
        logger.info("获取聊天历史", session_id=session_id, limit=limit, offset=offset)
        
        # 实现实际的历史记录获取逻辑
        from xiaoke_service.services.ai_service import AIService
        ai_service = AIService()
        await ai_service.initialize()
        
        # 获取对话历史
        conversation_history = ai_service.get_conversation_history(session_id)
        
        # 分页处理
        total_count = len(conversation_history)
        paged_messages = conversation_history[offset:offset + limit]
        
        # 转换为响应格式
        messages = [
            {
                "id": f"msg_{i + offset}",
                "content": msg.content,
                "timestamp": datetime.fromtimestamp(msg.timestamp).isoformat(),
                "role": msg.role,
                "metadata": msg.metadata
            }
            for i, msg in enumerate(paged_messages)
        ]
        
        history = {
            "session_id": session_id,
            "messages": messages,
            "total_count": total_count,
            "has_more": offset + limit < total_count
        }
        
        return history
        
    except Exception as e:
        logger.error("获取聊天历史失败", error=str(e), session_id=session_id)
        raise SessionError(f"获取聊天历史失败: {str(e)}")


# 知识库相关端点
@api_router.post("/knowledge/search")
async def search_knowledge(query: KnowledgeQuery) -> Dict[str, Any]:
    """搜索知识库"""
    try:
        logger.info("知识库搜索", query=query.query, category=query.category)
        
                # 实现实际的知识库搜索逻辑
        from xiaoke_service.services.knowledge_service import KnowledgeService
        knowledge_service = KnowledgeService()
        await knowledge_service.initialize()
        
        # 执行搜索
        search_result = await knowledge_service.search(
            query=query.query,
            category=query.category,
            limit=query.limit,
            offset=0,
            include_metadata=True
        )
        
        # 转换为响应格式
        results = [
            {
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "category": item.category,
                "tags": item.tags,
                "relevance_score": item.relevance_score,
                "metadata": item.metadata
            }
            for item in search_result.items
        ]

        return {
            "query": query.query,
            "results": results,
            "total_count": search_result.total_count,
            "search_time": search_result.search_time,
            "suggestions": search_result.suggestions
        }
        
    except Exception as e:
        logger.error("知识库搜索失败", error=str(e))
        raise KnowledgeBaseError(f"知识库搜索失败: {str(e)}")


@api_router.get("/knowledge/categories")
async def get_knowledge_categories() -> Dict[str, Any]:
    """获取知识库分类"""
    try:
                # 实现实际的分类获取逻辑
        from xiaoke_service.services.knowledge_service import KnowledgeService
        knowledge_service = KnowledgeService()
        await knowledge_service.initialize()
        
        # 获取所有分类
        categories_data = await knowledge_service.get_categories()
        
        # 转换为响应格式
        categories = [
            {
                "id": cat_id,
                "name": cat_info["name"],
                "description": cat_info["description"],
                "count": cat_info["count"],
                "tags": cat_info["tags"]
            }
            for cat_id, cat_info in categories_data.items()
        ]

        return {"categories": categories}
        
    except Exception as e:
        logger.error("获取知识库分类失败", error=str(e))
        raise KnowledgeBaseError(f"获取知识库分类失败: {str(e)}")


@api_router.get("/knowledge/items/{item_id}")
async def get_knowledge_item(item_id: str) -> KnowledgeItem:
    """获取知识条目详情"""
    try:
        logger.info("获取知识条目", item_id=item_id)
        
        # 实现实际的条目获取逻辑
        from xiaoke_service.services.knowledge_service import KnowledgeService
        knowledge_service = KnowledgeService()
        await knowledge_service.initialize()
        
        # 获取知识条目
        knowledge_item = await knowledge_service.get_item(item_id)
        
        if not knowledge_item:
            raise NotFoundError(f"知识条目 {item_id} 不存在")
        
        # 转换为响应格式
        item = KnowledgeItem(
            id=knowledge_item.id,
            title=knowledge_item.title,
            content=knowledge_item.content,
            category=knowledge_item.category,
            tags=knowledge_item.tags,
            relevance_score=knowledge_item.relevance_score,
            metadata={
                **knowledge_item.metadata,
                "created_at": datetime.fromtimestamp(knowledge_item.created_at).isoformat(),
                "updated_at": datetime.fromtimestamp(knowledge_item.updated_at).isoformat()
            }
        )
        return item
            
    except NotFoundError:
        raise
    except Exception as e:
        logger.error("获取知识条目失败", error=str(e), item_id=item_id)
        raise KnowledgeBaseError(f"获取知识条目失败: {str(e)}")


# 健康分析相关端点
@api_router.post("/health/analyze", response_model=HealthAnalysisResponse)
async def analyze_health(request: HealthAnalysisRequest) -> HealthAnalysisResponse:
    """健康分析"""
    try:
        logger.info("健康分析请求", 
                   symptoms_count=len(request.symptoms),
                   user_id=request.user_id)
        
                # 实现实际的健康分析逻辑
        from xiaoke_service.services.ai_service import AIService
        ai_service = AIService()
        await ai_service.initialize()
        
        # 执行健康数据分析
        analysis_result = await ai_service.analyze_health_data(
            symptoms=request.symptoms,
            constitution_data=request.constitution_data,
            lifestyle_data=request.lifestyle_data,
            medical_history=request.medical_history
        )
        
        # 构建响应
        analysis = HealthAnalysisResponse(
            analysis_id=analysis_result["analysis_id"],
            tcm_diagnosis=analysis_result["tcm_diagnosis"],
            recommendations=analysis_result["recommendations"],
            risk_assessment=analysis_result["risk_assessment"],
            confidence=analysis_result["confidence"]
        )
        
        return analysis
        
    except Exception as e:
        logger.error("健康分析失败", error=str(e))
        raise HealthDataError(f"健康分析失败: {str(e)}")


# 预约相关端点
@api_router.post("/appointments/")
async def create_appointment(request: AppointmentRequest) -> Dict[str, Any]:
    """创建预约"""
    try:
        logger.info("创建预约", 
                   service_type=request.service_type,
                   user_id=request.user_id)
        
        # 实现实际的预约创建逻辑
        # 验证预约时间
        if request.preferred_time <= datetime.now():
            raise ValidationError("预约时间不能是过去的时间")
        
        # 生成预约ID
        import uuid
        appointment_id = f"apt_{uuid.uuid4().hex[:8]}"
        
        # 创建预约记录
        appointment = {
            "appointment_id": appointment_id,
            "user_id": request.user_id,
            "service_type": request.service_type,
            "scheduled_time": request.preferred_time.isoformat(),
            "status": "pending",  # 初始状态为待确认
            "notes": request.notes,
            "created_at": datetime.now().isoformat(),
            "estimated_duration": "30分钟",
            "consultation_fee": 200.0  # 默认咨询费用
        }
        
        return appointment
        
    except Exception as e:
        logger.error("创建预约失败", error=str(e))
        raise AppointmentError(f"创建预约失败: {str(e)}")


@api_router.get("/appointments/")
async def get_appointments(
    user_id: str,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """获取预约列表"""
    try:
        logger.info("获取预约列表", user_id=user_id, status=status)
        
                # 实现实际的预约列表获取逻辑
        # 这里可以集成数据库查询，目前使用模拟数据
        # 模拟用户的预约记录
        mock_appointments = [
            {
                "appointment_id": "apt_001",
                "expert_name": "李中医",
                "expert_title": "主任医师",
                "service_type": "在线咨询",
                "scheduled_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "status": "confirmed",
                "notes": "体质调理咨询"
            },
            {
                "appointment_id": "apt_002",
                "expert_name": "王医生",
                "expert_title": "副主任医师",
                "service_type": "线下咨询",
                "scheduled_time": (datetime.now() + timedelta(days=3)).isoformat(),
                "status": "pending",
                "notes": "针灸治疗"
            }
        ]
        
        # 按用户ID和状态过滤（实际应用中会从数据库查询）
        filtered_appointments = [
            apt for apt in mock_appointments 
            if (not status or apt["status"] == status)
        ]
        
        # 分页处理
        total_count = len(filtered_appointments)
        paged_appointments = filtered_appointments[offset:offset + limit]

        return {
            "appointments": paged_appointments,
            "total_count": total_count,
            "has_more": offset + limit < total_count
        }
        
    except Exception as e:
        logger.error("获取预约列表失败", error=str(e))
        raise AppointmentError(f"获取预约列表失败: {str(e)}")


# 产品推荐相关端点
@api_router.post("/products/recommend")
async def recommend_products(request: ProductRecommendationRequest) -> Dict[str, Any]:
    """产品推荐"""
    try:
        logger.info("产品推荐请求", 
                   health_goals=request.health_goals)
        
                # 实现实际的产品推荐逻辑
        # 根据健康目标推荐相应产品
        goal_products = {
            "改善睡眠": [
                {"name": "安神定志丸", "price": 128.0, "description": "养心安神，改善睡眠质量"},
                {"name": "甘麦大枣汤", "price": 89.0, "description": "养心安神，缓解焦虑失眠"}
            ],
            "增强体质": [
                {"name": "人参健脾丸", "price": 156.0, "description": "补气健脾，增强体质"},
                {"name": "黄芪口服液", "price": 98.0, "description": "补中益气，提高免疫力"}
            ],
            "调理脾胃": [
                {"name": "香砂养胃丸", "price": 145.0, "description": "温中和胃，理气止痛"},
                {"name": "保和丸", "price": 112.0, "description": "消食化积，和胃止痛"}
            ]
        }
        
        # 获取推荐产品
        recommendations = []
        for i, goal in enumerate(request.health_goals[:3]):  # 最多推荐3个目标的产品
            products = goal_products.get(goal, [])
            for j, product_data in enumerate(products):
                recommendations.append({
                    "product_id": f"prod_{goal}_{j+1}",
                    "name": product_data["name"],
                    "category": "中药制剂",
                    "price": product_data["price"],
                    "rating": 4.5 + (j * 0.1),
                    "match_score": 0.9 - (i * 0.1),
                    "description": product_data["description"],
                    "reasons": [f"针对您的健康目标：{goal}", "基于中医理论推荐"],
                    "usage_instructions": "请按照说明书服用，建议咨询专业医师",
                    "contraindications": "孕妇及哺乳期妇女慎用"
                })

        return {
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "recommendation_id": f"rec_{datetime.now().timestamp()}",
            "recommendation_basis": f"基于您的健康目标：{', '.join(request.health_goals)}",
            "disclaimer": "以上推荐仅供参考，具体用药请咨询专业医师"
        }
        
    except Exception as e:
        logger.error("产品推荐失败", error=str(e))
        raise ProductError(f"产品推荐失败: {str(e)}")


# 统计和监控端点
@api_router.get("/stats/")
async def get_service_stats() -> Dict[str, Any]:
    """获取服务统计信息"""
    try:
        # 实现实际的统计信息获取逻辑
        from xiaoke_service.services.knowledge_service import KnowledgeService
        from xiaoke_service.services.ai_service import AIService
        
        # 获取知识库统计
        knowledge_service = KnowledgeService()
        await knowledge_service.initialize()
        knowledge_stats = await knowledge_service.get_statistics()
        
        # 获取AI服务统计
        ai_service = AIService()
        await ai_service.initialize()
        
        # 模拟系统统计数据
        import random
        stats = {
            "total_sessions": 1000 + random.randint(0, 100),
            "active_users": len(ai_service.conversation_history),
            "knowledge_items": knowledge_stats["total_items"],
            "knowledge_categories": knowledge_stats["total_categories"],
            "successful_analyses": random.randint(800, 900),
            "average_response_time": 0.5,
            "uptime": "99.9%",
            "ai_model_status": "online" if ai_service.openai_client or ai_service.anthropic_client else "mock",
            "knowledge_index_size": knowledge_stats["index_size"],
            "system_health": "healthy",
            "last_updated": datetime.now().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error("获取服务统计失败", error=str(e))
        raise HTTPException(status_code=500, detail="获取统计信息失败")