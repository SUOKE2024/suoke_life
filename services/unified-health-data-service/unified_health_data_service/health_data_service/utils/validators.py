"""
健康数据验证器
提供各种健康数据的验证功能
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class HealthDataValidator:
    """健康数据验证器"""

    def __init__(self):
        """初始化验证器"""
        self.vital_signs_ranges = {
            "heart_rate": (30, 200),
            "blood_pressure_systolic": (70, 250),
            "blood_pressure_diastolic": (40, 150),
            "temperature": (35.0, 42.0),
            "oxygen_saturation": (70, 100),
        }

    async def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证健康数据"""
        try:
            # 基本验证
            self._validate_basic_fields(data)

            # 根据数据类型进行特定验证
            data_type = data.get("data_type")

            if data_type == "vital_signs":
                self._validate_vital_signs(data)
            elif data_type == "diagnostic":
                self._validate_diagnostic_data(data)
            elif data_type == "tcm":
                self._validate_tcm_data(data)

            # 添加验证时间戳
            data["validated_at"] = datetime.utcnow()

            return data

        except Exception as e:
            logger.error(f"数据验证失败: {e}")
            raise

    def _validate_basic_fields(self, data: Dict[str, Any]) -> None:
        """验证基本字段"""
        # 必需字段检查
        required_fields = ["user_id", "data_type"]
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"缺少必需字段: {field}")

        # 用户ID格式验证
        user_id = data["user_id"]
        if not isinstance(user_id, str) or len(user_id) < 1:
            raise ValueError("用户ID格式无效")

        # 数据类型验证
        valid_data_types = ["vital_signs", "diagnostic", "tcm", "general"]
        if data["data_type"] not in valid_data_types:
            raise ValueError(f"无效的数据类型: {data['data_type']}")

    def _validate_vital_signs(self, data: Dict[str, Any]) -> None:
        """验证生命体征数据"""
        # 检查数值范围
        for field, (min_val, max_val) in self.vital_signs_ranges.items():
            if field in data:
                value = data[field]
                if value is not None:
                    try:
                        value = float(value)
                        if not (min_val <= value <= max_val):
                            raise ValueError(
                                f"{field} 值 {value} 超出正常范围 [{min_val}, {max_val}]"
                            )
                        data[field] = value  # 确保是数值类型
                    except (ValueError, TypeError):
                        raise ValueError(f"{field} 必须是有效的数值")

        # 血压逻辑验证
        if "blood_pressure_systolic" in data and "blood_pressure_diastolic" in data:
            sys_bp = data["blood_pressure_systolic"]
            dia_bp = data["blood_pressure_diastolic"]
            if sys_bp is not None and dia_bp is not None:
                if sys_bp <= dia_bp:
                    raise ValueError("收缩压必须大于舒张压")

    def _validate_diagnostic_data(self, data: Dict[str, Any]) -> None:
        """验证诊断数据"""
        # 必需字段
        required_fields = ["diagnosis_type", "diagnosis_result"]
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"诊断数据缺少必需字段: {field}")

        # 置信度验证
        if "confidence_score" in data:
            confidence = data["confidence_score"]
            if confidence is not None:
                try:
                    confidence = float(confidence)
                    if not (0.0 <= confidence <= 1.0):
                        raise ValueError("置信度必须在0.0到1.0之间")
                    data["confidence_score"] = confidence
                except (ValueError, TypeError):
                    raise ValueError("置信度必须是有效的数值")

    def _validate_tcm_data(self, data: Dict[str, Any]) -> None:
        """验证中医数据"""
        # 诊断方法验证
        if "diagnosis_method" in data:
            valid_methods = ["望", "闻", "问", "切", "综合"]
            if data["diagnosis_method"] not in valid_methods:
                raise ValueError(f"无效的中医诊断方法: {data['diagnosis_method']}")

        # 症状列表验证
        if "symptoms" in data:
            symptoms = data["symptoms"]
            if not isinstance(symptoms, list):
                raise ValueError("症状必须是列表格式")

            for symptom in symptoms:
                if not isinstance(symptom, str) or len(symptom.strip()) == 0:
                    raise ValueError("症状描述必须是非空字符串")

    def validate_user_id(self, user_id: str) -> bool:
        """验证用户ID格式"""
        if not isinstance(user_id, str):
            return False

        # 简单的用户ID格式验证（可根据实际需求调整）
        pattern = r"^[a-zA-Z0-9_-]+$"
        return bool(re.match(pattern, user_id)) and len(user_id) >= 3

    def validate_timestamp(self, timestamp: Any) -> datetime:
        """验证时间戳"""
        if isinstance(timestamp, datetime):
            return timestamp

        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("时间戳格式无效")

        if isinstance(timestamp, (int, float)):
            try:
                return datetime.fromtimestamp(timestamp)
            except (ValueError, OSError):
                raise ValueError("时间戳值无效")

        raise ValueError("时间戳类型无效")

    def get_validation_rules(self) -> Dict[str, Any]:
        """获取验证规则"""
        return {
            "vital_signs_ranges": self.vital_signs_ranges,
            "valid_data_types": ["vital_signs", "diagnostic", "tcm", "general"],
            "tcm_diagnosis_methods": ["望", "闻", "问", "切", "综合"],
            "required_fields": {
                "basic": ["user_id", "data_type"],
                "vital_signs": [],
                "diagnostic": ["diagnosis_type", "diagnosis_result"],
                "tcm": ["diagnosis_method"],
            },
        }
