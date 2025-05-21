# Privacy-ZKP 数据集格式说明

Privacy-ZKP 是用于评估健康数据隐私保护和零知识证明技术在索克生活APP中应用的测试数据集。

## 数据组织结构

```
privacy-zkp/
├── metadata.json               # 元数据信息
├── zkp-proofs/                 # 零知识证明测试数据
│   ├── health_records/         # 健康记录验证
│   ├── biometric_auth/         # 生物特征认证
│   └── consent_verification/   # 隐私同意验证
├── privacy_attacks/            # 隐私攻击测试数据
│   ├── inference_attacks/      # 推理攻击
│   ├── membership_attacks/     # 成员推断攻击
│   └── model_inversion/        # 模型反演攻击
└── compliance/                 # 合规性测试
    ├── train/                  # 训练集
    ├── val/                    # 验证集
    └── test/                   # 测试集（用于评测）
```

## 数据格式

隐私与安全测试数据采用JSON格式，基本结构如下：

### 零知识证明测试案例

```json
{
  "id": "zkp_health_001",
  "title": "慢性病状态零知识验证",
  "category": "health_records",
  "description": "验证用户是否患有特定慢性病，而无需披露具体病名或医疗记录",
  "scenario": {
    "context": "用户需要向保险服务提供慢性病状态证明，但不愿意披露具体疾病信息",
    "requirements": [
      "验证用户是否有慢性病",
      "不泄露具体是哪种慢性病",
      "不泄露诊断时间和治疗方案"
    ]
  },
  "input_data": {
    "user_id": "user_12345",
    "health_record_hash": "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
    "claim": "user_has_chronic_condition",
    "public_inputs": {
      "verified_hospital_id": "hospital_456",
      "record_timestamp_range": ["2023-01-01", "2023-12-31"]
    }
  },
  "zkp_parameters": {
    "protocol": "groth16",
    "curve": "bn254",
    "circuit_complexity": {
      "constraints": 5240,
      "variables": 5300
    }
  },
  "expected_proof": {
    "valid": true,
    "verification_time_ms": 120,
    "proof_size_bytes": 192
  },
  "attack_vectors": [
    {
      "type": "tampered_record",
      "description": "尝试使用篡改的健康记录生成证明",
      "expected_result": "verification_failed"
    },
    {
      "type": "outdated_record",
      "description": "使用过期的健康记录生成证明",
      "expected_result": "verification_failed"
    }
  ],
  "performance_metrics": {
    "proving_time_ms": {
      "mean": 1850,
      "p95": 2100,
      "max": 2500
    },
    "verification_time_ms": {
      "mean": 100,
      "p95": 150,
      "max": 200
    },
    "proof_size_bytes": 192,
    "memory_usage_mb": 450
  }
}
```

### 隐私攻击测试案例

```json
{
  "id": "privacy_attack_001",
  "title": "健康数据成员推断攻击",
  "category": "membership_attacks",
  "description": "测试攻击者能否判断某用户的数据是否被用于训练特定健康模型",
  "threat_model": {
    "attacker_capability": "黑盒访问模型API",
    "knowledge_level": "了解模型架构，无训练数据访问权限",
    "attack_goal": "判断目标用户的健康数据是否在训练集中"
  },
  "target_model": {
    "id": "health_prediction_model_v2",
    "type": "diagnostic_prediction",
    "access_pattern": "query_only"
  },
  "attack_method": {
    "name": "ShadowModel",
    "parameters": {
      "shadow_models_count": 10,
      "queries_per_model": 1000,
      "confidence_threshold": 0.8
    },
    "implementation_details": "使用模型预测置信度分布差异识别训练数据"
  },
  "test_data": {
    "member_samples": 100,
    "non_member_samples": 100,
    "feature_dimensions": 50
  },
  "defense_measure": {
    "name": "差分隐私",
    "parameters": {
      "epsilon": 2.0,
      "delta": 1e-5,
      "mechanism": "gaussian"
    },
    "expected_utility_loss": 0.05
  },
  "expected_results": {
    "baseline_attack_success_rate": 0.76,
    "with_defense_attack_success_rate": 0.53,
    "privacy_leakage_reduction": 0.23,
    "false_positive_rate": 0.08,
    "false_negative_rate": 0.12
  },
  "evaluation_metrics": {
    "auc": 0.81,
    "precision": 0.85,
    "recall": 0.72,
    "f1_score": 0.78
  }
}
```

### 隐私合规测试案例

```json
{
  "id": "compliance_test_001",
  "title": "健康数据处理合规性测试",
  "category": "user_consent",
  "description": "测试系统处理健康数据时是否正确执行用户同意设置",
  "regulatory_framework": ["GDPR", "HIPAA", "中国个人信息保护法"],
  "test_scenario": {
    "context": "用户撤回对舌象数据分析的同意授权",
    "initial_state": {
      "user_id": "user_78901",
      "consent_settings": {
        "tongue_image_analysis": true,
        "pulse_data_analysis": true,
        "diet_recommendation": true,
        "data_sharing_research": false
      },
      "data_present": [
        "tongue_images_20230601.jpg",
        "pulse_data_20230605.dat",
        "health_profile.json"
      ]
    },
    "action_sequence": [
      {
        "action": "revoke_consent",
        "target": "tongue_image_analysis",
        "timestamp": "2023-06-10T14:30:00Z"
      },
      {
        "action": "system_update",
        "description": "系统处理撤回同意请求",
        "timestamp": "2023-06-10T14:30:05Z"
      },
      {
        "action": "user_request",
        "description": "用户请求健康分析报告",
        "timestamp": "2023-06-10T15:00:00Z"
      }
    ]
  },
  "expected_behavior": {
    "data_processing": {
      "tongue_image_analysis": {
        "allowed": false,
        "action_taken": "exclude_from_analysis"
      },
      "pulse_data_analysis": {
        "allowed": true,
        "action_taken": "include_in_analysis"
      }
    },
    "data_access": {
      "tongue_images": {
        "user_access": true,
        "system_processing": false,
        "third_party_access": false
      }
    },
    "notifications": [
      {
        "event": "consent_change_confirmation",
        "required": true,
        "timing": "immediate"
      },
      {
        "event": "processing_limitation_notice",
        "required": true,
        "timing": "when_affected_service_requested"
      }
    ]
  },
  "validation_points": [
    {
      "component": "consent_manager",
      "check": "正确更新用户同意状态",
      "method": "数据库记录检查",
      "expected_result": "tongue_image_analysis设置为false"
    },
    {
      "component": "data_processor",
      "check": "仅处理有授权的数据类型",
      "method": "系统日志分析",
      "expected_result": "健康分析不包含舌象分析结果"
    },
    {
      "component": "user_interface",
      "check": "通知用户功能限制",
      "method": "UI检查",
      "expected_result": "显示舌象分析功能已禁用的通知"
    }
  ],
  "compliance_score": {
    "gdpr_alignment": 0.95,
    "hipaa_alignment": 0.90,
    "pipl_alignment": 0.92,
    "overall": 0.92
  }
}
```

## 测试场景

Privacy-ZKP 数据集包含三大类测试场景：

1. **零知识证明应用**：测试系统使用零知识证明技术保护用户隐私的能力
   - 健康状况证明无需透露具体疾病信息
   - 年龄段验证无需提供确切出生日期
   - 合规药方验证无需完全公开用户健康档案

2. **隐私攻击防护**：测试系统抵抗各类隐私攻击的能力
   - 成员推断攻击：判断某用户数据是否用于训练模型
   - 模型反演攻击：从模型输出重建用户敏感信息
   - 推理攻击：从非敏感属性推断敏感属性

3. **隐私合规性**：测试系统遵守隐私法规和用户同意的能力
   - 用户同意授权管理
   - 数据最小化原则实施
   - 数据删除权执行效果

## 数据集获取

完整数据集可通过以下命令下载：

```bash
python -m internal.suokebench.setup --download-data privacy-zkp
```

## 引用与来源

Privacy-ZKP 数据集由索克生活APP团队与隐私安全专家合作开发，用于评估健康应用中的隐私保护技术和实践。数据集模拟了真实场景下的隐私挑战，但不包含任何真实用户数据。 