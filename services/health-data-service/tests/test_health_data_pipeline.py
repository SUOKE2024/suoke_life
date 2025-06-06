"""
test_health_data_pipeline - 索克生活项目模块
"""

from health_data_service.core.data_standardization import (
from health_data_service.services.health_data_pipeline import (
import asyncio
import json
import os
import pytest
import sys

#!/usr/bin/env python3
"""
健康数据流水线测试

测试健康数据的完整处理流程，包括数据标准化、零知识验证和区块链存储。
"""


# 导入测试模块
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

    DataType, 
    DataQuality,
    standardize_vital_signs,
    standardize_lab_results,
    standardize_wearable_data,
    standardize_tcm_look_data,
    standardize_tcm_listen_data,
    standardize_tcm_inquiry_data,
    standardize_tcm_palpation_data,
    standardize_tcm_calculation_data
)

    HealthDataPipeline,
    PipelineConfig,
    PipelineStage,
    ProcessingStatus,
    process_vital_signs,
    process_lab_results,
    process_wearable_data,
    process_tcm_look_data,
    process_tcm_listen_data,
    process_tcm_inquiry_data,
    process_tcm_palpation_data,
    process_tcm_calculation_data
)

class TestHealthDataPipeline:
    """健康数据流水线测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.pipeline = HealthDataPipeline()
        self.test_user_id = "test_user_001"
    
    @pytest.mark.asyncio
    async def test_vital_signs_pipeline(self):
        """测试生命体征数据流水线"""
        print("\n=== 测试生命体征数据流水线 ===")
        
        # 测试数据
        vital_signs_data = {
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "heart_rate": 72,
            "temperature": 36.5,
            "oxygen_saturation": 98.5
        }
        
        print(f"原始数据: {json.dumps(vital_signs_data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        result = await self.pipeline.process_health_data(
            data=vital_signs_data,
            data_type=DataType.VITAL_SIGNS,
            user_id=self.test_user_id,
            source="manual_input"
        )
        
        # 验证结果
        assert result.status == ProcessingStatus.SUCCESS
        assert result.stage == PipelineStage.COMPLETED
        assert result.standardized_data is not None
        assert result.privacy_proof is not None
        
        print(f"处理状态: {result.status.value}")
        print(f"处理阶段: {result.stage.value}")
        print(f"数据质量分数: {result.standardized_data.quality_score}")
        print(f"质量等级: {result.standardized_data.quality_level.value}")
        print(f"处理时间: {result.processing_time:.3f}秒")
        
        # 检查标准化数据
        standardized = result.standardized_data.standardized_data
        assert "mean_arterial_pressure" in standardized
        assert "bp_category" in standardized
        
        print(f"平均动脉压: {standardized['mean_arterial_pressure']}")
        print(f"血压分类: {standardized['bp_category']}")
        
        # 检查隐私证明
        assert result.privacy_proof.data_hash is not None
        print(f"数据哈希: {result.privacy_proof.data_hash}")
        
        print("✅ 生命体征数据流水线测试通过")
    
    @pytest.mark.asyncio
    async def test_lab_results_pipeline(self):
        """测试检验结果数据流水线"""
        print("\n=== 测试检验结果数据流水线 ===")
        
        # 测试数据
        lab_data = {
            "glucose": 95.0,
            "cholesterol_total": 180.0,
            "hdl_cholesterol": 55.0,
            "ldl_cholesterol": 110.0,
            "triglycerides": 120.0,
            "hemoglobin": 14.5
        }
        
        print(f"原始数据: {json.dumps(lab_data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        result = await self.pipeline.process_health_data(
            data=lab_data,
            data_type=DataType.LAB_RESULTS,
            user_id=self.test_user_id,
            source="laboratory"
        )
        
        # 验证结果
        assert result.status == ProcessingStatus.SUCCESS
        assert result.standardized_data is not None
        
        print(f"处理状态: {result.status.value}")
        print(f"数据质量分数: {result.standardized_data.quality_score}")
        
        # 检查标准化数据
        standardized = result.standardized_data.standardized_data
        assert "glucose_category" in standardized
        assert "cholesterol_ratio" in standardized
        
        print(f"血糖分类: {standardized['glucose_category']}")
        print(f"胆固醇比值: {standardized['cholesterol_ratio']}")
        
        # 检查单位转换
        if "glucose_mmol" in standardized:
            print(f"血糖值 (mmol/L): {standardized['glucose_mmol']:.2f}")
        
        print("✅ 检验结果数据流水线测试通过")
    
    @pytest.mark.asyncio
    async def test_wearable_data_pipeline(self):
        """测试可穿戴设备数据流水线"""
        print("\n=== 测试可穿戴设备数据流水线 ===")
        
        # 测试数据
        wearable_data = {
            "steps": 8500,
            "distance": 6.2,
            "calories_burned": 320,
            "sleep_duration": 7.5,
            "sleep_quality": 85.0
        }
        
        print(f"原始数据: {json.dumps(wearable_data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        result = await self.pipeline.process_health_data(
            data=wearable_data,
            data_type=DataType.WEARABLE_DATA,
            user_id=self.test_user_id,
            source="smartwatch"
        )
        
        # 验证结果
        assert result.status == ProcessingStatus.SUCCESS
        assert result.standardized_data is not None
        
        print(f"处理状态: {result.status.value}")
        print(f"数据质量分数: {result.standardized_data.quality_score}")
        
        # 检查单位转换
        standardized = result.standardized_data.standardized_data
        if "distance_miles" in standardized:
            print(f"距离 (英里): {standardized['distance_miles']:.2f}")
        
        print("✅ 可穿戴设备数据流水线测试通过")
    
    @pytest.mark.asyncio
    async def test_batch_processing(self):
        """测试批量处理"""
        print("\n=== 测试批量数据处理 ===")
        
        # 批量测试数据
        batch_data = [
            {"systolic_bp": 110, "diastolic_bp": 70, "heart_rate": 68},
            {"systolic_bp": 125, "diastolic_bp": 82, "heart_rate": 75},
            {"systolic_bp": 135, "diastolic_bp": 88, "heart_rate": 80},
        ]
        
        print(f"批量处理 {len(batch_data)} 条生命体征数据")
        
        # 批量处理
        results = await self.pipeline.batch_process_health_data(
            data_list=batch_data,
            data_type=DataType.VITAL_SIGNS,
            user_id=self.test_user_id,
            source="batch_import"
        )
        
        # 验证结果
        assert len(results) == len(batch_data)
        
        success_count = sum(1 for r in results if r.status == ProcessingStatus.SUCCESS)
        print(f"成功处理: {success_count}/{len(results)}")
        
        for i, result in enumerate(results):
            print(f"数据 {i+1}: {result.status.value}, 质量分数: {result.standardized_data.quality_score if result.standardized_data else 'N/A'}")
        
        print("✅ 批量处理测试通过")
    
    @pytest.mark.asyncio
    async def test_data_validation_errors(self):
        """测试数据验证错误处理"""
        print("\n=== 测试数据验证错误处理 ===")
        
        # 无效数据
        invalid_data = {
            "systolic_bp": 300,  # 超出范围
            "diastolic_bp": 200,  # 超出范围
            "heart_rate": -10     # 负值
        }
        
        print(f"无效数据: {json.dumps(invalid_data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        result = await self.pipeline.process_health_data(
            data=invalid_data,
            data_type=DataType.VITAL_SIGNS,
            user_id=self.test_user_id,
            source="test"
        )
        
        # 验证错误处理
        assert len(result.errors) > 0
        print(f"验证错误: {result.errors}")
        
        if result.standardized_data:
            print(f"数据质量分数: {result.standardized_data.quality_score}")
            print(f"质量等级: {result.standardized_data.quality_level.value}")
        
        print("✅ 数据验证错误处理测试通过")
    
    @pytest.mark.asyncio
    async def test_privacy_proof_verification(self):
        """测试隐私证明验证"""
        print("\n=== 测试隐私证明验证 ===")
        
        # 正常数据
        data = {
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "heart_rate": 72
        }
        
        # 处理数据
        result = await self.pipeline.process_health_data(
            data=data,
            data_type=DataType.VITAL_SIGNS,
            user_id=self.test_user_id,
            source="test"
        )
        
        # 验证隐私证明
        if result.privacy_proof:
            verification_result = await self.pipeline.verify_privacy_proof(result.privacy_proof)
            print(f"隐私证明验证结果: {verification_result}")
            assert verification_result is True
        
        print("✅ 隐私证明验证测试通过")
    
    def test_pipeline_statistics(self):
        """测试流水线统计信息"""
        print("\n=== 测试流水线统计信息 ===")
        
        stats = self.pipeline.get_pipeline_statistics()
        print(f"统计信息: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        
        assert "total_processed" in stats
        assert "success_count" in stats
        assert "success_rate" in stats
        
        print("✅ 流水线统计信息测试通过")
    
    @pytest.mark.asyncio
    async def test_tcm_look_data_pipeline(self):
        """测试中医望诊数据流水线"""
        print("\n=== 测试中医望诊数据流水线 ===")
        
        # 测试数据
        tcm_look_data = {
            "face_color": "红润",
            "face_luster": "有神",
            "tongue_color": "淡红",
            "tongue_coating": "薄白",
            "tongue_texture": "正常",
            "body_posture": "端正",
            "gait": "正常"
        }
        
        print(f"原始数据: {json.dumps(tcm_look_data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        result = await self.pipeline.process_health_data(
            data=tcm_look_data,
            data_type=DataType.TCM_LOOK,
            user_id=self.test_user_id,
            source="tcm_clinic"
        )
        
        # 验证结果
        assert result.status == ProcessingStatus.SUCCESS
        assert result.standardized_data is not None
        
        print(f"处理状态: {result.status.value}")
        print(f"数据质量分数: {result.standardized_data.quality_score}")
        print("✅ 中医望诊数据流水线测试通过")
    
    @pytest.mark.asyncio
    async def test_tcm_inquiry_data_pipeline(self):
        """测试中医问诊数据流水线"""
        print("\n=== 测试中医问诊数据流水线 ===")
        
        # 测试数据
        tcm_inquiry_data = {
            "chief_complaint": "头痛眩晕，心悸失眠",
            "symptom_duration": "慢性",
            "cold_heat": "无明显寒热",
            "sweating": "盗汗",
            "appetite": "食欲不振",
            "sleep_quality": "失眠",
            "urination": "正常",
            "defecation": "便溏"
        }
        
        print(f"原始数据: {json.dumps(tcm_inquiry_data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        result = await self.pipeline.process_health_data(
            data=tcm_inquiry_data,
            data_type=DataType.TCM_INQUIRY,
            user_id=self.test_user_id,
            source="tcm_clinic"
        )
        
        # 验证结果
        assert result.status == ProcessingStatus.SUCCESS
        assert result.standardized_data is not None
        
        print(f"处理状态: {result.status.value}")
        print(f"数据质量分数: {result.standardized_data.quality_score}")
        print("✅ 中医问诊数据流水线测试通过")
    
    @pytest.mark.asyncio
    async def test_tcm_palpation_data_pipeline(self):
        """测试中医切诊数据流水线"""
        print("\n=== 测试中医切诊数据流水线 ===")
        
        # 测试数据
        tcm_palpation_data = {
            "pulse_position": "浮",
            "pulse_rate": "数",
            "pulse_rhythm": "规律",
            "pulse_strength": "有力",
            "pulse_shape": "弦",
            "skin_temperature": "正常",
            "skin_moisture": "正常",
            "skin_elasticity": "正常",
            "abdominal_tension": "正常",
            "abdominal_pain": "无"
        }
        
        print(f"原始数据: {json.dumps(tcm_palpation_data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        result = await self.pipeline.process_health_data(
            data=tcm_palpation_data,
            data_type=DataType.TCM_PALPATION,
            user_id=self.test_user_id,
            source="tcm_clinic"
        )
        
        # 验证结果
        assert result.status == ProcessingStatus.SUCCESS
        assert result.standardized_data is not None
        
        print(f"处理状态: {result.status.value}")
        print(f"数据质量分数: {result.standardized_data.quality_score}")
        print("✅ 中医切诊数据流水线测试通过")
    
    @pytest.mark.asyncio
    async def test_tcm_calculation_data_pipeline(self):
        """测试中医算诊数据流水线"""
        print("\n=== 测试中医算诊数据流水线 ===")
        
        # 测试数据
        tcm_calculation_data = {
            "birth_year": 1990,
            "birth_month": 5,
            "birth_day": 15,
            "birth_hour": 14,
            "gender": "女",
            "current_meridian": "心经",
            "constitution_type": "气虚质",
            "five_elements_score": {
                "wood": 75.0,
                "fire": 60.0,
                "earth": 80.0,
                "metal": 70.0,
                "water": 65.0
            },
            "life_hexagram": "坤",
            "health_direction": "西南",
            "health_risk_level": "中"
        }
        
        print(f"原始数据: {json.dumps(tcm_calculation_data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        result = await self.pipeline.process_health_data(
            data=tcm_calculation_data,
            data_type=DataType.TCM_CALCULATION,
            user_id=self.test_user_id,
            source="tcm_calculation"
        )
        
        # 验证结果
        assert result.status == ProcessingStatus.SUCCESS
        assert result.standardized_data is not None
        
        print(f"处理状态: {result.status.value}")
        print(f"数据质量分数: {result.standardized_data.quality_score}")
        print(f"体质类型: {tcm_calculation_data['constitution_type']}")
        print(f"本命卦: {tcm_calculation_data['life_hexagram']}")
        print("✅ 中医算诊数据流水线测试通过")

class TestDataStandardization:
    """数据标准化测试类"""
    
    def test_vital_signs_standardization(self):
        """测试生命体征标准化"""
        print("\n=== 测试生命体征标准化 ===")
        
        data = {
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "heart_rate": 72,
            "temperature": 36.5
        }
        
        result = standardize_vital_signs(data)
        
        assert result.data_type == DataType.VITAL_SIGNS
        assert result.quality_level in [DataQuality.HIGH, DataQuality.MEDIUM]
        
        print(f"质量分数: {result.quality_score}")
        print(f"标准化字段: {list(result.standardized_data.keys())}")
        
        print("✅ 生命体征标准化测试通过")
    
    def test_lab_results_standardization(self):
        """测试检验结果标准化"""
        print("\n=== 测试检验结果标准化 ===")
        
        data = {
            "glucose": 95.0,
            "cholesterol_total": 180.0,
            "hdl_cholesterol": 55.0
        }
        
        result = standardize_lab_results(data)
        
        assert result.data_type == DataType.LAB_RESULTS
        print(f"质量分数: {result.quality_score}")
        print(f"血糖分类: {result.standardized_data.get('glucose_category', 'N/A')}")
        
        print("✅ 检验结果标准化测试通过")

async def run_comprehensive_test():
    """运行综合测试"""
    print("🚀 开始健康数据流水线综合测试")
    print("=" * 60)
    
    # 创建测试实例
    pipeline_test = TestHealthDataPipeline()
    pipeline_test.setup_method()
    
    standardization_test = TestDataStandardization()
    
    try:
        # 运行数据标准化测试
        standardization_test.test_vital_signs_standardization()
        standardization_test.test_lab_results_standardization()
        
        # 运行流水线测试
        await pipeline_test.test_vital_signs_pipeline()
        await pipeline_test.test_lab_results_pipeline()
        await pipeline_test.test_wearable_data_pipeline()
        await pipeline_test.test_batch_processing()
        await pipeline_test.test_data_validation_errors()
        await pipeline_test.test_privacy_proof_verification()
        pipeline_test.test_pipeline_statistics()
        await pipeline_test.test_tcm_look_data_pipeline()
        await pipeline_test.test_tcm_inquiry_data_pipeline()
        await pipeline_test.test_tcm_palpation_data_pipeline()
        await pipeline_test.test_tcm_calculation_data_pipeline()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！健康数据流水线功能正常")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        raise

def demo_health_data_processing():
    """演示健康数据处理"""
    print("\n📊 健康数据处理演示")
    print("=" * 40)
    
    # 演示数据
    demo_data = {
        "生命体征": {
            "systolic_bp": 125,
            "diastolic_bp": 82,
            "heart_rate": 75,
            "temperature": 36.8,
            "oxygen_saturation": 97.5
        },
        "检验结果": {
            "glucose": 105.0,
            "cholesterol_total": 195.0,
            "hdl_cholesterol": 48.0,
            "ldl_cholesterol": 125.0,
            "hemoglobin": 13.8
        },
        "可穿戴设备": {
            "steps": 12500,
            "distance": 9.2,
            "calories_burned": 450,
            "sleep_duration": 6.8,
            "sleep_quality": 78.0
        }
    }
    
    for data_name, data_values in demo_data.items():
        print(f"\n{data_name}数据:")
        for key, value in data_values.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    # 演示数据处理
    demo_health_data_processing()
    
    # 运行综合测试
    asyncio.run(run_comprehensive_test()) 