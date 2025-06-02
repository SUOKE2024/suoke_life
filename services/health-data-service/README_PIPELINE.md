# 健康数据流水线使用指南

## 概述

健康数据流水线是索克生活平台的核心组件，负责处理、标准化和保护用户的健康数据。该流水线集成了数据验证、标准化、隐私保护（零知识证明）和区块链存储等功能，为平台提供了完整的健康数据管理解决方案。

### 核心特性

- **多数据类型支持**：支持生命体征、检验结果、可穿戴设备数据以及中医五诊数据
- **中医五诊集成**：完整支持望、闻、问、切、算五种中医诊断数据类型
- **数据标准化**：自动转换和标准化不同来源的健康数据
- **隐私保护**：使用零知识证明技术保护敏感健康信息
- **质量评估**：对数据质量进行自动评分和验证
- **区块链存储**：将数据证明存储在区块链上，确保数据不可篡改
- **异步处理**：支持高并发的数据处理需求
- **批量处理**：支持大量数据的批量处理和分析

## 核心功能

### 1. 数据标准化
- **多格式支持**: 支持生命体征、检验结果、可穿戴设备数据等多种格式
- **自动验证**: 内置数据验证规则，确保数据质量
- **单位转换**: 自动进行单位转换和标准化
- **质量评分**: 为每个数据集提供质量分数和等级

### 2. 零知识验证
- **隐私保护**: 使用zk-SNARKs技术保护敏感健康数据
- **范围证明**: 验证健康指标在正常范围内，无需暴露具体数值
- **完整性验证**: 确保数据未被篡改
- **可验证性**: 第三方可验证数据有效性而无需访问原始数据

### 3. 区块链存储
- **不可篡改**: 将零知识证明存储在区块链上
- **访问控制**: 细粒度的数据访问权限管理
- **审计追踪**: 完整的数据访问和验证记录

## 快速开始

### 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 可选：安装零知识证明库
pip install py_ecc
```

### 基本使用

```python
import asyncio
from health_data_service.services.health_data_pipeline import (
    HealthDataPipeline,
    DataType,
    PipelineConfig
)

# 创建流水线实例
pipeline = HealthDataPipeline()

# 处理生命体征数据
async def process_vital_signs():
    data = {
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "heart_rate": 72,
        "temperature": 36.5
    }
    
    result = await pipeline.process_health_data(
        data=data,
        data_type=DataType.VITAL_SIGNS,
        user_id="user_001",
        source="manual_input"
    )
    
    print(f"处理状态: {result.status}")
    print(f"数据质量: {result.standardized_data.quality_score}")
    print(f"隐私证明: {result.privacy_proof.data_hash}")

# 处理可穿戴设备数据
async def process_wearable_data(data, user_id, source):
    result = await pipeline.process_health_data(
        data=data,
        data_type=DataType.WEARABLE_DATA,
        user_id=user_id,
        source=source
    )
    print(f"处理状态: {result.status}")
    print(f"数据质量: {result.standardized_data.quality_score}")
    print(f"隐私证明: {result.privacy_proof.data_hash}")

# 运行示例
asyncio.run(process_vital_signs())
```

## 支持的数据类型

### 1. 生命体征 (VITAL_SIGNS)

```python
vital_signs = {
    "systolic_bp": 120,        # 收缩压 (mmHg)
    "diastolic_bp": 80,        # 舒张压 (mmHg)
    "heart_rate": 72,          # 心率 (bpm)
    "temperature": 36.5,       # 体温 (°C)
    "respiratory_rate": 16,    # 呼吸频率 (次/分)
    "oxygen_saturation": 98.5  # 血氧饱和度 (%)
}
```

**自动计算字段**:
- `mean_arterial_pressure`: 平均动脉压
- `bp_category`: 血压分类 (normal, elevated, high_stage1, etc.)
- `temperature_fahrenheit`: 华氏温度

### 2. 检验结果 (LAB_RESULTS)

```python
lab_results = {
    "glucose": 95.0,           # 血糖 (mg/dL)
    "cholesterol_total": 180.0, # 总胆固醇 (mg/dL)
    "hdl_cholesterol": 55.0,   # 高密度脂蛋白 (mg/dL)
    "ldl_cholesterol": 110.0,  # 低密度脂蛋白 (mg/dL)
    "triglycerides": 120.0,    # 甘油三酯 (mg/dL)
    "hemoglobin": 14.5         # 血红蛋白 (g/dL)
}
```

**自动计算字段**:
- `glucose_category`: 血糖分类
- `cholesterol_ratio`: 胆固醇比值
- `glucose_mmol`: 血糖值 (mmol/L)

### 3. 可穿戴设备数据 (WEARABLE_DATA)

```python
wearable_data = {
    "steps": 8500,             # 步数
    "distance": 6.2,           # 距离 (km)
    "calories_burned": 320,    # 消耗卡路里
    "sleep_duration": 7.5,     # 睡眠时长 (小时)
    "sleep_quality": 85.0      # 睡眠质量评分
}
```

### 4. 中医望诊数据 (TCM_LOOK)

```python
tcm_look_data = {
    "face_color": "红润",
    "tongue_color": "淡红",
    "tongue_coating": "薄白",
    "body_posture": "端正"
}
```

### 5. 中医闻诊数据 (TCM_LISTEN)

```python
tcm_listen_data = {
    # 语音特征
    "voice_strength": "洪亮",  # 语音强度：洪亮、低微、嘶哑、失音
    "speech_speed": "正常",    # 语速：正常、急促、缓慢、断续
    
    # 呼吸音
    "breathing_sound": "平和", # 呼吸音：平和、粗糙、微弱、喘促
    "cough_sound": "无",       # 咳嗽声：无、干咳、湿咳、顿咳
    
    # 心音特征
    "heart_sound_rhythm": "规律",    # 心音节律：规律、不规律、间歇、奔马律
    "heart_sound_intensity": "正常"  # 心音强度：正常、增强、减弱、杂音
}
```

### 6. 中医问诊数据 (TCM_INQUIRY)

```python
tcm_inquiry_data = {
    "chief_complaint": "头痛眩晕，心悸失眠",
    "symptom_duration": "慢性",
    "cold_heat": "无明显寒热",
    "sweating": "盗汗",
    "appetite": "食欲不振",
    "sleep_quality": "失眠"
}
```

### 7. 中医切诊数据 (TCM_PALPATION)

```python
tcm_palpation_data = {
    "pulse_position": "浮",
    "pulse_rate": "数",
    "pulse_shape": "弦",
    "skin_temperature": "正常"
}
```

### 8. 中医算诊数据 (TCM_CALCULATION)

```python
tcm_calculation_data = {
    "birth_year": 1990,
    "birth_month": 5,
    "birth_day": 15,
    "birth_hour": 14,
    "gender": "女",
    "constitution_type": "气虚质",
    "life_hexagram": "坤"
}
```

## 流水线配置

```python
from health_data_service.services.health_data_pipeline import PipelineConfig

# 自定义配置
config = PipelineConfig(
    enable_standardization=True,    # 启用数据标准化
    enable_privacy_proof=True,      # 启用隐私证明
    enable_quality_check=True,      # 启用质量检查
    min_quality_score=70.0,         # 最低质量分数
    privacy_proof_types=[           # 隐私证明类型
        "blood_pressure",
        "blood_glucose",
        "data_integrity"
    ]
)

pipeline = HealthDataPipeline(config)
```

## 批量处理

```python
# 批量处理多条数据
batch_data = [
    {"systolic_bp": 110, "diastolic_bp": 70, "heart_rate": 68},
    {"systolic_bp": 125, "diastolic_bp": 82, "heart_rate": 75},
    {"systolic_bp": 135, "diastolic_bp": 88, "heart_rate": 80}
]

results = await pipeline.batch_process_health_data(
    data_list=batch_data,
    data_type=DataType.VITAL_SIGNS,
    user_id="user_001",
    source="batch_import"
)

for i, result in enumerate(results):
    print(f"数据 {i+1}: {result.status}, 质量: {result.standardized_data.quality_score}")
```

## 零知识验证

### 生成证明

```python
from services.common.security.zk_snarks import prove_blood_pressure_valid

# 生成血压有效性证明
proof = prove_blood_pressure_valid(systolic=120, diastolic=80)
print(f"证明哈希: {proof.data_hash}")
```

### 验证证明

```python
from services.common.security.zk_snarks import verify_health_proof

# 验证证明
is_valid = verify_health_proof(proof)
print(f"证明有效: {is_valid}")
```

## 区块链集成

```python
from services.blockchain_service.zk_integration import (
    store_health_proof_on_blockchain,
    verify_health_proof_from_blockchain
)

# 存储证明到区块链
transaction_id = await store_health_proof_on_blockchain(
    user_id="user_001",
    proof=proof,
    metadata={"source": "hospital_a"}
)

# 从区块链验证证明
verification_result = await verify_health_proof_from_blockchain(
    data_hash=proof.data_hash,
    requester_id="doctor_001"
)
```

## 数据质量评估

流水线会自动评估数据质量并分配等级：

- **HIGH (90-100分)**: 高质量数据，完整且准确
- **MEDIUM (70-89分)**: 中等质量，可能有轻微问题
- **LOW (50-69分)**: 低质量，存在明显问题
- **INVALID (<50分)**: 无效数据，不建议使用

## 错误处理

```python
result = await pipeline.process_health_data(data, DataType.VITAL_SIGNS, "user_001")

if result.status == ProcessingStatus.FAILED:
    print("处理失败:")
    for error in result.errors:
        print(f"  - {error}")

if result.warnings:
    print("警告:")
    for warning in result.warnings:
        print(f"  - {warning}")
```

## 监控和统计

```python
# 获取流水线统计信息
stats = pipeline.get_pipeline_statistics()
print(f"总处理数: {stats['total_processed']}")
print(f"成功率: {stats['success_rate']:.2%}")

# 获取特定流水线状态
status = pipeline.get_pipeline_status("pipeline_id")
if status:
    print(f"流水线状态: {status['result']['status']}")
```

## 最佳实践

### 1. 数据预处理
- 确保数据格式正确
- 移除明显的异常值
- 使用标准单位

### 2. 隐私保护
- 仅在必要时生成零知识证明
- 定期轮换加密密钥
- 限制数据访问权限

### 3. 性能优化
- 使用批量处理处理大量数据
- 合理配置质量检查阈值
- 监控处理时间和资源使用

### 4. 错误处理
- 实现重试机制
- 记录详细的错误日志
- 提供用户友好的错误信息

## 测试

运行完整的测试套件：

```bash
# 运行单元测试
python -m pytest tests/test_health_data_pipeline.py -v

# 运行集成测试
python tests/test_health_data_pipeline.py
```

## 故障排除

### 常见问题

1. **导入错误**: 确保所有依赖已正确安装
2. **数据验证失败**: 检查数据格式和范围
3. **证明生成失败**: 验证输入数据的有效性
4. **性能问题**: 考虑使用批量处理或调整配置

### 日志配置

```python
import logging

# 配置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 贡献

欢迎提交问题报告和功能请求。请确保：

1. 提供详细的问题描述
2. 包含重现步骤
3. 添加相关的测试用例
4. 遵循代码风格指南

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

### 中医五诊数据处理示例

```python
from health_data_service.services.health_data_pipeline import (
    process_tcm_look_data,
    process_tcm_listen_data,
    process_tcm_inquiry_data,
    process_tcm_palpation_data,
    process_tcm_calculation_data
)

# 处理中医望诊数据
tcm_look_data = {
    "face_color": "红润",
    "tongue_color": "淡红",
    "tongue_coating": "薄白",
    "body_posture": "端正"
}

result = await process_tcm_look_data(
    data=tcm_look_data,
    user_id="user123",
    source="tcm_clinic"
)

# 处理中医问诊数据
tcm_inquiry_data = {
    "chief_complaint": "头痛眩晕，心悸失眠",
    "symptom_duration": "慢性",
    "cold_heat": "无明显寒热",
    "sweating": "盗汗",
    "appetite": "食欲不振",
    "sleep_quality": "失眠"
}

result = await process_tcm_inquiry_data(
    data=tcm_inquiry_data,
    user_id="user123",
    source="tcm_clinic"
)

# 处理中医切诊数据
tcm_palpation_data = {
    "pulse_position": "浮",
    "pulse_rate": "数",
    "pulse_shape": "弦",
    "skin_temperature": "正常"
}

result = await process_tcm_palpation_data(
    data=tcm_palpation_data,
    user_id="user123",
    source="tcm_clinic"
)

# 处理中医算诊数据
tcm_calculation_data = {
    "birth_year": 1990,
    "birth_month": 5,
    "birth_day": 15,
    "birth_hour": 14,
    "gender": "女",
    "constitution_type": "气虚质",
    "life_hexagram": "坤"
}

result = await process_tcm_calculation_data(
    data=tcm_calculation_data,
    user_id="user123",
    source="tcm_calculation"
) 