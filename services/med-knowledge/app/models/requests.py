"""
请求模型
定义API请求参数的验证和序列化模型
"""

from pydantic import BaseModel, Field, validator


class PaginationRequest(BaseModel):
    """分页请求基础模型"""

    limit: int = Field(default=20, ge=1, le=100, description="每页数量,范围1-100")
    offset: int = Field(default=0, ge=0, description="偏移量,从0开始")

    @validator("limit")
    def validate_limit(cls, v):
        if v > 100:
            raise ValueError("每页数量不能超过100")
        return v


class SearchRequest(PaginationRequest):
    """搜索请求模型"""

    query: str = Field(..., min_length=1, max_length=200, description="搜索关键词")
    entity_type: str | None = Field(None, description="实体类型过滤")

    @validator("query")
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("搜索关键词不能为空")
        return v.strip()

    @validator("entity_type")
    def validate_entity_type(cls, v):
        if v is not None:
            allowed_types = [
                "constitution",
                "symptom",
                "acupoint",
                "herb",
                "syndrome",
                "biomarker",
                "western_disease",
                "prevention_evidence",
                "integrated_treatment",
                "lifestyle_intervention",
            ]
            if v not in allowed_types:
                raise ValueError(f'实体类型必须是: {", ".join(allowed_types)}')
        return v


class ConstitutionListRequest(PaginationRequest):
    """体质列表请求模型"""

    pass


class SymptomListRequest(PaginationRequest):
    """症状列表请求模型"""

    pass


class AcupointListRequest(PaginationRequest):
    """穴位列表请求模型"""

    meridian: str | None = Field(None, max_length=50, description="经络过滤")

    @validator("meridian")
    def validate_meridian(cls, v):
        if v is not None and not v.strip():
            return None
        return v


class HerbListRequest(PaginationRequest):
    """中药列表请求模型"""

    category: str | None = Field(None, max_length=50, description="分类过滤")

    @validator("category")
    def validate_category(cls, v):
        if v is not None and not v.strip():
            return None
        return v


class SyndromeListRequest(PaginationRequest):
    """证型列表请求模型"""

    pass


class RecommendationRequest(BaseModel):
    """推荐请求模型"""

    constitution_id: str = Field(..., min_length=1, description="体质ID")
    types: list[str] | None = Field(None, description="推荐类型列表")

    @validator("constitution_id")
    def validate_constitution_id(cls, v):
        if not v.strip():
            raise ValueError("体质ID不能为空")
        return v.strip()

    @validator("types")
    def validate_types(cls, v):
        if v is not None:
            allowed_types = ["diet", "exercise", "lifestyle", "acupoint", "herb"]
            for t in v:
                if t not in allowed_types:
                    raise ValueError(f'推荐类型必须是: {", ".join(allowed_types)}')
        return v


class BiomarkerListRequest(PaginationRequest):
    """生物标志物列表请求模型"""

    category: str | None = Field(None, max_length=50, description="分类过滤")

    @validator("category")
    def validate_category(cls, v):
        if v is not None and not v.strip():
            return None
        return v


class BiomarkerByConstitutionRequest(PaginationRequest):
    """按体质查询生物标志物请求模型"""

    constitution_id: str = Field(..., min_length=1, description="体质ID")

    @validator("constitution_id")
    def validate_constitution_id(cls, v):
        if not v.strip():
            raise ValueError("体质ID不能为空")
        return v.strip()


class WesternDiseaseListRequest(PaginationRequest):
    """西医疾病列表请求模型"""

    pass


class WesternDiseaseBysyndromeRequest(PaginationRequest):
    """按证型查询西医疾病请求模型"""

    syndrome_id: str = Field(..., min_length=1, description="证型ID")

    @validator("syndrome_id")
    def validate_syndrome_id(cls, v):
        if not v.strip():
            raise ValueError("证型ID不能为空")
        return v.strip()


class PreventionEvidenceListRequest(PaginationRequest):
    """预防医学证据列表请求模型"""

    category: str | None = Field(None, max_length=50, description="分类过滤")
    evidence_level: str | None = Field(None, max_length=20, description="证据等级过滤")

    @validator("category")
    def validate_category(cls, v):
        if v is not None and not v.strip():
            return None
        return v

    @validator("evidence_level")
    def validate_evidence_level(cls, v):
        if v is not None:
            allowed_levels = ["A", "B", "C", "D"]
            if v not in allowed_levels:
                raise ValueError(f'证据等级必须是: {", ".join(allowed_levels)}')
        return v


class IntegratedTreatmentListRequest(PaginationRequest):
    """中西医结合治疗列表请求模型"""

    target_condition: str | None = Field(None, max_length=100, description="目标疾病过滤")

    @validator("target_condition")
    def validate_target_condition(cls, v):
        if v is not None and not v.strip():
            return None
        return v


class LifestyleInterventionListRequest(PaginationRequest):
    """生活方式干预列表请求模型"""

    category: str | None = Field(None, max_length=50, description="分类过滤")

    @validator("category")
    def validate_category(cls, v):
        if v is not None and not v.strip():
            return None
        return v


class LifestyleInterventionByConstitutionRequest(PaginationRequest):
    """按体质查询生活方式干预请求模型"""

    constitution_id: str = Field(..., min_length=1, description="体质ID")
    category: str | None = Field(None, max_length=50, description="分类过滤")

    @validator("constitution_id")
    def validate_constitution_id(cls, v):
        if not v.strip():
            raise ValueError("体质ID不能为空")
        return v.strip()

    @validator("category")
    def validate_category(cls, v):
        if v is not None and not v.strip():
            return None
        return v


class GraphVisualizationRequest(BaseModel):
    """知识图谱可视化请求模型"""

    entity_type: str | None = Field(None, description="实体类型过滤")
    entity_id: str | None = Field(None, description="中心实体ID")
    depth: int = Field(default=2, ge=1, le=5, description="遍历深度,范围1-5")
    max_nodes: int = Field(default=100, ge=10, le=500, description="最大节点数,范围10-500")

    @validator("entity_type")
    def validate_entity_type(cls, v):
        if v is not None:
            allowed_types = [
                "constitution",
                "symptom",
                "acupoint",
                "herb",
                "syndrome",
                "biomarker",
                "western_disease",
            ]
            if v not in allowed_types:
                raise ValueError(f'实体类型必须是: {", ".join(allowed_types)}')
        return v

    @validator("entity_id")
    def validate_entity_id(cls, v):
        if v is not None and not v.strip():
            return None
        return v


class PathAnalysisRequest(BaseModel):
    """路径分析请求模型"""

    from_id: str = Field(..., min_length=1, description="起始节点ID")
    to_id: str = Field(..., min_length=1, description="目标节点ID")
    max_depth: int = Field(default=5, ge=1, le=10, description="最大搜索深度")
    max_paths: int = Field(default=10, ge=1, le=50, description="最大路径数量")

    @validator("from_id", "to_id")
    def validate_node_ids(cls, v):
        if not v.strip():
            raise ValueError("节点ID不能为空")
        return v.strip()

    @validator("to_id")
    def validate_different_nodes(cls, v, values):
        if "from_id" in values and v == values["from_id"]:
            raise ValueError("起始节点和目标节点不能相同")
        return v


class RelationshipAnalysisRequest(BaseModel):
    """关系分析请求模型"""

    node_id: str = Field(..., min_length=1, description="节点ID")
    relationship_types: list[str] | None = Field(None, description="关系类型过滤")
    direction: str = Field(default="both", description="关系方向: in, out, both")

    @validator("node_id")
    def validate_node_id(cls, v):
        if not v.strip():
            raise ValueError("节点ID不能为空")
        return v.strip()

    @validator("direction")
    def validate_direction(cls, v):
        allowed_directions = ["in", "out", "both"]
        if v not in allowed_directions:
            raise ValueError(f'关系方向必须是: {", ".join(allowed_directions)}')
        return v

    @validator("relationship_types")
    def validate_relationship_types(cls, v):
        if v is not None:
            allowed_types = [
                "BELONGS_TO",
                "TREATS",
                "CAUSES",
                "PREVENTS",
                "RELATED_TO",
                "INDICATES",
                "CONTRAINDICATED",
                "SYNERGISTIC",
                "ANTAGONISTIC",
            ]
            for t in v:
                if t not in allowed_types:
                    raise ValueError(f'关系类型必须是: {", ".join(allowed_types)}')
        return v


class DataImportRequest(BaseModel):
    """数据导入请求模型"""

    source_type: str = Field(..., description="数据源类型")
    source_path: str = Field(..., min_length=1, description="数据源路径")
    overwrite: bool = Field(default=False, description="是否覆盖现有数据")
    validate_only: bool = Field(default=False, description="仅验证不导入")

    @validator("source_type")
    def validate_source_type(cls, v):
        allowed_types = ["json", "csv", "xml", "excel"]
        if v not in allowed_types:
            raise ValueError(f'数据源类型必须是: {", ".join(allowed_types)}')
        return v

    @validator("source_path")
    def validate_source_path(cls, v):
        if not v.strip():
            raise ValueError("数据源路径不能为空")
        return v.strip()
