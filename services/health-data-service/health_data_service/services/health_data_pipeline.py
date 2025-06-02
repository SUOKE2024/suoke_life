#!/usr/bin/env python3
"""
健康数据流水线服务

集成零知识验证和数据标准化功能，提供完整的健康数据处理流水线。
支持数据收集、标准化、隐私保护验证、存储和查询等功能。
"""

import asyncio
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging
from enum import Enum

# 导入零知识验证模块
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../common/security'))

try:
    from zk_snarks import (
        HealthDataZKService, 
        HealthDataProof, 
        get_zk_service,
        prove_blood_pressure_valid,
        prove_blood_glucose_valid,
        verify_health_proof
    )
except ImportError:
    logging.warning("无法导入零知识验证模块，使用模拟实现")
    
    # 模拟实现
    @dataclass
    class HealthDataProof:
        proof: Dict[str, Any]
        public_inputs: Dict[str, Any]
        verification_key: Dict[str, Any]
        timestamp: str
        data_hash: str
    
    class HealthDataZKService:
        def prove_health_data_validity(self, data_type, health_data, validation_params):
            return HealthDataProof(
                proof={"mock": True},
                public_inputs=validation_params,
                verification_key={"mock": True},
                timestamp=datetime.now().isoformat(),
                data_hash="mock_hash"
            )
        
        def verify_health_data_proof(self, proof):
            return True
    
    def get_zk_service():
        return HealthDataZKService()

# 导入数据标准化模块
from ..core.data_standardization import (
    HealthDataStandardizer,
    StandardizedData,
    DataType,
    DataQuality,
    get_standardizer
)

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """流水线阶段"""
    COLLECTION = "collection"  # 数据收集
    VALIDATION = "validation"  # 数据验证
    STANDARDIZATION = "standardization"  # 数据标准化
    PRIVACY_PROOF = "privacy_proof"  # 隐私证明
    STORAGE = "storage"  # 数据存储
    COMPLETED = "completed"  # 完成


class ProcessingStatus(Enum):
    """处理状态"""
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    SUCCESS = "success"  # 成功
    FAILED = "failed"  # 失败
    PARTIAL = "partial"  # 部分成功


@dataclass
class PipelineResult:
    """流水线处理结果"""
    pipeline_id: str
    original_data: Dict[str, Any]
    standardized_data: Optional[StandardizedData]
    privacy_proof: Optional[HealthDataProof]
    stage: PipelineStage
    status: ProcessingStatus
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    processing_time: float
    timestamp: str


@dataclass
class PipelineConfig:
    """流水线配置"""
    enable_standardization: bool = True
    enable_privacy_proof: bool = True
    enable_quality_check: bool = True
    min_quality_score: float = 70.0
    privacy_proof_types: List[str] = None
    storage_options: Dict[str, Any] = None


class HealthDataPipeline:
    """健康数据流水线"""
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """初始化流水线"""
        self.config = config or PipelineConfig()
        self.standardizer = get_standardizer()
        self.zk_service = get_zk_service()
        self.processing_cache = {}
        
        # 初始化默认隐私证明类型
        if self.config.privacy_proof_types is None:
            self.config.privacy_proof_types = [
                "blood_pressure", "blood_glucose", "age", "data_integrity"
            ]
    
    async def process_health_data(
        self,
        data: Dict[str, Any],
        data_type: DataType,
        user_id: str,
        source: str = "unknown"
    ) -> PipelineResult:
        """
        处理健康数据
        
        Args:
            data: 健康数据
            data_type: 数据类型
            user_id: 用户ID
            source: 数据来源
            
        Returns:
            PipelineResult: 处理结果
        """
        pipeline_id = f"{user_id}_{data_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"开始处理健康数据流水线: {pipeline_id}")
        
        result = PipelineResult(
            pipeline_id=pipeline_id,
            original_data=data,
            standardized_data=None,
            privacy_proof=None,
            stage=PipelineStage.COLLECTION,
            status=ProcessingStatus.PROCESSING,
            errors=[],
            warnings=[],
            metadata={
                "user_id": user_id,
                "source": source,
                "data_type": data_type.value,
                "start_time": start_time.isoformat()
            },
            processing_time=0.0,
            timestamp=start_time.isoformat()
        )
        
        try:
            # 阶段1: 数据验证
            result.stage = PipelineStage.VALIDATION
            validation_result = await self._validate_input_data(data, data_type)
            if not validation_result["valid"]:
                result.errors.extend(validation_result["errors"])
                result.status = ProcessingStatus.FAILED
                return result
            
            # 阶段2: 数据标准化
            if self.config.enable_standardization:
                result.stage = PipelineStage.STANDARDIZATION
                standardized_data = await self._standardize_data(data, data_type)
                result.standardized_data = standardized_data
                
                # 质量检查
                if self.config.enable_quality_check:
                    if standardized_data.quality_score < self.config.min_quality_score:
                        result.warnings.append(
                            f"数据质量分数 {standardized_data.quality_score} 低于最低要求 {self.config.min_quality_score}"
                        )
                
                result.errors.extend(standardized_data.validation_errors)
                result.warnings.extend(standardized_data.validation_warnings)
            
            # 阶段3: 隐私证明生成
            if self.config.enable_privacy_proof and result.standardized_data:
                result.stage = PipelineStage.PRIVACY_PROOF
                privacy_proof = await self._generate_privacy_proof(
                    result.standardized_data, data_type
                )
                result.privacy_proof = privacy_proof
            
            # 阶段4: 数据存储
            result.stage = PipelineStage.STORAGE
            storage_result = await self._store_processed_data(result)
            if not storage_result["success"]:
                result.errors.extend(storage_result["errors"])
                result.status = ProcessingStatus.PARTIAL
            else:
                result.stage = PipelineStage.COMPLETED
                result.status = ProcessingStatus.SUCCESS
            
        except Exception as e:
            logger.error(f"处理流水线时发生错误: {e}")
            result.errors.append(f"流水线处理失败: {str(e)}")
            result.status = ProcessingStatus.FAILED
        
        finally:
            # 计算处理时间
            end_time = datetime.now()
            result.processing_time = (end_time - start_time).total_seconds()
            result.metadata["end_time"] = end_time.isoformat()
            
            logger.info(f"流水线处理完成: {pipeline_id}, 状态: {result.status.value}")
        
        return result
    
    async def _validate_input_data(
        self, 
        data: Dict[str, Any], 
        data_type: DataType
    ) -> Dict[str, Any]:
        """验证输入数据"""
        errors = []
        
        # 基本验证
        if not data:
            errors.append("输入数据为空")
        
        if not isinstance(data, dict):
            errors.append("输入数据必须是字典格式")
        
        # 数据类型特定验证
        if data_type == DataType.VITAL_SIGNS:
            required_fields = ["systolic_bp", "diastolic_bp"]
            for field in required_fields:
                if field not in data:
                    errors.append(f"生命体征数据缺少必填字段: {field}")
        
        elif data_type == DataType.LAB_RESULTS:
            # 检验结果至少需要一个指标
            lab_fields = ["glucose", "cholesterol_total", "hemoglobin"]
            if not any(field in data for field in lab_fields):
                errors.append("检验结果数据至少需要包含一个检验指标")
        
        # 中医五诊数据验证
        elif data_type == DataType.TCM_LOOK:
            # 望诊数据至少需要一个观察项
            look_fields = ["face_color", "tongue_color", "body_posture"]
            if not any(field in data for field in look_fields):
                errors.append("望诊数据至少需要包含一个观察项")
        
        elif data_type == DataType.TCM_LISTEN:
            # 闻诊数据至少需要一个听诊项
            listen_fields = ["voice_strength", "breathing_sound", "heart_sound_rhythm"]
            if not any(field in data for field in listen_fields):
                errors.append("闻诊数据至少需要包含一个听诊项")
        
        elif data_type == DataType.TCM_INQUIRY:
            # 问诊数据必须包含主诉
            if "chief_complaint" not in data:
                errors.append("问诊数据必须包含主诉症状")
        
        elif data_type == DataType.TCM_PALPATION:
            # 切诊数据至少需要一个触诊项
            palpation_fields = ["pulse_position", "skin_temperature", "abdominal_tension"]
            if not any(field in data for field in palpation_fields):
                errors.append("切诊数据至少需要包含一个触诊项")
        
        elif data_type == DataType.TCM_CALCULATION:
            # 算诊数据必须包含基础信息
            required_calc_fields = ["birth_year", "birth_month", "birth_day", "birth_hour", "gender"]
            for field in required_calc_fields:
                if field not in data:
                    errors.append(f"算诊数据缺少必填字段: {field}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _standardize_data(
        self, 
        data: Dict[str, Any], 
        data_type: DataType
    ) -> StandardizedData:
        """标准化数据"""
        logger.info(f"开始标准化 {data_type.value} 数据")
        
        # 使用标准化器处理数据
        standardized_data = self.standardizer.standardize_data(
            raw_data=data,
            data_type=data_type,
            source_format="json"
        )
        
        logger.info(f"数据标准化完成，质量分数: {standardized_data.quality_score}")
        return standardized_data
    
    async def _generate_privacy_proof(
        self, 
        standardized_data: StandardizedData, 
        data_type: DataType
    ) -> Optional[HealthDataProof]:
        """生成隐私证明"""
        logger.info(f"开始生成 {data_type.value} 数据的隐私证明")
        
        try:
            # 根据数据类型选择合适的证明方法
            if data_type == DataType.VITAL_SIGNS:
                return await self._generate_vital_signs_proof(standardized_data)
            elif data_type == DataType.LAB_RESULTS:
                return await self._generate_lab_results_proof(standardized_data)
            elif data_type == DataType.WEARABLE_DATA:
                return await self._generate_wearable_data_proof(standardized_data)
            else:
                # 通用数据完整性证明
                return await self._generate_integrity_proof(standardized_data)
        
        except Exception as e:
            logger.error(f"生成隐私证明时发生错误: {e}")
            return None
    
    async def _generate_vital_signs_proof(
        self, 
        standardized_data: StandardizedData
    ) -> Optional[HealthDataProof]:
        """生成生命体征隐私证明"""
        data = standardized_data.standardized_data
        
        # 血压证明
        if "systolic_bp" in data and "diastolic_bp" in data:
            try:
                proof = self.zk_service.prove_health_data_validity(
                    data_type="blood_pressure",
                    health_data={
                        "systolic": data["systolic_bp"],
                        "diastolic": data["diastolic_bp"]
                    },
                    validation_params={"valid_bp": 1}
                )
                return proof
            except Exception as e:
                logger.error(f"生成血压证明失败: {e}")
        
        return None
    
    async def _generate_lab_results_proof(
        self, 
        standardized_data: StandardizedData
    ) -> Optional[HealthDataProof]:
        """生成检验结果隐私证明"""
        data = standardized_data.standardized_data
        
        # 血糖证明
        if "glucose" in data:
            try:
                proof = self.zk_service.prove_health_data_validity(
                    data_type="blood_glucose",
                    health_data={"glucose": int(data["glucose"])},
                    validation_params={"valid_glucose": 1}
                )
                return proof
            except Exception as e:
                logger.error(f"生成血糖证明失败: {e}")
        
        return None
    
    async def _generate_wearable_data_proof(
        self, 
        standardized_data: StandardizedData
    ) -> Optional[HealthDataProof]:
        """生成可穿戴设备数据隐私证明"""
        # 对于可穿戴设备数据，主要验证数据完整性
        return await self._generate_integrity_proof(standardized_data)
    
    async def _generate_integrity_proof(
        self, 
        standardized_data: StandardizedData
    ) -> Optional[HealthDataProof]:
        """生成数据完整性证明"""
        try:
            # 计算数据哈希
            data_hash = self._calculate_data_hash(standardized_data.standardized_data)
            current_time = int(datetime.now().timestamp())
            
            proof = self.zk_service.prove_health_data_validity(
                data_type="data_integrity",
                health_data={
                    "data_hash": data_hash,
                    "timestamp": current_time
                },
                validation_params={
                    "data_valid": 1,
                    "expected_hash": data_hash
                }
            )
            return proof
        except Exception as e:
            logger.error(f"生成完整性证明失败: {e}")
            return None
    
    def _calculate_data_hash(self, data: Dict[str, Any]) -> int:
        """计算数据哈希（简化版本）"""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.sha256(data_str.encode())
        # 转换为整数（取前8字节）
        return int.from_bytes(hash_obj.digest()[:8], byteorder='big')
    
    async def _store_processed_data(self, result: PipelineResult) -> Dict[str, Any]:
        """存储处理后的数据"""
        logger.info(f"存储处理结果: {result.pipeline_id}")
        
        try:
            # 这里应该连接到实际的存储系统
            # 目前使用内存缓存模拟
            self.processing_cache[result.pipeline_id] = {
                "result": asdict(result),
                "stored_at": datetime.now().isoformat()
            }
            
            return {"success": True, "errors": []}
        
        except Exception as e:
            logger.error(f"存储数据时发生错误: {e}")
            return {"success": False, "errors": [str(e)]}
    
    async def batch_process_health_data(
        self,
        data_list: List[Dict[str, Any]],
        data_type: DataType,
        user_id: str,
        source: str = "batch"
    ) -> List[PipelineResult]:
        """批量处理健康数据"""
        logger.info(f"开始批量处理 {len(data_list)} 条健康数据")
        
        tasks = []
        for i, data in enumerate(data_list):
            task = self.process_health_data(
                data=data,
                data_type=data_type,
                user_id=f"{user_id}_batch_{i}",
                source=source
            )
            tasks.append(task)
        
        # 并发处理
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"批量处理第 {i+1} 条数据时发生异常: {result}")
                error_result = PipelineResult(
                    pipeline_id=f"{user_id}_batch_{i}_error",
                    original_data=data_list[i],
                    standardized_data=None,
                    privacy_proof=None,
                    stage=PipelineStage.COLLECTION,
                    status=ProcessingStatus.FAILED,
                    errors=[f"处理异常: {str(result)}"],
                    warnings=[],
                    metadata={"batch_index": i},
                    processing_time=0.0,
                    timestamp=datetime.now().isoformat()
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def verify_privacy_proof(self, proof: HealthDataProof) -> bool:
        """验证隐私证明"""
        try:
            return self.zk_service.verify_health_data_proof(proof)
        except Exception as e:
            logger.error(f"验证隐私证明时发生错误: {e}")
            return False
    
    def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """获取流水线状态"""
        if pipeline_id in self.processing_cache:
            return self.processing_cache[pipeline_id]
        return None
    
    def get_pipeline_statistics(self) -> Dict[str, Any]:
        """获取流水线统计信息"""
        total_processed = len(self.processing_cache)
        success_count = sum(
            1 for item in self.processing_cache.values()
            if item["result"]["status"] == ProcessingStatus.SUCCESS.value
        )
        
        return {
            "total_processed": total_processed,
            "success_count": success_count,
            "success_rate": success_count / total_processed if total_processed > 0 else 0,
            "cache_size": total_processed
        }


# 全局流水线实例
_pipeline = None


def get_health_data_pipeline(config: Optional[PipelineConfig] = None) -> HealthDataPipeline:
    """获取健康数据流水线实例"""
    global _pipeline
    if _pipeline is None:
        _pipeline = HealthDataPipeline(config)
    return _pipeline


# 便捷函数
async def process_vital_signs(
    data: Dict[str, Any], 
    user_id: str, 
    source: str = "manual"
) -> PipelineResult:
    """处理生命体征数据"""
    pipeline = get_health_data_pipeline()
    return await pipeline.process_health_data(data, DataType.VITAL_SIGNS, user_id, source)


async def process_lab_results(
    data: Dict[str, Any], 
    user_id: str, 
    source: str = "lab"
) -> PipelineResult:
    """处理检验结果数据"""
    pipeline = get_health_data_pipeline()
    return await pipeline.process_health_data(data, DataType.LAB_RESULTS, user_id, source)


async def process_wearable_data(
    data: Dict[str, Any], 
    user_id: str, 
    source: str = "wearable"
) -> PipelineResult:
    """处理可穿戴设备数据"""
    pipeline = get_health_data_pipeline()
    return await pipeline.process_health_data(data, DataType.WEARABLE_DATA, user_id, source)


# 中医五诊数据处理便捷函数
async def process_tcm_look_data(
    data: Dict[str, Any], 
    user_id: str, 
    source: str = "tcm_clinic"
) -> PipelineResult:
    """处理中医望诊数据"""
    pipeline = get_health_data_pipeline()
    return await pipeline.process_health_data(data, DataType.TCM_LOOK, user_id, source)


async def process_tcm_listen_data(
    data: Dict[str, Any], 
    user_id: str, 
    source: str = "tcm_clinic"
) -> PipelineResult:
    """处理中医闻诊数据"""
    pipeline = get_health_data_pipeline()
    return await pipeline.process_health_data(data, DataType.TCM_LISTEN, user_id, source)


async def process_tcm_inquiry_data(
    data: Dict[str, Any], 
    user_id: str, 
    source: str = "tcm_clinic"
) -> PipelineResult:
    """处理中医问诊数据"""
    pipeline = get_health_data_pipeline()
    return await pipeline.process_health_data(data, DataType.TCM_INQUIRY, user_id, source)


async def process_tcm_palpation_data(
    data: Dict[str, Any], 
    user_id: str, 
    source: str = "tcm_clinic"
) -> PipelineResult:
    """处理中医切诊数据"""
    pipeline = get_health_data_pipeline()
    return await pipeline.process_health_data(data, DataType.TCM_PALPATION, user_id, source)


async def process_tcm_calculation_data(
    data: Dict[str, Any], 
    user_id: str, 
    source: str = "tcm_calculation"
) -> PipelineResult:
    """处理中医算诊数据"""
    pipeline = get_health_data_pipeline()
    return await pipeline.process_health_data(data, DataType.TCM_CALCULATION, user_id, source) 