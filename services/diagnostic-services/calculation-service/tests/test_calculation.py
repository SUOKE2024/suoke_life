"""
算诊功能测试
"""

import pytest
from datetime import datetime
from calculation_service.core.algorithms.ziwu_liuzhu.calculator import ZiwuLiuzhuCalculator
from calculation_service.core.algorithms.constitution.calculator import ConstitutionCalculator
from calculation_service.core.algorithms.bagua.calculator import BaguaCalculator
from calculation_service.core.algorithms.wuyun_liuqi.calculator import WuyunLiuqiCalculator
from calculation_service.core.algorithms.comprehensive_calculator import ComprehensiveCalculator


class TestZiwuLiuzhu:
    """子午流注测试"""
    
    def setup_method(self):
        self.calculator = ZiwuLiuzhuCalculator()
    
    def test_analyze_current_time(self):
        """测试当前时间分析"""
        dt = datetime(2024, 1, 15, 14, 30)  # 下午2:30
        result = self.calculator.analyze_current_time(dt)
        
        assert "当前时辰" in result
        assert "当前经络" in result
        assert "最佳治疗时间" in result
        assert result["当前时辰"] == "未时"
    
    def test_get_meridian_schedule(self):
        """测试经络时间表"""
        schedule = self.calculator.get_meridian_schedule()
        
        assert len(schedule) == 12
        assert "子时" in schedule
        assert schedule["子时"]["经络"] == "胆经"


class TestConstitution:
    """体质分析测试"""
    
    def setup_method(self):
        self.calculator = ConstitutionCalculator()
    
    def test_analyze_constitution(self):
        """测试体质分析"""
        birth_info = {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 14,
            "gender": "男"
        }
        
        result = self.calculator.analyze_constitution(birth_info)
        
        assert "八字信息" in result
        assert "体质分析" in result
        assert "调理建议" in result
        assert "五行强弱" in result
    
    def test_calculate_bazi(self):
        """测试八字计算"""
        birth_info = {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 14
        }
        
        bazi = self.calculator.calculate_bazi(birth_info)
        
        assert "年柱" in bazi
        assert "月柱" in bazi
        assert "日柱" in bazi
        assert "时柱" in bazi


class TestBagua:
    """八卦分析测试"""
    
    def setup_method(self):
        self.calculator = BaguaCalculator()
    
    def test_analyze_personal_bagua(self):
        """测试个人八卦分析"""
        birth_info = {
            "year": 1990,
            "month": 5,
            "day": 15,
            "gender": "男"
        }
        
        result = self.calculator.analyze_personal_bagua(birth_info)
        
        assert "本命卦" in result
        assert "健康分析" in result
        assert "调理建议" in result
        assert "方位指导" in result
    
    def test_calculate_benming_gua(self):
        """测试本命卦计算"""
        birth_info = {
            "year": 1990,
            "gender": "男"
        }
        
        gua = self.calculator.calculate_benming_gua(birth_info)
        
        assert gua in ["乾", "坤", "震", "巽", "坎", "离", "艮", "兑"]


class TestWuyunLiuqi:
    """五运六气测试"""
    
    def setup_method(self):
        self.calculator = WuyunLiuqiCalculator()
    
    def test_analyze_current_period(self):
        """测试当前时期分析"""
        dt = datetime(2024, 5, 15)
        result = self.calculator.analyze_current_period(dt)
        
        assert "五运分析" in result
        assert "司天在泉" in result
        assert "当前气分析" in result
        assert "疾病预测" in result
        assert "调养建议" in result
    
    def test_get_wuyun(self):
        """测试五运获取"""
        wuyun = self.calculator.get_wuyun(2024)
        
        assert "运" in wuyun
        assert "五行" in wuyun
        assert "脏腑" in wuyun
    
    def test_get_yearly_prediction(self):
        """测试年度预测"""
        prediction = self.calculator.get_yearly_prediction(2024)
        
        assert "年份" in prediction
        assert "年运总览" in prediction
        assert "分期预测" in prediction
        assert "全年建议" in prediction


class TestComprehensiveCalculator:
    """综合算诊测试"""
    
    def setup_method(self):
        self.calculator = ComprehensiveCalculator()
    
    def test_comprehensive_analysis(self):
        """测试综合分析"""
        birth_info = {
            "year": 1990,
            "month": 5,
            "day": 15,
            "hour": 14,
            "gender": "男",
            "name": "测试用户"
        }
        
        analysis_date = datetime(2024, 5, 15)
        
        result = self.calculator.comprehensive_analysis(
            birth_info=birth_info,
            analysis_date=analysis_date
        )
        
        assert "个人信息" in result
        assert "分析时间" in result
        assert "子午流注分析" in result
        assert "体质分析" in result
        assert "八卦分析" in result
        assert "运气分析" in result
        assert "综合建议" in result
        assert "调养重点" in result
    
    def test_generate_health_advice(self):
        """测试健康建议生成"""
        # 模拟各种分析结果
        ziwu_result = {"最佳治疗时间": ["子时", "午时"]}
        constitution_result = {"体质类型": "平和质"}
        bagua_result = {"本命卦": "乾卦"}
        wuyun_result = {"总体特点": "木运太过"}
        
        advice = self.calculator._generate_health_advice(
            ziwu_result, constitution_result, bagua_result, wuyun_result
        )
        
        assert "饮食调养" in advice
        assert "起居调养" in advice
        assert "情志调养" in advice
        assert "运动调养" in advice


if __name__ == "__main__":
    pytest.main([__file__]) 