"""
算诊服务综合测试

测试所有算诊功能的集成测试
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from calculation_service.main import app
from calculation_service.core.algorithms.comprehensive_calculator import ComprehensiveCalculator
from calculation_service.core.algorithms.ziwu_liuzhu.calculator import ZiwuLiuzhuCalculator
from calculation_service.core.algorithms.constitution.calculator import ConstitutionCalculator
from calculation_service.core.algorithms.bagua.calculator import BaguaCalculator
from calculation_service.core.algorithms.wuyun_liuqi.calculator import WuyunLiuqiCalculator
from calculation_service.utils.validators import validate_birth_info
from calculation_service.utils.formatters import format_analysis_result
from calculation_service.utils.cache import cache_manager

class TestCalculationService:
    """算诊服务综合测试类"""
    
    @pytest.fixture
    def client(self):
        """测试客户端"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_birth_info(self):
        """示例出生信息"""
        return {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 14,
            "gender": "男",
            "name": "张三"
        }
    
    @pytest.fixture
    def comprehensive_calculator(self):
        """综合算诊计算器"""
        return ComprehensiveCalculator()
    
    def test_service_health(self, client):
        """测试服务健康状态"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "calculation-service"
        assert data["status"] == "running"
        assert "子午流注分析" in data["features"]
        assert "八字体质分析" in data["features"]
        assert "八卦配属分析" in data["features"]
        assert "五运六气分析" in data["features"]
        assert "综合算诊" in data["features"]
    
    def test_ping(self, client):
        """测试ping接口"""
        response = client.get("/ping")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["message"] == "pong"
    
    def test_birth_info_validation(self, sample_birth_info):
        """测试出生信息验证"""
        # 正常情况
        assert validate_birth_info(sample_birth_info) == True
        
        # 缺少必需字段
        invalid_info = sample_birth_info.copy()
        del invalid_info["year"]
        
        with pytest.raises(Exception):
            validate_birth_info(invalid_info)
        
        # 无效年份
        invalid_info = sample_birth_info.copy()
        invalid_info["year"] = 1800
        
        with pytest.raises(Exception):
            validate_birth_info(invalid_info)
    
    def test_ziwu_liuzhu_analysis(self, sample_birth_info):
        """测试子午流注分析"""
        calculator = ZiwuLiuzhuCalculator()
        
        # 测试当前时辰分析
        current_time = datetime.now()
        result = calculator.analyze_current_time(current_time)
        
        assert "当前时辰" in result
        assert "当前经络" in result
        assert "经络特点" in result
        assert "调养建议" in result
        
        # 测试最佳治疗时间
        treatment_times = calculator.get_best_treatment_times("头痛")
        assert isinstance(treatment_times, list)
        assert len(treatment_times) > 0
    
    def test_constitution_analysis(self, sample_birth_info):
        """测试八字体质分析"""
        calculator = ConstitutionCalculator()
        
        result = calculator.analyze_constitution(sample_birth_info)
        
        assert "八字信息" in result
        assert "体质类型" in result
        assert "五行强弱" in result
        assert "调理建议" in result
        assert "养生要点" in result
        
        # 验证八字计算
        bazi = calculator.calculate_bazi(
            sample_birth_info["year"],
            sample_birth_info["month"], 
            sample_birth_info["day"],
            sample_birth_info["hour"]
        )
        
        assert "年柱" in bazi
        assert "月柱" in bazi
        assert "日柱" in bazi
        assert "时柱" in bazi
    
    def test_bagua_analysis(self, sample_birth_info):
        """测试八卦配属分析"""
        calculator = BaguaCalculator()
        
        result = calculator.analyze_bagua(sample_birth_info)
        
        assert "本命卦" in result
        assert "卦象特点" in result
        assert "健康分析" in result
        assert "调理建议" in result
        assert "方位指导" in result
        
        # 测试本命卦计算
        benming_gua = calculator.calculate_benming_gua(
            sample_birth_info["year"],
            sample_birth_info["gender"]
        )
        
        assert benming_gua in ["乾", "坤", "震", "巽", "坎", "离", "艮", "兑"]
    
    def test_wuyun_liuqi_analysis(self, sample_birth_info):
        """测试五运六气分析"""
        calculator = WuyunLiuqiCalculator()
        
        result = calculator.analyze_wuyun_liuqi(sample_birth_info["year"])
        
        assert "五运分析" in result
        assert "司天在泉" in result
        assert "疾病预测" in result
        assert "调养建议" in result
        assert "总体特点" in result
        
        # 测试运气推算
        yunqi = calculator.calculate_yunqi(sample_birth_info["year"])
        assert "主运" in yunqi
        assert "客运" in yunqi
        assert "司天" in yunqi
        assert "在泉" in yunqi
    
    def test_comprehensive_analysis(self, sample_birth_info, comprehensive_calculator):
        """测试综合算诊分析"""
        analysis_options = {
            "include_ziwu": True,
            "include_constitution": True,
            "include_bagua": True,
            "include_wuyun_liuqi": True
        }
        
        result = comprehensive_calculator.comprehensive_analysis(
            sample_birth_info,
            analysis_options
        )
        
        assert "个人信息" in result
        assert "分析时间" in result
        assert "子午流注分析" in result
        assert "体质分析" in result
        assert "八卦分析" in result
        assert "运气分析" in result
        assert "综合建议" in result
        assert "调养重点" in result
        assert "注意事项" in result
        
        # 测试健康风险评估
        risk_assessment = comprehensive_calculator.assess_health_risks(result)
        assert "风险等级" in risk_assessment
        assert "主要风险" in risk_assessment
        assert "预防建议" in risk_assessment
    
    def test_result_formatting(self, sample_birth_info, comprehensive_calculator):
        """测试结果格式化"""
        analysis_options = {
            "include_ziwu": True,
            "include_constitution": True,
            "include_bagua": False,
            "include_wuyun_liuqi": False
        }
        
        result = comprehensive_calculator.comprehensive_analysis(
            sample_birth_info,
            analysis_options
        )
        
        formatted_result = format_analysis_result(result)
        
        assert "分析概要" in formatted_result
        assert "详细分析" in formatted_result
        assert "综合建议" in formatted_result
        assert "调养重点" in formatted_result
        assert "注意事项" in formatted_result
        
        # 检查分析概要
        summary = formatted_result["分析概要"]
        assert "分析时间" in summary
        assert "个人信息" in summary
        assert "分析类型" in summary
        
        # 检查详细分析
        details = formatted_result["详细分析"]
        assert "子午流注" in details
        assert "体质分析" in details
    
    def test_cache_functionality(self):
        """测试缓存功能"""
        # 清理缓存
        cache_manager.clear()
        
        # 测试缓存设置和获取
        test_key = "test_key"
        test_data = {"test": "data"}
        
        cache_manager.set(test_key, test_data)
        cached_data = cache_manager.get(test_key)
        
        assert cached_data == test_data
        
        # 测试缓存统计
        stats = cache_manager.get_stats()
        assert stats["total_items"] >= 1
        assert stats["active_items"] >= 1
        
        # 测试缓存删除
        assert cache_manager.delete(test_key) == True
        assert cache_manager.get(test_key) is None
    
    def test_api_comprehensive_analysis(self, client, sample_birth_info):
        """测试API综合分析接口"""
        request_data = {
            "birth_info": sample_birth_info,
            "analysis_options": {
                "include_ziwu": True,
                "include_constitution": True,
                "include_bagua": True,
                "include_wuyun_liuqi": True
            }
        }
        
        response = client.post("/api/v1/calculation/comprehensive", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        
        result = data["data"]
        assert "个人信息" in result
        assert "分析时间" in result
        assert "子午流注分析" in result
        assert "体质分析" in result
        assert "八卦分析" in result
        assert "运气分析" in result
    
    def test_api_ziwu_analysis(self, client):
        """测试API子午流注分析接口"""
        request_data = {
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        response = client.post("/api/v1/calculation/ziwu", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        
        result = data["data"]
        assert "当前时辰" in result
        assert "当前经络" in result
    
    def test_api_constitution_analysis(self, client, sample_birth_info):
        """测试API体质分析接口"""
        response = client.post("/api/v1/calculation/constitution", json=sample_birth_info)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        
        result = data["data"]
        assert "八字信息" in result
        assert "体质类型" in result
    
    def test_api_bagua_analysis(self, client, sample_birth_info):
        """测试API八卦分析接口"""
        response = client.post("/api/v1/calculation/bagua", json=sample_birth_info)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        
        result = data["data"]
        assert "本命卦" in result
        assert "健康分析" in result
    
    def test_api_wuyun_analysis(self, client):
        """测试API五运六气分析接口"""
        request_data = {"year": 2024}
        
        response = client.post("/api/v1/calculation/wuyun", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        
        result = data["data"]
        assert "五运分析" in result
        assert "司天在泉" in result
    
    def test_api_health_check(self, client):
        """测试API健康检查接口"""
        response = client.get("/api/v1/calculation/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "algorithms" in data
        assert "cache" in data
        assert "timestamp" in data
    
    def test_error_handling(self, client):
        """测试错误处理"""
        # 测试无效的出生信息
        invalid_birth_info = {
            "year": "invalid",
            "month": 13,
            "day": 32,
            "hour": 25,
            "gender": "unknown"
        }
        
        response = client.post("/api/v1/calculation/constitution", json=invalid_birth_info)
        assert response.status_code == 400
        
        data = response.json()
        assert data["success"] == False
        assert "error_code" in data
    
    def test_cache_endpoints(self, client):
        """测试缓存管理接口"""
        # 测试缓存统计
        response = client.get("/cache/stats")
        assert response.status_code == 200
        
        # 测试清理缓存
        response = client.post("/cache/clear")
        assert response.status_code == 200
        
        # 测试清理过期缓存
        response = client.post("/cache/cleanup")
        assert response.status_code == 200

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"]) 