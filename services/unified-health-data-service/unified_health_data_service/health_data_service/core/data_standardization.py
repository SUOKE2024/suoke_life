"""
data_standardization - 索克生活项目模块
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
import json
import logging

#! / usr / bin / env python3
"""
健康数据标准化处理模块

提供健康数据的标准化、验证、转换和质量控制功能。
支持多种健康数据格式，包括生理指标、检验报告、影像数据等。
"""


logger = logging.getLogger(__name__)

class DataType(Enum):
"""数据类型枚举"""
    VITAL_SIGNS = "vital_signs"  # 生命体征
    LAB_RESULTS = "lab_results"  # 检验结果
    MEDICAL_IMAGING = "medical_imaging"  # 医学影像
    MEDICATION = "medication"  # 用药信息
    SYMPTOMS = "symptoms"  # 症状
    DIAGNOSIS = "diagnosis"  # 诊断
    LIFESTYLE = "lifestyle"  # 生活方式
    WEARABLE_DATA = "wearable_data"  # 可穿戴设备数据

    # 中医五诊数据类型
    TCM_LOOK = "tcm_look"  # 望诊数据（面诊、舌诊、体态等）
    TCM_LISTEN = "tcm_listen"  # 闻诊数据（语音、呼吸音、心音等）
    TCM_INQUIRY = "tcm_inquiry"  # 问诊数据（症状、病史、体质等）
    TCM_PALPATION = "tcm_palpation"  # 切诊数据（脉象、触诊等）
    TCM_CALCULATION = "tcm_calculation"  # 算诊数据（子午流注、八字体质等）

class DataQuality(Enum):
"""数据质量等级"""
    HIGH = "high"  # 高质量
    MEDIUM = "medium"  # 中等质量
    LOW = "low"  # 低质量
    INVALID = "invalid"  # 无效数据

@dataclass
class ValidationRule:
"""验证规则"""
    field_name: str
    rule_type: str  # range, regex, enum, required, etc.
    parameters: dict[str, Any]
    error_message: str
    severity: str = "error"  # error, warning, info

@dataclass
class StandardizedData:
"""标准化数据"""
    original_data: dict[str, Any]
    standardized_data: dict[str, Any]
    data_type: DataType
    quality_score: float
    quality_level: DataQuality
    validation_errors: list[str] = field(default_factory = list)
    validation_warnings: list[str] = field(default_factory = list)
    metadata: dict[str, Any] = field(default_factory = dict)
    timestamp: str = field(default_factory = lambda: datetime.now().isoformat())

@dataclass
class HealthDataSchema:
"""健康数据模式"""
    schema_id: str
    data_type: DataType
    version: str
    fields: dict[str, dict[str, Any]]
    validation_rules: list[ValidationRule]
    transformation_rules: dict[str, str]
    description: str

class HealthDataStandardizer:
"""健康数据标准化器"""

    def __init__(self) -> None:
    """初始化标准化器"""
self.schemas = self._initialize_schemas()
self.unit_conversions = self._initialize_unit_conversions()
self.reference_ranges = self._initialize_reference_ranges()

    def _initialize_schemas(self) -> dict[str, HealthDataSchema]:
    """初始化数据模式"""
schemas = {}

# 生命体征模式
schemas["vital_signs"] = HealthDataSchema(
schema_id = "vital_signs_v1.0",
data_type = DataType.VITAL_SIGNS,
version = "1.0",
fields = {
"systolic_bp": {
"type": "integer",
"unit": "mmHg",
"range": [70, 250],
"required": True
},
"diastolic_bp": {
"type": "integer",
"unit": "mmHg",
"range": [40, 150],
"required": True
},
"heart_rate": {
"type": "integer",
"unit": "bpm",
"range": [30, 220],
"required": True
},
"temperature": {
"type": "float",
"unit": "celsius",
"range": [30.0, 45.0],
"required": False
},
"respiratory_rate": {
"type": "integer",
"unit": "breaths / min",
"range": [8, 60],
"required": False
},
"oxygen_saturation": {
"type": "float",
"unit": "percentage",
"range": [70.0, 100.0],
"required": False
}
},
validation_rules = [
ValidationRule(
field_name = "systolic_bp",
rule_type = "range",
parameters = {"min": 70, "max": 250},
error_message = "收缩压必须在70 - 250 mmHg范围内"
),
ValidationRule(
field_name = "diastolic_bp",
rule_type = "range",
parameters = {"min": 40, "max": 150},
error_message = "舒张压必须在40 - 150 mmHg范围内"
),
ValidationRule(
field_name = "blood_pressure_logic",
rule_type = "custom",
parameters = {"function": "validate_bp_logic"},
error_message = "收缩压必须大于舒张压"
)
],
transformation_rules = {
"temperature_fahrenheit": "celsius_to_fahrenheit",
"normalize_units": "standardize_units"
},
description = "生命体征数据标准化模式"
)

# 检验结果模式
schemas["lab_results"] = HealthDataSchema(
schema_id = "lab_results_v1.0",
data_type = DataType.LAB_RESULTS,
version = "1.0",
fields = {
"glucose": {
"type": "float",
"unit": "mg / dL",
"range": [30.0, 600.0],
"required": False
},
"cholesterol_total": {
"type": "float",
"unit": "mg / dL",
"range": [100.0, 500.0],
"required": False
},
"hdl_cholesterol": {
"type": "float",
"unit": "mg / dL",
"range": [20.0, 100.0],
"required": False
},
"ldl_cholesterol": {
"type": "float",
"unit": "mg / dL",
"range": [50.0, 300.0],
"required": False
},
"triglycerides": {
"type": "float",
"unit": "mg / dL",
"range": [30.0, 1000.0],
"required": False
},
"hemoglobin": {
"type": "float",
"unit": "g / dL",
"range": [8.0, 20.0],
"required": False
}
},
validation_rules = [
ValidationRule(
field_name = "glucose",
rule_type = "range",
parameters = {"min": 30.0, "max": 600.0},
error_message = "血糖值必须在30 - 600 mg / dL范围内"
)
],
transformation_rules = {
"glucose_mmol": "mg_dl_to_mmol_l_glucose",
"cholesterol_mmol": "mg_dl_to_mmol_l_cholesterol"
},
description = "检验结果数据标准化模式"
)

# 可穿戴设备数据模式
schemas["wearable_data"] = HealthDataSchema(
schema_id = "wearable_data_v1.0",
data_type = DataType.WEARABLE_DATA,
version = "1.0",
fields = {
"steps": {
"type": "integer",
"unit": "count",
"range": [0, 100000],
"required": False
},
"distance": {
"type": "float",
"unit": "km",
"range": [0.0, 200.0],
"required": False
},
"calories_burned": {
"type": "integer",
"unit": "kcal",
"range": [0, 10000],
"required": False
},
"sleep_duration": {
"type": "float",
"unit": "hours",
"range": [0.0, 24.0],
"required": False
},
"sleep_quality": {
"type": "float",
"unit": "score",
"range": [0.0, 100.0],
"required": False
}
},
validation_rules = [
ValidationRule(
field_name = "steps",
rule_type = "range",
parameters = {"min": 0, "max": 100000},
error_message = "步数必须在0 - 100000范围内"
)
],
transformation_rules = {
"distance_miles": "km_to_miles",
"normalize_activity": "standardize_activity_data"
},
description = "可穿戴设备数据标准化模式"
)

# 中医望诊数据模式
schemas["tcm_look"] = HealthDataSchema(
schema_id = "tcm_look_v1.0",
data_type = DataType.TCM_LOOK,
version = "1.0",
fields = {
# 面诊数据
"face_color": {
"type": "string",
"enum": ["红润", "苍白", "萎黄", "青黑", "潮红"],
"required": False
},
"face_luster": {
"type": "string",
"enum": ["有神", "少神", "失神", "假神"],
"required": False
},
"facial_expression": {
"type": "string",
"enum": ["安静", "烦躁", "痛苦", "淡漠"],
"required": False
},
# 舌诊数据
"tongue_color": {
"type": "string",
"enum": ["淡红", "淡白", "红", "绛", "紫"],
"required": False
},
"tongue_coating": {
"type": "string",
"enum": ["薄白", "厚白", "薄黄", "厚黄", "无苔"],
"required": False
},
"tongue_texture": {
"type": "string",
"enum": ["正常", "胖大", "瘦薄", "裂纹", "齿痕"],
"required": False
},
# 体态数据
"body_posture": {
"type": "string",
"enum": ["端正", "佝偻", "强直", "蜷卧"],
"required": False
},
"gait": {
"type": "string",
"enum": ["正常", "蹒跚", "急促", "缓慢"],
"required": False
}
},
validation_rules = [
ValidationRule(
field_name = "tongue_color",
rule_type = "enum",
parameters = {"values": ["淡红", "淡白", "红", "绛", "紫"]},
error_message = "舌色必须是有效的中医术语"
)
],
transformation_rules = {
"normalize_tcm_terms": "standardize_tcm_terminology"
},
description = "中医望诊数据标准化模式"
)

# 中医闻诊数据模式
schemas["tcm_listen"] = HealthDataSchema(
schema_id = "tcm_listen_v1.0",
data_type = DataType.TCM_LISTEN,
version = "1.0",
fields = {
# 语音特征
"voice_strength": {
"type": "string",
"enum": ["洪亮", "低微", "嘶哑", "失音"],
"required": False
},
"speech_speed": {
"type": "string",
"enum": ["正常", "急促", "缓慢", "断续"],
"required": False
},
# 呼吸音
"breathing_sound": {
"type": "string",
"enum": ["平和", "粗糙", "微弱", "喘促"],
"required": False
},
"cough_sound": {
"type": "string",
"enum": ["无", "干咳", "湿咳", "顿咳"],
"required": False
},
# 心音特征
"heart_sound_rhythm": {
"type": "string",
"enum": ["规律", "不规律", "间歇", "奔马律"],
"required": False
},
"heart_sound_intensity": {
"type": "string",
"enum": ["正常", "增强", "减弱", "杂音"],
"required": False
}
},
validation_rules = [
ValidationRule(
field_name = "voice_strength",
rule_type = "enum",
parameters = {"values": ["洪亮", "低微", "嘶哑", "失音"]},
error_message = "语音强度必须是有效的中医术语"
)
],
transformation_rules = {
"normalize_audio_features": "standardize_audio_analysis"
},
description = "中医闻诊数据标准化模式"
)

# 中医问诊数据模式
schemas["tcm_inquiry"] = HealthDataSchema(
schema_id = "tcm_inquiry_v1.0",
data_type = DataType.TCM_INQUIRY,
version = "1.0",
fields = {
# 主诉症状
"chief_complaint": {
"type": "string",
"required": True
},
"symptom_duration": {
"type": "string",
"enum": ["急性", "亚急性", "慢性"],
"required": False
},
# 寒热症状
"cold_heat": {
"type": "string",
"enum": ["恶寒", "恶热", "寒热往来", "无明显寒热"],
"required": False
},
# 汗出情况
"sweating": {
"type": "string",
"enum": ["无汗", "自汗", "盗汗", "大汗"],
"required": False
},
# 饮食情况
"appetite": {
"type": "string",
"enum": ["正常", "食欲不振", "食欲亢进", "厌食"],
"required": False
},
# 睡眠情况
"sleep_quality": {
"type": "string",
"enum": ["正常", "失眠", "多梦", "嗜睡"],
"required": False
},
# 二便情况
"urination": {
"type": "string",
"enum": ["正常", "尿频", "尿急", "尿痛", "尿少"],
"required": False
},
"defecation": {
"type": "string",
"enum": ["正常", "便秘", "腹泻", "便溏"],
"required": False
}
},
validation_rules = [
ValidationRule(
field_name = "chief_complaint",
rule_type = "required",
parameters = {},
error_message = "主诉症状为必填项"
)
],
transformation_rules = {
"extract_symptoms": "extract_tcm_symptoms",
"classify_syndrome": "classify_tcm_syndrome"
},
description = "中医问诊数据标准化模式"
)

# 中医切诊数据模式
schemas["tcm_palpation"] = HealthDataSchema(
schema_id = "tcm_palpation_v1.0",
data_type = DataType.TCM_PALPATION,
version = "1.0",
fields = {
# 脉象特征
"pulse_position": {
"type": "string",
"enum": ["浮", "中", "沉"],
"required": False
},
"pulse_rate": {
"type": "string",
"enum": ["迟", "缓", "平", "数", "疾"],
"required": False
},
"pulse_rhythm": {
"type": "string",
"enum": ["规律", "不规律", "间歇", "促", "结", "代"],
"required": False
},
"pulse_strength": {
"type": "string",
"enum": ["有力", "无力", "洪", "细", "微"],
"required": False
},
"pulse_shape": {
"type": "string",
"enum": ["滑", "涩", "弦", "紧", "缓", "濡", "弱"],
"required": False
},
# 触诊数据
"skin_temperature": {
"type": "string",
"enum": ["正常", "发热", "发凉", "局部发热"],
"required": False
},
"skin_moisture": {
"type": "string",
"enum": ["正常", "干燥", "湿润", "出汗"],
"required": False
},
"skin_elasticity": {
"type": "string",
"enum": ["正常", "弹性差", "水肿", "硬化"],
"required": False
},
# 腹诊
"abdominal_tension": {
"type": "string",
"enum": ["正常", "胀满", "柔软", "硬满"],
"required": False
},
"abdominal_pain": {
"type": "string",
"enum": ["无", "轻度", "中度", "重度"],
"required": False
}
},
validation_rules = [
ValidationRule(
field_name = "pulse_position",
rule_type = "enum",
parameters = {"values": ["浮", "中", "沉"]},
error_message = "脉位必须是有效的中医术语"
)
],
transformation_rules = {
"analyze_pulse": "analyze_pulse_pattern",
"classify_constitution": "classify_body_constitution"
},
description = "中医切诊数据标准化模式"
)

# 中医算诊数据模式
schemas["tcm_calculation"] = HealthDataSchema(
schema_id = "tcm_calculation_v1.0",
data_type = DataType.TCM_CALCULATION,
version = "1.0",
fields = {
# 基础信息
"birth_year": {
"type": "integer",
"range": [1900, 2100],
"required": True
},
"birth_month": {
"type": "integer",
"range": [1, 12],
"required": True
},
"birth_day": {
"type": "integer",
"range": [1, 31],
"required": True
},
"birth_hour": {
"type": "integer",
"range": [0, 23],
"required": True
},
"gender": {
"type": "string",
"enum": ["男", "女"],
"required": True
},
# 子午流注分析结果
"current_meridian": {
"type": "string",
"enum": ["肺经", "大肠经", "胃经", "脾经", "心经", "小肠经",
"膀胱经", "肾经", "心包经", "三焦经", "胆经", "肝经"],
"required": False
},
"optimal_treatment_time": {
"type": "string",
"required": False
},
# 八字体质分析
"constitution_type": {
"type": "string",
"enum": ["平和质", "气虚质", "阳虚质", "阴虚质", "痰湿质",
"湿热质", "血瘀质", "气郁质", "特禀质"],
"required": False
},
"five_elements_score": {
"type": "object",
"properties": {
"wood": {"type": "float", "range": [0.0, 100.0]},
"fire": {"type": "float", "range": [0.0, 100.0]},
"earth": {"type": "float", "range": [0.0, 100.0]},
"metal": {"type": "float", "range": [0.0, 100.0]},
"water": {"type": "float", "range": [0.0, 100.0]}
},
"required": False
},
# 八卦配属
"life_hexagram": {
"type": "string",
"enum": ["乾", "坤", "震", "巽", "坎", "离", "艮", "兑"],
"required": False
},
"health_direction": {
"type": "string",
"enum": ["东", "南", "西", "北", "东南", "西南", "西北", "东北"],
"required": False
},
# 五运六气
"annual_qi": {
"type": "string",
"required": False
},
"seasonal_qi": {
"type": "string",
"required": False
},
"health_risk_level": {
"type": "string",
"enum": ["低", "中", "高"],
"required": False
}
},
validation_rules = [
ValidationRule(
field_name = "birth_year",
rule_type = "range",
parameters = {"min": 1900, "max": 2100},
error_message = "出生年份必须在1900 - 2100范围内"
),
ValidationRule(
field_name = "gender",
rule_type = "required",
parameters = {},
error_message = "性别为必填项"
)
],
transformation_rules = {
"calculate_ziwu": "calculate_meridian_flow",
"analyze_constitution": "analyze_eight_character_constitution",
"calculate_bagua": "calculate_bagua_attribution",
"analyze_wuyun": "analyze_five_movements_six_qi"
},
description = "中医算诊数据标准化模式"
)

return schemas

    def _initialize_unit_conversions(self) -> dict[str, callable]:
    """初始化单位转换函数"""
return {
"celsius_to_fahrenheit": lambda c: c * 9 / 5 + 32,
"fahrenheit_to_celsius": lambda f: (f - 32) * 5 / 9,
"kg_to_lbs": lambda kg: kg * 2.20462,
"lbs_to_kg": lambda lbs: lbs / 2.20462,
"cm_to_inches": lambda cm: cm / 2.54,
"inches_to_cm": lambda inches: inches * 2.54,
"mg_dl_to_mmol_l_glucose": lambda mg_dl: mg_dl / 18.0,
"mmol_l_to_mg_dl_glucose": lambda mmol_l: mmol_l * 18.0,
"mg_dl_to_mmol_l_cholesterol": lambda mg_dl: mg_dl / 38.67,
"mmol_l_to_mg_dl_cholesterol": lambda mmol_l: mmol_l * 38.67,
"km_to_miles": lambda km: km * 0.621371,
"miles_to_km": lambda miles: miles / 0.621371
}

    def _initialize_reference_ranges(self) -> dict[str, dict[str, Any]]:
    """初始化参考范围"""
return {
"blood_pressure": {
"normal": {"systolic": [90, 120], "diastolic": [60, 80]},
"elevated": {"systolic": [120, 129], "diastolic": [60, 80]},
"high_stage1": {"systolic": [130, 139], "diastolic": [80, 89]},
"high_stage2": {"systolic": [140, 180], "diastolic": [90, 120]},
"crisis": {"systolic": [180, 250], "diastolic": [120, 150]}
},
"glucose": {
"normal_fasting": [70, 100],
"prediabetes_fasting": [100, 125],
"diabetes_fasting": [126, 600],
"normal_random": [70, 140],
"diabetes_random": [200, 600]
},
"cholesterol": {
"total_desirable": [0, 200],
"total_borderline": [200, 239],
"total_high": [240, 500],
"hdl_low": [0, 40],
"hdl_normal": [40, 60],
"hdl_high": [60, 100],
"ldl_optimal": [0, 100],
"ldl_near_optimal": [100, 129],
"ldl_borderline": [130, 159],
"ldl_high": [160, 189],
"ldl_very_high": [190, 300]
}
}

    def standardize_data(
self,
raw_data: dict[str, Any],
data_type: DataType,
source_format: Optional[str] = None
    ) -> StandardizedData:
    """
标准化健康数据

Args:
    raw_data: 原始数据
data_type: 数据类型
source_format: 源数据格式

Returns:
    StandardizedData: 标准化后的数据
"""
logger.info(f"开始标准化 {data_type.value} 数据")

# 获取对应的模式
schema_key = data_type.value
if schema_key not in self.schemas:
    raise ValueError(f"不支持的数据类型: {data_type}")

schema = self.schemas[schema_key]

# 数据预处理
preprocessed_data = self._preprocess_data(raw_data, schema)

# 数据验证
validation_errors, validation_warnings = self._validate_data(preprocessed_data, schema)

# 数据转换
standardized_data = self._transform_data(preprocessed_data, schema)

# 计算质量分数
quality_score, quality_level = self._calculate_quality_score(
standardized_data, validation_errors, validation_warnings
)

# 添加元数据
metadata = self._generate_metadata(raw_data, schema, source_format)

return StandardizedData(
original_data = raw_data,
standardized_data = standardized_data,
data_type = data_type,
quality_score = quality_score,
quality_level = quality_level,
validation_errors = validation_errors,
validation_warnings = validation_warnings,
metadata = metadata
)

    def _preprocess_data(self, data: dict[str, Any], schema: HealthDataSchema) -> dict[str, Any]:
    """数据预处理"""
processed_data = {}

for field_name, field_config in schema.fields.items():
    if field_name in data:
    value = data[field_name]

# 类型转换
try:
    if field_config["type"]=="integer":
    processed_data[field_name] = int(float(value))
elif field_config["type"]=="float":
    processed_data[field_name] = float(value)
elif field_config["type"]=="string":
    processed_data[field_name] = str(value)
else:
    processed_data[field_name] = value
except (ValueError, TypeError):
    logger.warning(f"无法转换字段 {field_name} 的值: {value}")
processed_data[field_name] = value

return processed_data

    def _validate_data(
self,
data: dict[str, Any],
schema: HealthDataSchema
    ) -> Tuple[list[str], list[str]]:
    """数据验证"""
errors = []
warnings = []

# 字段验证
for field_name, field_config in schema.fields.items():
    if field_config.get("required", False) and field_name not in data:
    errors.append(f"必填字段 {field_name} 缺失")
continue

if field_name in data:
    value = data[field_name]

# 范围验证
if "range" in field_config:
    min_val, max_val = field_config["range"]
if not (min_val <=value <=max_val):
    errors.append(f"字段 {field_name} 值 {value} 超出范围 [{min_val}, {max_val}]")

# 规则验证
for rule in schema.validation_rules:
    if rule.rule_type=="range":
    field_name = rule.field_name
if field_name in data:
    value = data[field_name]
min_val = rule.parameters.get("min")
max_val = rule.parameters.get("max")

if min_val is not None and value < min_val:
    errors.append(f"{rule.error_message}: 值 {value} 小于最小值 {min_val}")
if max_val is not None and value > max_val:
    errors.append(f"{rule.error_message}: 值 {value} 大于最大值 {max_val}")

elif rule.rule_type=="custom":
    if rule.field_name=="blood_pressure_logic":
    if "systolic_bp" in data and "diastolic_bp" in data:
    if data["systolic_bp"] <=data["diastolic_bp"]:
    errors.append(rule.error_message)

return errors, warnings

    def _transform_data(self, data: dict[str, Any], schema: HealthDataSchema) -> dict[str, Any]:
    """数据转换"""
transformed_data = data.copy()

# 应用转换规则
for rule_name, function_name in schema.transformation_rules.items():
    if function_name in self.unit_conversions:
    # 单位转换
if rule_name=="temperature_fahrenheit" and "temperature" in data:
    transformed_data["temperature_fahrenheit"] = self.unit_conversions[function_name](
data["temperature"]
)
elif rule_name=="glucose_mmol" and "glucose" in data:
    transformed_data["glucose_mmol"] = self.unit_conversions[function_name](
data["glucose"]
)
elif rule_name=="distance_miles" and "distance" in data:
    transformed_data["distance_miles"] = self.unit_conversions[function_name](
data["distance"]
)

# 添加计算字段
if schema.data_type==DataType.VITAL_SIGNS:
    if "systolic_bp" in data and "diastolic_bp" in data:
    # 计算平均动脉压
map_pressure = (data["systolic_bp"] + 2 * data["diastolic_bp"]) / 3
transformed_data["mean_arterial_pressure"] = round(map_pressure, 1)

# 血压分类
transformed_data["bp_category"] = self._classify_blood_pressure(
data["systolic_bp"], data["diastolic_bp"]
)

elif schema.data_type==DataType.LAB_RESULTS:
    if "glucose" in data:
    transformed_data["glucose_category"] = self._classify_glucose(data["glucose"])

if all(k in data for k in ["cholesterol_total", "hdl_cholesterol", "ldl_cholesterol"]):
    # 计算胆固醇比值
if data["hdl_cholesterol"] > 0:
    transformed_data["cholesterol_ratio"] = round(
data["cholesterol_total"] / data["hdl_cholesterol"], 2
)

return transformed_data

    def _calculate_quality_score(
self,
data: dict[str, Any],
errors: list[str],
warnings: list[str]
    ) -> Tuple[float, DataQuality]:
    """计算数据质量分数"""
base_score = 100.0

# 错误扣分
error_penalty = len(errors) * 20
warning_penalty = len(warnings) * 5

# 完整性评分
completeness_score = len(data) * 2  # 每个字段加2分

# 计算最终分数
final_score = max(0, base_score - error_penalty - warning_penalty + completeness_score)
final_score = min(100, final_score)  # 最高100分

# 确定质量等级
if final_score >=90:
    quality_level = DataQuality.HIGH
elif final_score >=70:
    quality_level = DataQuality.MEDIUM
elif final_score >=50:
    quality_level = DataQuality.LOW
else:
    quality_level = DataQuality.INVALID

return final_score, quality_level

    def _generate_metadata(
self,
raw_data: dict[str, Any],
schema: HealthDataSchema,
source_format: Optional[str]
    ) -> dict[str, Any]:
    """生成元数据"""
return {
"schema_id": schema.schema_id,
"schema_version": schema.version,
"source_format": source_format,
"processing_timestamp": datetime.now().isoformat(),
"field_count": len(raw_data),
"standardized_field_count": len(schema.fields),
"data_size_bytes": len(json.dumps(raw_data).encode('utf - 8'))
}

    def _classify_blood_pressure(self, systolic: int, diastolic: int) -> str:
    """血压分类"""
ranges = self.reference_ranges["blood_pressure"]

for category, values in ranges.items():
    sys_range = values["systolic"]
dia_range = values["diastolic"]

if (sys_range[0] <=systolic <=sys_range[1] and
dia_range[0] <=diastolic <=dia_range[1]):
    return category

return "unknown"

    def _classify_glucose(self, glucose: float) -> str:
    """血糖分类"""
ranges = self.reference_ranges["glucose"]

# 假设是空腹血糖
if ranges["normal_fasting"][0] <=glucose <=ranges["normal_fasting"][1]:
    return "normal_fasting"
elif ranges["prediabetes_fasting"][0] <=glucose <=ranges["prediabetes_fasting"][1]:
    return "prediabetes_fasting"
elif glucose >=ranges["diabetes_fasting"][0]:
    return "diabetes_fasting"
else:
    return "unknown"

    def batch_standardize(
self,
data_list: list[dict[str, Any]],
data_type: DataType,
source_format: Optional[str] = None
    ) -> list[StandardizedData]:
    """批量标准化数据"""
results = []

for i, data in enumerate(data_list):
    try:
    result = self.standardize_data(data, data_type, source_format)
results.append(result)
except Exception as e:
    logger.error(f"标准化第 {i + 1} 条数据时发生错误: {e}")
# 创建错误结果
error_result = StandardizedData(
original_data = data,
standardized_data = {},
data_type = data_type,
quality_score = 0.0,
quality_level = DataQuality.INVALID,
validation_errors = [f"标准化失败: {str(e)}"],
validation_warnings = [],
metadata = {"error": True, "error_message": str(e)}
)
results.append(error_result)

return results

    def get_schema_info(self, data_type: DataType) -> dict[str, Any]:
    """获取数据模式信息"""
schema_key = data_type.value
if schema_key not in self.schemas:
    raise ValueError(f"不支持的数据类型: {data_type}")

schema = self.schemas[schema_key]
return {
"schema_id": schema.schema_id,
"version": schema.version,
"description": schema.description,
"fields": schema.fields,
"validation_rules": [
{
"field": rule.field_name,
"type": rule.rule_type,
"message": rule.error_message
}
for rule in schema.validation_rules
]
}

# 全局标准化器实例
_standardizer = None

def get_standardizer() -> HealthDataStandardizer:
"""获取健康数据标准化器实例"""
    global _standardizer
    if _standardizer is None:
    _standardizer = HealthDataStandardizer()
    return _standardizer

# 便捷函数
def standardize_vital_signs(data: dict[str, Any]) -> StandardizedData:
"""标准化生命体征数据"""
    return get_standardizer().standardize_data(data, DataType.VITAL_SIGNS)

def standardize_lab_results(data: dict[str, Any]) -> StandardizedData:
"""标准化检验结果数据"""
    return get_standardizer().standardize_data(data, DataType.LAB_RESULTS)

def standardize_wearable_data(data: dict[str, Any]) -> StandardizedData:
"""标准化可穿戴设备数据"""
    return get_standardizer().standardize_data(data, DataType.WEARABLE_DATA)

# 中医五诊数据标准化便捷函数
def standardize_tcm_look_data(data: dict[str, Any]) -> StandardizedData:
"""标准化中医望诊数据"""
    return get_standardizer().standardize_data(data, DataType.TCM_LOOK)

def standardize_tcm_listen_data(data: dict[str, Any]) -> StandardizedData:
"""标准化中医闻诊数据"""
    return get_standardizer().standardize_data(data, DataType.TCM_LISTEN)

def standardize_tcm_inquiry_data(data: dict[str, Any]) -> StandardizedData:
"""标准化中医问诊数据"""
    return get_standardizer().standardize_data(data, DataType.TCM_INQUIRY)

def standardize_tcm_palpation_data(data: dict[str, Any]) -> StandardizedData:
"""标准化中医切诊数据"""
    return get_standardizer().standardize_data(data, DataType.TCM_PALPATION)

def standardize_tcm_calculation_data(data: dict[str, Any]) -> StandardizedData:
"""标准化中医算诊数据"""
    return get_standardizer().standardize_data(data, DataType.TCM_CALCULATION)
