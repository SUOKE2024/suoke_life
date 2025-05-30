# 零知识证明健康报告使用指南

## 概述

零知识证明（Zero-Knowledge Proof, ZKP）健康报告模块允许用户在不泄露具体健康数据的情况下，证明自己的健康状况符合特定要求。这对于保护用户隐私同时满足健康验证需求非常重要。

## 核心功能

### 1. 支持的证明类型

- **年龄范围证明** (`AGE_RANGE`): 证明年龄在指定范围内，而不暴露具体年龄
- **健康状态证明** (`HEALTH_STATUS`): 证明健康指标符合特定标准
- **生命体征范围证明** (`VITAL_SIGNS_RANGE`): 证明生命体征在正常范围内
- **体质类型证明** (`CONSTITUTION_TYPE`): 证明具有或不具有特定体质类型
- **用药依从性证明** (`MEDICATION_COMPLIANCE`): 证明用药依从率达到要求
- **活动水平证明** (`ACTIVITY_LEVEL`): 证明活动水平达到特定级别
- **风险评估证明** (`RISK_ASSESSMENT`): 证明健康风险在可接受范围内

### 2. 主要接口

```typescript
// 生成单个健康证明
generateHealthProof(request: HealthProofRequest): Promise<ZKProof>

// 验证健康证明
verifyHealthProof(proof: ZKProof, publicInputs?: any[]): Promise<VerificationResult>

// 生成综合健康报告
generateComprehensiveHealthProof(userId: string, healthData: any, requirements: any): Promise<ZKProof[]>

// 验证综合健康报告
verifyComprehensiveHealthProof(proofs: ZKProof[]): Promise<{allValid: boolean; results: VerificationResult[]}>
```

## 使用示例

### 1. 年龄范围证明

用于保险申请、健康服务资格验证等场景：

```typescript
import { generateHealthProof, verifyHealthProof, ProofType } from '@/agents/zkp_health_report';

// 生成年龄范围证明
const ageProof = await generateHealthProof({
  userId: 'user_123',
  proofType: ProofType.AGE_RANGE,
  privateData: { 
    actualAge: 35  // 实际年龄（私有数据）
  },
  publicAttributes: { 
    minAge: 18,    // 最小年龄要求
    maxAge: 65     // 最大年龄要求
  },
  expirationTime: 24 * 60 * 60 * 1000  // 24小时有效期
});

// 验证证明
const verificationResult = await verifyHealthProof(ageProof);
console.log('证明有效:', verificationResult.valid);
console.log('验证消息:', verificationResult.message);
```

### 2. 生命体征范围证明

用于健康检查、医疗服务申请等场景：

```typescript
// 定义生命体征数据
const vitalSigns = {
  temperature: 36.5,
  heartRate: 72,
  bloodPressureSystolic: 120,
  bloodPressureDiastolic: 80,
  respiratoryRate: 16,
  oxygenSaturation: 98
};

// 定义正常范围
const normalRanges = [
  { metric: 'temperature', min: 36.0, max: 37.5, unit: '℃' },
  { metric: 'heartRate', min: 60, max: 100, unit: 'bpm' },
  { metric: 'bloodPressureSystolic', min: 90, max: 140, unit: 'mmHg' },
  { metric: 'bloodPressureDiastolic', min: 60, max: 90, unit: 'mmHg' },
  { metric: 'oxygenSaturation', min: 95, max: 100, unit: '%' }
];

// 生成证明
const vitalSignsProof = await generateHealthProof({
  userId: 'user_123',
  proofType: ProofType.VITAL_SIGNS_RANGE,
  privateData: { vitalSigns },
  publicAttributes: { 
    ranges: normalRanges,
    allInRange: true  // 所有指标都在正常范围内
  }
});
```

### 3. 体质类型证明

用于中医健康管理、个性化健康方案等场景：

```typescript
// 体质评估数据
const constitutionData = {
  types: ['平和质', '气虚质', '阳虚质'],
  scores: { 
    平和质: 65,
    气虚质: 20,
    阳虚质: 15
  },
  dominantType: '平和质',
  assessmentDate: '2024-01-15'
};

// 生成体质证明
const constitutionProof = await generateHealthProof({
  userId: 'user_123',
  proofType: ProofType.CONSTITUTION_TYPE,
  privateData: { constitutionData },
  publicAttributes: {
    hasType: ['平和质'],           // 具有的体质类型
    doesNotHaveType: ['痰湿质'],   // 不具有的体质类型
    dominantType: '平和质'         // 主导体质类型
  }
});
```

### 4. 综合健康报告

用于全面健康评估、健康保险申请等场景：

```typescript
// 准备综合健康数据
const comprehensiveHealthData = {
  age: 35,
  vitalSigns: {
    temperature: 36.5,
    heartRate: 72,
    bloodPressureSystolic: 120,
    bloodPressureDiastolic: 80
  },
  constitutionType: ['平和质', '气虚质'],
  activityLevel: '活跃',
  riskFactors: [
    { factor: '血压', level: 'normal' },
    { factor: '血糖', level: 'normal' },
    { factor: '胆固醇', level: 'normal' }
  ],
  medicationCompliance: {
    rate: 95,
    period: '过去3个月'
  }
};

// 定义验证要求
const healthRequirements = {
  ageRange: { min: 18, max: 65 },
  vitalSignsRanges: [
    { metric: 'temperature', min: 36.0, max: 37.5, unit: '℃' },
    { metric: 'heartRate', min: 60, max: 100, unit: 'bpm' },
    { metric: 'bloodPressureSystolic', min: 90, max: 140, unit: 'mmHg' },
    { metric: 'bloodPressureDiastolic', min: 60, max: 90, unit: 'mmHg' }
  ],
  requiredConstitutionTypes: ['平和质'],
  minActivityLevel: '中等',
  maxRiskLevel: '中风险'
};

// 生成综合健康证明
const proofs = await generateComprehensiveHealthProof(
  'user_123',
  comprehensiveHealthData,
  healthRequirements
);

// 验证所有证明
const verificationResults = await verifyComprehensiveHealthProof(proofs);
console.log('所有证明有效:', verificationResults.allValid);
console.log('各项验证结果:', verificationResults.results);
```

### 5. 用药依从性证明

用于慢病管理、医疗保险理赔等场景：

```typescript
// 用药记录（私有数据）
const medicationRecords = [
  { date: '2024-01-01', medication: 'Medicine A', taken: true, time: '08:00' },
  { date: '2024-01-02', medication: 'Medicine A', taken: true, time: '08:15' },
  { date: '2024-01-03', medication: 'Medicine A', taken: true, time: '08:00' },
  { date: '2024-01-04', medication: 'Medicine A', taken: false, reason: '忘记' },
  { date: '2024-01-05', medication: 'Medicine A', taken: true, time: '08:30' }
];

// 生成依从性证明
const complianceProof = await generateHealthProof({
  userId: 'user_123',
  proofType: ProofType.MEDICATION_COMPLIANCE,
  privateData: { medicationRecords },
  publicAttributes: {
    complianceRate: 80,      // 依从率达到80%
    period: '2024年1月'      // 统计周期
  }
});
```

## 高级功能

### 1. 证明有效期设置

```typescript
const proofWithExpiration = await generateHealthProof({
  userId: 'user_123',
  proofType: ProofType.HEALTH_STATUS,
  privateData: { healthMetrics },
  publicAttributes: { meetsStandards: true, category: '优秀' },
  expirationTime: 7 * 24 * 60 * 60 * 1000  // 7天有效期
});
```

### 2. 自定义密钥

```typescript
const customSecret = 'user_custom_secret_key';
const proofWithCustomSecret = await generateHealthProof({
  userId: 'user_123',
  proofType: ProofType.AGE_RANGE,
  privateData: { actualAge: 35 },
  publicAttributes: { minAge: 18, maxAge: 65 },
  secret: customSecret  // 使用自定义密钥
});
```

### 3. 公共输入验证

```typescript
// 生成证明
const proof = await generateHealthProof({
  userId: 'user_123',
  proofType: ProofType.AGE_RANGE,
  privateData: { actualAge: 35 },
  publicAttributes: { minAge: 18, maxAge: 65 }
});

// 验证时提供公共输入
const result = await verifyHealthProof(proof, [18, 65]);
// 只有当公共输入匹配时，验证才会通过
```

## 安全注意事项

1. **密钥管理**: 
   - 建议为每个用户生成唯一的密钥
   - 密钥应安全存储，不应在网络中传输
   - 定期更新密钥以提高安全性

2. **证明有效期**:
   - 根据使用场景设置合适的有效期
   - 避免证明被长期重复使用
   - 验证时始终检查有效期

3. **数据完整性**:
   - 确保私有数据的真实性和准确性
   - 使用可信的数据源
   - 定期审计证明生成过程

4. **隐私保护**:
   - 仅暴露必要的公共属性
   - 避免在证明中包含可识别个人身份的信息
   - 使用最小化披露原则

## 性能优化建议

1. **批量处理**: 使用 `BatchProofGenerator` 批量生成多个证明
2. **缓存机制**: 对频繁验证的证明实施缓存
3. **异步处理**: 使用异步方法避免阻塞主线程
4. **压缩存储**: 对证明数据进行压缩以减少存储空间

## 集成示例

### 与智能合约集成

```typescript
// 将证明提交到区块链
async function submitProofToBlockchain(proof: ZKProof) {
  const proofHash = CryptoJS.SHA256(JSON.stringify(proof)).toString();
  
  // 调用智能合约方法
  await contract.submitHealthProof(
    proof.id,
    proofHash,
    proof.publicInputs,
    proof.timestamp
  );
}
```

### 与API服务集成

```typescript
// API端点示例
app.post('/api/health/verify-age', async (req, res) => {
  const { proof, requiredAge } = req.body;
  
  // 验证证明
  const result = await verifyHealthProof(proof, [requiredAge.min, requiredAge.max]);
  
  if (result.valid) {
    res.json({ 
      success: true, 
      message: '年龄验证通过',
      details: result.details 
    });
  } else {
    res.status(400).json({ 
      success: false, 
      message: result.message 
    });
  }
});
```

## 故障排除

### 常见问题

1. **证明验证失败**:
   - 检查证明是否过期
   - 确认公共输入是否匹配
   - 验证证明结构是否完整

2. **性能问题**:
   - 减少证明的复杂度
   - 使用批量处理
   - 实施适当的缓存策略

3. **兼容性问题**:
   - 确保使用相同版本的算法
   - 检查数据格式是否一致
   - 验证加密库版本兼容性

## 未来扩展

1. **支持更多证明类型**: 如基因检测结果、疫苗接种记录等
2. **集成专业ZK库**: 如 snarkjs、libsnark 等
3. **链上验证优化**: 减少 gas 消耗
4. **多方计算支持**: 支持多个数据源的联合证明
5. **隐私增强技术**: 集成同态加密、安全多方计算等技术

## 总结

零知识证明健康报告模块为"索克生活"平台提供了强大的隐私保护能力，使用户能够在保护个人健康数据隐私的同时，满足各种健康验证需求。通过合理使用本模块，可以构建一个既安全又实用的健康数据生态系统。 