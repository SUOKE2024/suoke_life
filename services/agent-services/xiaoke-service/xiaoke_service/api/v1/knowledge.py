"""
知识库 API 端点
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from xiaoke_service.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class KnowledgeQuery(BaseModel):
    """知识查询请求模型"""

    query: str
    category: str | None = None
    limit: int = 10


class KnowledgeItem(BaseModel):
    """知识条目模型"""

    id: str
    title: str
    content: str
    category: str
    confidence: float
    source: str


class KnowledgeResponse(BaseModel):
    """知识查询响应模型"""

    query: str
    results: list[KnowledgeItem]
    total_count: int


@router.post("/search", response_model=KnowledgeResponse)
async def search_knowledge(request: KnowledgeQuery) -> KnowledgeResponse:
    """搜索知识库"""
    try:
        logger.info(f"知识库搜索请求: query={request.query}, category={request.category}")

        # 这里应该调用实际的知识库搜索服务
        sample_item = KnowledgeItem(
            id="tcm-001",
            title="中医基础理论",
            content="中医学是以阴阳五行作为理论基础, 将人体看成是气、形、神的统一体...",
            category="中医理论",
            confidence=0.92,
            source="中医药大学教材",
        )

        return KnowledgeResponse(
            query=request.query,
            results=[sample_item],
            total_count=1
        )
    except Exception as e:
        logger.error(f"知识库搜索失败: {e!s}")
        raise HTTPException(status_code=500, detail="知识库搜索失败") from e


@router.get("/categories")
async def get_knowledge_categories() -> dict:
    """获取知识库分类"""
    try:
        logger.info("获取知识库分类")

        return {
            "categories": [
                {"id": "tcm-theory", "name": "中医理论", "count": 150},
                {"id": "herbs", "name": "中药材", "count": 500},
                {"id": "acupuncture", "name": "针灸", "count": 200},
                {"id": "health-tips", "name": "养生保健", "count": 300},
            ],
            "status": "success"
        }
    except Exception as e:
        logger.error(f"获取知识库分类失败: {e!s}")
        raise HTTPException(status_code=500, detail="获取知识库分类失败") from e


@router.get("/items/{item_id}")
async def get_knowledge_item(item_id: str) -> KnowledgeItem:
    """获取特定知识条目"""
    try:
        logger.info(f"获取知识条目: item_id={item_id}")

        # 这里应该从数据库查询实际的知识条目
        return KnowledgeItem(
            id=item_id,
            title="示例知识条目",
            content="这是一个示例知识条目的内容...",
            category="示例分类",
            confidence=0.95,
            source="示例来源",
        )
    except Exception as e:
        logger.error(f"获取知识条目失败: {e!s}")
        raise HTTPException(status_code=500, detail="获取知识条目失败") from e
