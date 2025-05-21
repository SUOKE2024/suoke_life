import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.entities import (
    Constitution, ConstitutionListResponse, Symptom, SymptomListResponse,
    Syndrome, SyndromeListResponse, Biomarker, BiomarkerListResponse,
    WesternDisease, WesternDiseaseListResponse, PreventionEvidence,
    PreventionEvidenceListResponse, IntegratedTreatment, IntegratedTreatmentListResponse,
    LifestyleIntervention, LifestyleInterventionListResponse
)
from app.services.knowledge_service import KnowledgeService


class TestKnowledgeService:
    """知识服务测试类"""
    
    @pytest.fixture
    def repository_mock(self):
        """创建仓库Mock"""
        mock = AsyncMock()
        
        # 设置一些基本的返回值
        mock.get_node_count.return_value = 1000
        mock.get_relationship_count.return_value = 2500
        
        return mock
    
    @pytest.fixture
    def service(self, repository_mock):
        """创建服务实例"""
        return KnowledgeService(repository_mock)
    
    @pytest.mark.asyncio
    async def test_get_node_count(self, service, repository_mock):
        """测试获取节点数量"""
        # 设置返回值
        repository_mock.get_node_count.return_value = 1234
        
        # 调用服务方法
        result = await service.get_node_count()
        
        # 验证结果
        assert result == 1234
        repository_mock.get_node_count.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_relationship_count(self, service, repository_mock):
        """测试获取关系数量"""
        # 设置返回值
        repository_mock.get_relationship_count.return_value = 5678
        
        # 调用服务方法
        result = await service.get_relationship_count()
        
        # 验证结果
        assert result == 5678
        repository_mock.get_relationship_count.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_constitution_by_id(self, service, repository_mock):
        """测试根据ID获取体质"""
        constitution_id = "constitution-1"
        mock_constitution = Constitution(
            id=constitution_id,
            name="平和质",
            description="平和体质是指阴阳气血调和、脏腑功能平衡的正常体质状态。",
            characteristics=["面色润泽", "精力充沛"],
            symptoms=[],
            preventions=["起居有常", "饮食有节"],
            food_recommendations=["米饭", "蔬菜"],
            food_avoidances=[],
            prevalence=0.3,
            biomarker_correlations=[],
            western_medicine_correlations=[]
        )
        
        # 设置Mock返回值
        repository_mock.get_constitution_by_id.return_value = mock_constitution
        
        # 调用服务方法
        result = await service.get_constitution_by_id(constitution_id)
        
        # 验证结果
        assert result == mock_constitution
        repository_mock.get_constitution_by_id.assert_called_once_with(constitution_id)
    
    @pytest.mark.asyncio
    async def test_get_constitution_by_id_not_found(self, service, repository_mock):
        """测试获取不存在的体质"""
        constitution_id = "non-existent"
        
        # 设置Mock抛出异常
        repository_mock.get_constitution_by_id.side_effect = Exception("Not found")
        
        # 调用服务方法
        result = await service.get_constitution_by_id(constitution_id)
        
        # 验证结果
        assert result is None
        repository_mock.get_constitution_by_id.assert_called_once_with(constitution_id)
    
    @pytest.mark.asyncio
    async def test_get_constitutions(self, service, repository_mock):
        """测试获取所有体质"""
        limit = 10
        offset = 0
        mock_response = ConstitutionListResponse(
            data=[
                Constitution(
                    id="constitution-1",
                    name="平和质",
                    description="平和体质描述",
                    characteristics=[],
                    symptoms=[],
                    preventions=[],
                    food_recommendations=[],
                    food_avoidances=[],
                    prevalence=0.3,
                    biomarker_correlations=[],
                    western_medicine_correlations=[]
                )
            ],
            total=1,
            limit=limit,
            offset=offset
        )
        
        # 设置Mock返回值
        repository_mock.get_constitutions.return_value = mock_response
        
        # 调用服务方法
        result = await service.get_constitutions(limit, offset)
        
        # 验证结果
        assert result == mock_response
        repository_mock.get_constitutions.assert_called_once_with(limit, offset)
    
    @pytest.mark.asyncio
    async def test_search_knowledge(self, service, repository_mock):
        """测试搜索知识库"""
        query = "高血压"
        entity_type = "WesternDisease"
        limit = 10
        offset = 0
        
        mock_response = MagicMock()
        
        # 设置Mock返回值
        repository_mock.search_knowledge.return_value = mock_response
        
        # 调用服务方法
        result = await service.search_knowledge(query, entity_type, limit, offset)
        
        # 验证结果
        assert result == mock_response
        repository_mock.search_knowledge.assert_called_once_with(
            query, entity_type, limit, offset
        )
    
    @pytest.mark.asyncio
    async def test_get_recommendations_by_constitution(self, service, repository_mock):
        """测试获取体质相关推荐"""
        # 设置Mock返回值
        mock_response = MagicMock()
        repository_mock.get_recommendations_by_constitution.return_value = mock_response
        
        # 调用服务方法
        types = ["food", "exercise"]
        result = await service.get_recommendations_by_constitution("1", types)
        
        # 验证结果
        assert result == mock_response
        repository_mock.get_recommendations_by_constitution.assert_called_once_with("1", types)
    
    @pytest.mark.asyncio
    async def test_get_biomarkers_by_constitution(self, service, repository_mock):
        """测试获取与特定体质相关的生物标志物"""
        constitution_id = "constitution-1"
        limit = 10
        offset = 0
        
        mock_response = BiomarkerListResponse(
            data=[
                Biomarker(
                    id="biomarker-1",
                    name="C反应蛋白",
                    category="炎症因子",
                    description="炎症的标志物",
                    normal_range="<5 mg/L",
                    significance="炎症水平指标",
                    related_diseases=[],
                    related_syndromes=[],
                    related_constitutions=["气虚质"],
                    monitoring_frequency="每季度一次",
                    intervention_thresholds={}
                )
            ],
            total=1,
            limit=limit,
            offset=offset
        )
        
        # 设置Mock返回值
        repository_mock.get_biomarkers_by_constitution.return_value = mock_response
        
        # 调用服务方法
        result = await service.get_biomarkers_by_constitution(
            constitution_id, limit, offset
        )
        
        # 验证结果
        assert result == mock_response
        repository_mock.get_biomarkers_by_constitution.assert_called_once_with(
            constitution_id, limit, offset
        )
    
    @pytest.mark.asyncio
    async def test_get_western_diseases_by_syndrome(self, service, repository_mock):
        """测试获取与特定证型相关的西医疾病"""
        syndrome_id = "syndrome-1"
        limit = 10
        offset = 0
        
        mock_response = WesternDiseaseListResponse(
            data=[
                WesternDisease(
                    id="disease-1",
                    name="高血压",
                    icd_code="I10",
                    description="血压持续升高的疾病",
                    etiology="多因素病因",
                    pathophysiology="血管收缩与心输出量增加",
                    risk_factors=["肥胖", "高盐饮食"],
                    screening_methods=["血压测量"],
                    prevention_strategies=["减少盐摄入", "规律运动"],
                    tcm_correlations=["肝阳上亢证"],
                    early_signs=["头晕", "头痛"]
                )
            ],
            total=1,
            limit=limit,
            offset=offset
        )
        
        # 设置Mock返回值
        repository_mock.get_western_diseases_by_syndrome.return_value = mock_response
        
        # 调用服务方法
        result = await service.get_western_diseases_by_syndrome(
            syndrome_id, limit, offset
        )
        
        # 验证结果
        assert result == mock_response
        repository_mock.get_western_diseases_by_syndrome.assert_called_once_with(
            syndrome_id, limit, offset
        )
    
    @pytest.mark.asyncio
    async def test_get_lifestyle_interventions_by_constitution(self, service, repository_mock):
        """测试获取适合特定体质的生活方式干预"""
        constitution_id = "constitution-1"
        limit = 10
        offset = 0
        category = "饮食"
        
        mock_response = LifestyleInterventionListResponse(
            data=[
                LifestyleIntervention(
                    id="intervention-1",
                    name="温和饮食调理",
                    category="饮食",
                    description="适合平和体质的饮食调理",
                    protocol="三餐规律，清淡饮食",
                    scientific_basis="营养均衡理论",
                    tcm_principles="脾胃为后天之本",
                    suitable_constitutions=["平和质"],
                    contraindicated_constitutions=[],
                    health_metrics=["体重指数", "血糖水平"],
                    success_factors=["坚持性", "家庭支持"]
                )
            ],
            total=1,
            limit=limit,
            offset=offset
        )
        
        # 设置Mock返回值
        repository_mock.get_lifestyle_interventions_by_constitution.return_value = mock_response
        
        # 调用服务方法
        result = await service.get_lifestyle_interventions_by_constitution(
            constitution_id, limit, offset, category
        )
        
        # 验证结果
        assert result == mock_response
        repository_mock.get_lifestyle_interventions_by_constitution.assert_called_once_with(
            constitution_id, limit, offset, category
        )
    
    @pytest.mark.asyncio
    async def test_get_prevention_evidence(self, service, repository_mock):
        """测试获取预防医学证据"""
        limit = 10
        offset = 0
        category = "饮食"
        evidence_level = "A"
        
        mock_response = PreventionEvidenceListResponse(
            data=[
                PreventionEvidence(
                    id="evidence-1",
                    title="地中海饮食与心血管健康",
                    category="饮食",
                    description="地中海饮食降低心血管疾病风险",
                    evidence_level="A",
                    source_type="临床研究",
                    source_details="多中心随机对照试验",
                    effectiveness=0.85,
                    applicable_populations=["一般人群", "心血管高风险人群"],
                    contraindications=[],
                    implementation_guide="每日食用橄榄油、坚果、蔬菜水果"
                )
            ],
            total=1,
            limit=limit,
            offset=offset
        )
        
        # 设置Mock返回值
        repository_mock.get_prevention_evidence.return_value = mock_response
        
        # 调用服务方法
        result = await service.get_prevention_evidence(
            limit, offset, category, evidence_level
        )
        
        # 验证结果
        assert result == mock_response
        repository_mock.get_prevention_evidence.assert_called_once_with(
            limit, offset, category, evidence_level
        )
    
    @pytest.mark.asyncio
    async def test_get_integrated_treatments(self, service, repository_mock):
        """测试获取中西医结合治疗方案"""
        limit = 10
        offset = 0
        target_condition = "高血压"
        
        mock_response = IntegratedTreatmentListResponse(
            data=[
                IntegratedTreatment(
                    id="treatment-1",
                    name="高血压中西医结合治疗方案",
                    target_condition="高血压",
                    description="结合中西医方法控制血压",
                    tcm_components=[{"type": "中药", "name": "天麻钩藤饮"}],
                    western_components=[{"type": "西药", "name": "ACEI类降压药"}],
                    integration_rationale="中药调节体质，西药稳定控制血压",
                    expected_outcomes=["血压控制稳定", "副作用减少"],
                    evidence_base="多项临床研究",
                    personalization_factors=["年龄", "体质类型"],
                    monitoring_metrics=["血压", "症状改善"]
                )
            ],
            total=1,
            limit=limit,
            offset=offset
        )
        
        # 设置Mock返回值
        repository_mock.get_integrated_treatments.return_value = mock_response
        
        # 调用服务方法
        result = await service.get_integrated_treatments(
            limit, offset, target_condition
        )
        
        # 验证结果
        assert result == mock_response
        repository_mock.get_integrated_treatments.assert_called_once_with(
            limit, offset, target_condition
        )
    
    @pytest.mark.asyncio
    async def test_exception_handling(self, service, repository_mock):
        """测试异常处理"""
        # 设置Mock抛出异常
        repository_mock.get_constitution_by_id.side_effect = Exception("数据库错误")
        
        # 调用服务方法
        result = await service.get_constitution_by_id("1")
        
        # 验证结果：应当返回None而不是抛出异常
        assert result is None 