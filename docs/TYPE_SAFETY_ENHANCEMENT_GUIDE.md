# 索克生活 - 类型安全增强指南

## 概述

本指南介绍了索克生活项目中新增的类型安全增强功能，包括：

- **MCP时间戳服务类型**：标准化的时间数据管理
- **中医辨证类型定义**：完整的TCM数据结构
- **增强的生物标志物类型**：集成中医辨证关联字段
- **五诊数据类型**：望闻问切算的数字化表示
- **智能体诊断结果类型**：四个智能体的协同诊断
- **算诊数据类型**：基于中医理论的计算诊断

## 核心特性

### 1. MCP时间戳服务

#### 特点
- **标准化格式**：统一的时间戳结构
- **多精度支持**：秒、毫秒、微秒精度
- **来源追踪**：设备、服务器、传感器、手动输入
- **同步状态**：NTP同步验证
- **时区感知**：自动时区检测和转换

#### 使用示例

```typescript
import { createMCPTimestamp, formatMCPTimestamp, getRelativeTime } from '../utils/mcpTimestamp';

// 创建当前时间戳
const timestamp = createMCPTimestamp('device', 'millisecond');

// 格式化显示
const formatted = formatMCPTimestamp(timestamp);
console.log(formatted); // "2024/01/15 14:30:25"

// 相对时间
const relative = getRelativeTime(timestamp);
console.log(relative); // "刚刚" 或 "5分钟前"
```

### 2. 增强的生物标志物数据类型

#### 新增字段
- **MCP时间戳**：替代简单字符串时间戳
- **中医辨证关联**：关联脏腑、证候、中医解释
- **数据质量指标**：可靠性、异常值检测
- **趋势信息**：变化方向和显著性

#### 使用示例

```typescript
import { BiomarkerData } from '../types/TCM';
import { createMCPTimestamp } from '../utils/mcpTimestamp';

const heartRateData: BiomarkerData = {
  id: 'heart-rate-001',
  name: '心率',
  type: 'vital-sign',
  value: 72,
  unit: 'bpm',
  timestamp: createMCPTimestamp('device'),
  referenceRange: {
    min: 60,
    max: 100,
    optimal: 70
  },
  tcmAssociation: {
    relatedOrgans: [{
      organ: 'heart',
      state: 'normal',
      score: 85,
      symptoms: [],
      assessedAt: createMCPTimestamp('server')
    }],
    relatedSyndromes: [],
    tcmInterpretation: '心率正常，心气充足，血脉运行顺畅',
    tcmIndicators: ['心气', '血脉']
  },
  quality: {
    reliability: 0.95,
    isOutlier: false,
    source: 'device'
  },
  trend: {
    direction: 'stable',
    rate: 0.02,
    significance: 'minimal'
  }
};
```

### 3. 中医辨证类型系统

#### 体质类型
支持九种标准中医体质：
- `qi-deficiency` - 气虚质
- `yang-deficiency` - 阳虚质
- `yin-deficiency` - 阴虚质
- `phlegm-dampness` - 痰湿质
- `damp-heat` - 湿热质
- `blood-stasis` - 血瘀质
- `qi-stagnation` - 气郁质
- `special-diathesis` - 特禀质
- `balanced` - 平和质

#### 证候类型
```typescript
import { TCMSyndrome } from '../types/TCM';

const syndrome: TCMSyndrome = {
  name: '气虚血瘀',
  code: 'QXXY-001',
  category: 'qi-blood',
  severity: 'moderate',
  confidence: 0.85,
  symptoms: ['乏力', '面色苍白', '舌质暗'],
  diagnosedAt: createMCPTimestamp('server')
};
```

### 4. 五诊数据类型

#### 望诊数据
```typescript
import { InspectionData } from '../types/TCM';

const inspection: InspectionData = {
  complexion: {
    color: 'red',
    luster: 'lustrous',
    description: '面色红润有光泽'
  },
  tongue: {
    body: {
      color: 'red',
      texture: 'normal',
      shape: 'normal'
    },
    coating: {
      color: 'white',
      thickness: 'thin',
      moisture: 'moist'
    }
  },
  spirit: 'vigorous',
  bodyType: 'normal',
  timestamp: createMCPTimestamp('manual')
};
```

#### 切诊数据（脉诊）
```typescript
import { PalpationData } from '../types/TCM';

const palpation: PalpationData = {
  pulse: {
    position: 'middle',
    rate: 72,
    rhythm: 'regular',
    strength: 'normal',
    shape: 'normal',
    quality: 'floating'
  },
  palpation: {
    abdomen: {
      tenderness: false,
      distension: false,
      masses: false,
      temperature: 'normal'
    },
    acupoints: [{
      name: '神门',
      tenderness: false,
      sensitivity: 3
    }]
  },
  timestamp: createMCPTimestamp('manual')
};
```

### 5. 算诊数据类型

#### 算诊数据（CalculationData）

算诊是索克生活项目的创新功能，将传统中医理论与现代计算技术相结合：

```typescript
interface CalculationData {
  id: string;
  patientInfo: {
    birthTime: MCPTimestamp;
    gender: 'male' | 'female';
    birthLocation?: {
      latitude: number;
      longitude: number;
      timezone: string;
    };
  };
  
  // 子午流注分析
  ziwuLiuzhu: {
    currentHour: {
      earthlyBranch: string;  // 地支
      meridian: string;       // 当令经络
      organ: string;          // 对应脏腑
    };
    openingPoints: Array<{
      time: string;
      point: string;
      meridian: string;
      function: string;
    }>;
    optimalTreatmentTime: {
      start: MCPTimestamp;
      end: MCPTimestamp;
      reason: string;
    };
    recommendations: string[];
  };
  
  // 四柱八字体质分析
  constitutionAnalysis: {
    fourPillars: {
      year: { heavenly: string; earthly: string };
      month: { heavenly: string; earthly: string };
      day: { heavenly: string; earthly: string };
      hour: { heavenly: string; earthly: string };
    };
    fiveElements: {
      wood: number;
      fire: number;
      earth: number;
      metal: number;
      water: number;
    };
    constitutionType: TCMConstitution;
    elementStrength: {
      strongest: string;
      weakest: string;
      balance: number; // 0-1，1表示完全平衡
    };
    adjustmentAdvice: {
      strengthen: string[];
      reduce: string[];
      methods: string[];
    };
  };
  
  // 八卦方位分析
  baguaAnalysis: {
    natalHexagram: {
      name: string;
      symbol: string;
      element: string;
      direction: string;
    };
    healthAnalysis: {
      strengths: string[];
      weaknesses: string[];
      risks: string[];
    };
    directionalGuidance: {
      favorable: string[];
      unfavorable: string[];
      livingAdvice: string[];
    };
  };
  
  // 五运六气分析
  wuyunLiuqi: {
    annualQi: {
      year: number;
      mainQi: string;
      guestQi: string;
      hostHeaven: string;
      hostEarth: string;
    };
    diseasePrediction: {
      susceptibleDiseases: string[];
      preventionMethods: string[];
      criticalPeriods: Array<{
        period: string;
        risk: 'low' | 'medium' | 'high';
        description: string;
      }>;
    };
    seasonalGuidance: {
      spring: string[];
      summer: string[];
      autumn: string[];
      winter: string[];
    };
  };
  
  // 综合分析结果
  comprehensiveResult: {
    overallScore: number; // 0-100
    primaryRisks: Array<{
      risk: string;
      severity: 'low' | 'medium' | 'high';
      probability: number; // 0-1
      prevention: string[];
    }>;
    personalizedPlan: {
      immediate: string[];
      shortTerm: string[];
      longTerm: string[];
    };
    optimalTimings: Array<{
      activity: string;
      timing: string;
      reason: string;
    }>;
  };
  
  confidence: {
    overall: number;
    ziwuLiuzhu: number;
    constitution: number;
    bagua: number;
    wuyunLiuqi: number;
  };
  
  timestamp: MCPTimestamp;
  practitioner?: {
    id: string;
    name: string;
    qualification: string;
  };
}
```

### 6. 智能体诊断结果

#### 四个智能体协同诊断
```typescript
import { AgentDiagnosisResult } from '../types/TCM';

const diagnosis: AgentDiagnosisResult = {
  agentId: 'xiaoai', // 'xiaoai' | 'xiaoke' | 'laoke' | 'soer'
  diagnosis: {
    primarySyndrome: {
      name: '气血平和',
      code: 'QX-001',
      category: 'qi-blood',
      severity: 'mild',
      confidence: 0.85,
      symptoms: ['精神饱满', '面色红润'],
      diagnosedAt: createMCPTimestamp('server')
    },
    secondarySyndromes: [],
    constitution: 'balanced',
    organStates: []
  },
  treatment: {
    principle: '调和气血，养心安神',
    lifestyle: {
      diet: ['清淡饮食', '多食新鲜蔬果'],
      exercise: ['适量有氧运动', '太极拳'],
      sleep: ['规律作息', '晚上11点前入睡'],
      emotion: ['保持心情愉悦', '避免过度紧张']
    }
  },
  confidence: 0.85,
  timestamp: createMCPTimestamp('server'),
  dataSource: {
    biomarkers: [heartRateData]
  }
};
```

## 组件使用示例

### 增强健康仪表板组件

```typescript
import React from 'react';
import { EnhancedHealthDashboard } from '../components/health/EnhancedHealthDashboard';

const HealthScreen: React.FC = () => {
  return (
    <EnhancedHealthDashboard
      userId="user-001"
      onBiomarkerPress={(biomarker) => {
        // 处理生物标志物点击
        console.log('生物标志物:', biomarker.name, biomarker.tcmAssociation.tcmInterpretation);
      }}
      onAgentDiagnosisPress={(diagnosis) => {
        // 处理智能体诊断点击
        console.log('智能体诊断:', diagnosis.agentId, diagnosis.diagnosis.primarySyndrome.name);
      }}
    />
  );
};
```

## 类型安全优势

### 1. 编译时错误检测
```typescript
// ❌ 编译错误：缺少必需字段
const invalidBiomarker: BiomarkerData = {
  id: 'test',
  name: '测试'
  // 缺少其他必需字段，TypeScript会报错
};

// ✅ 正确：包含所有必需字段
const validBiomarker: BiomarkerData = {
  id: 'test',
  name: '测试',
  type: 'vital-sign',
  value: 100,
  unit: 'unit',
  timestamp: createMCPTimestamp(),
  referenceRange: { min: 0, max: 200 },
  tcmAssociation: {
    relatedOrgans: [],
    relatedSyndromes: [],
    tcmInterpretation: '正常',
    tcmIndicators: []
  },
  quality: {
    reliability: 1.0,
    isOutlier: false,
    source: 'device'
  }
};
```

### 2. 智能代码补全
IDE会提供完整的类型提示和自动补全功能。

### 3. 重构安全性
类型系统确保重构时不会破坏现有代码。

## 数据验证

### MCP时间戳验证
```typescript
import { validateMCPTimestamp } from '../utils/mcpTimestamp';

const timestamp = createMCPTimestamp();
if (validateMCPTimestamp(timestamp)) {
  console.log('时间戳有效');
} else {
  console.error('时间戳无效');
}
```

### 数据完整性检查
```typescript
import { ComprehensiveHealthData } from '../types/TCM';

const validateHealthData = (data: ComprehensiveHealthData): boolean => {
  // 检查时间戳有效性
  const timestampValid = validateMCPTimestamp(data.lastUpdated);
  
  // 检查完整性评分
  const completenessValid = data.completenessScore >= 0 && data.completenessScore <= 1;
  
  // 检查生物标志物数据质量
  const biomarkersValid = data.biomarkers.every(biomarker => 
    validateMCPTimestamp(biomarker.timestamp) &&
    biomarker.quality.reliability >= 0 &&
    biomarker.quality.reliability <= 1
  );
  
  return timestampValid && completenessValid && biomarkersValid;
};
```

## 最佳实践

### 1. 始终使用MCP时间戳
```typescript
// ❌ 避免使用简单字符串
const badTimestamp = new Date().toISOString();

// ✅ 使用MCP时间戳
const goodTimestamp = createMCPTimestamp('device');
```

### 2. 提供完整的中医辨证关联
```typescript
// 为每个生物标志物提供中医解释
const biomarker: BiomarkerData = {
  // ... 其他字段
  tcmAssociation: {
    relatedOrgans: [/* 相关脏腑 */],
    relatedSyndromes: [/* 相关证候 */],
    tcmInterpretation: '详细的中医意义解释',
    tcmIndicators: ['相关中医指标']
  }
};
```

### 3. 验证数据质量
```typescript
// 始终检查数据可靠性
if (biomarker.quality.reliability < 0.8) {
  console.warn('数据可靠性较低，请谨慎使用');
}

// 检查异常值
if (biomarker.quality.isOutlier) {
  console.warn('检测到异常值');
}
```

### 4. 利用智能体协同
```typescript
// 收集多个智能体的诊断结果
const agentDiagnoses = await Promise.all([
  getXiaoaiDiagnosis(healthData),
  getXiaokeDiagnosis(healthData),
  getLaokeDiagnosis(healthData),
  getSoerDiagnosis(healthData)
]);

// 综合分析置信度
const averageConfidence = agentDiagnoses.reduce(
  (sum, diagnosis) => sum + diagnosis.confidence, 0
) / agentDiagnoses.length;
```

## 测试

运行类型安全测试：

```bash
# 运行TCM类型测试
npm test src/types/__tests__/TCM.test.ts

# 运行MCP时间戳服务测试
npm test src/utils/__tests__/mcpTimestamp.test.ts
```

## 总结

通过引入这些类型安全增强功能，索克生活项目现在具备了：

1. **标准化的时间数据管理**：MCP时间戳服务确保时间数据的一致性和可追溯性
2. **完整的中医辨证数字化**：涵盖五诊、证候、体质、脏腑状态的完整类型系统
3. **增强的数据质量保证**：内置数据验证和质量评估机制
4. **智能体协同诊断**：支持四个智能体的分布式诊断决策
5. **类型安全的开发体验**：编译时错误检测、智能代码补全、重构安全性

这些增强功能为构建可靠、可维护的健康管理平台奠定了坚实的基础。 