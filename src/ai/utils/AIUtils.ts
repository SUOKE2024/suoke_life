/**
 * AI工具函数
 * 提供常用的AI相关工具方法
 */

import type { AIRequest, AIResponse } from '../types/AITypes';
import { AITaskType, LLMModelType } from '../types/AITypes';

/**
 * 验证AI请求格式
 */
export function validateAIRequest(request: AIRequest): boolean {
  if (!request.taskType || !Object.values(AITaskType).includes(request.taskType)) {
    return false;
  }

  if (!request.input || (typeof request.input !== 'string' && !(request.input instanceof ArrayBuffer) && !(request.input instanceof File))) {
    return false;
  }

  return true;
}

/**
 * 清理和预处理输入文本
 */
export function preprocessText(text: string): string {
  return text
    .trim()
    .replace(/\s+/g, ' ') // 合并多个空格
    .replace(/[\r\n]+/g, '\n') // 标准化换行符
    .substring(0, 10000); // 限制长度
}

/**
 * 估算token数量（简单估算）
 */
export function estimateTokenCount(text: string): number {
  // 简单的token估算：平均每个token约4个字符
  return Math.ceil(text.length / 4);
}

/**
 * 检查模型是否支持特定任务
 */
export function isModelSupportedForTask(modelType: LLMModelType, taskType: AITaskType): boolean {
  const modelCapabilities: Record<LLMModelType, AITaskType[]> = {
    [LLMModelType.GPT4]: [
      AITaskType.TEXT_GENERATION,
      AITaskType.QUESTION_ANSWERING,
      AITaskType.SUMMARIZATION,
      AITaskType.TRANSLATION,
      AITaskType.HEALTH_ANALYSIS,
      AITaskType.TCM_DIAGNOSIS
    ],
    [LLMModelType.GPT4_TURBO]: [
      AITaskType.TEXT_GENERATION,
      AITaskType.QUESTION_ANSWERING,
      AITaskType.SUMMARIZATION,
      AITaskType.TRANSLATION,
      AITaskType.HEALTH_ANALYSIS,
      AITaskType.TCM_DIAGNOSIS
    ],
    [LLMModelType.GPT4O]: [
      AITaskType.TEXT_GENERATION,
      AITaskType.QUESTION_ANSWERING,
      AITaskType.SUMMARIZATION,
      AITaskType.TRANSLATION,
      AITaskType.HEALTH_ANALYSIS,
      AITaskType.TCM_DIAGNOSIS,
      AITaskType.IMAGE_CLASSIFICATION
    ],
    [LLMModelType.CLAUDE_3_OPUS]: [
      AITaskType.TEXT_GENERATION,
      AITaskType.QUESTION_ANSWERING,
      AITaskType.SUMMARIZATION,
      AITaskType.TRANSLATION,
      AITaskType.HEALTH_ANALYSIS
    ],
    [LLMModelType.CLAUDE_3_SONNET]: [
      AITaskType.TEXT_GENERATION,
      AITaskType.QUESTION_ANSWERING,
      AITaskType.SUMMARIZATION,
      AITaskType.TRANSLATION,
      AITaskType.HEALTH_ANALYSIS
    ],
    [LLMModelType.CLAUDE_3_HAIKU]: [
      AITaskType.TEXT_GENERATION,
      AITaskType.QUESTION_ANSWERING,
      AITaskType.SUMMARIZATION
    ],
    [LLMModelType.GEMINI_PRO]: [
      AITaskType.TEXT_GENERATION,
      AITaskType.QUESTION_ANSWERING,
      AITaskType.TRANSLATION
    ],
    [LLMModelType.GEMINI_ULTRA]: [
      AITaskType.TEXT_GENERATION,
      AITaskType.QUESTION_ANSWERING,
      AITaskType.TRANSLATION,
      AITaskType.HEALTH_ANALYSIS
    ],
    [LLMModelType.LLAMA_3_70B]: [
      AITaskType.TEXT_GENERATION,
      AITaskType.QUESTION_ANSWERING,
      AITaskType.TCM_DIAGNOSIS
    ],
    [LLMModelType.LLAMA_3_8B]: [
      AITaskType.TEXT_GENERATION,
      AITaskType.QUESTION_ANSWERING
    ],
    [LLMModelType.QWEN_72B]: [
      AITaskType.TEXT_GENERATION,
      AITaskType.QUESTION_ANSWERING,
      AITaskType.TCM_DIAGNOSIS,
      AITaskType.TRANSLATION
    ],
    [LLMModelType.BAICHUAN_13B]: [
      AITaskType.TEXT_GENERATION,
      AITaskType.QUESTION_ANSWERING,
      AITaskType.TCM_DIAGNOSIS
    ]
  };

  return modelCapabilities[modelType]?.includes(taskType) || false;
}

/**
 * 计算AI响应的质量分数
 */
export function calculateResponseQuality(response: AIResponse): number {
  let score = 0;

  // 基础成功分数
  if (response.success) {
    score += 50;
  }

  // 响应时间分数（越快越好）
  if (response.metadata?.processingTime) {
    const timeScore = Math.max(0, 30 - (response.metadata.processingTime / 1000));
    score += timeScore;
  }

  // 置信度分数
  if (response.metadata?.confidence) {
    score += response.metadata.confidence * 20;
  }

  return Math.min(100, Math.max(0, score));
}

/**
 * 格式化AI响应用于显示
 */
export function formatAIResponse(response: AIResponse): string {
  if (!response.success) {
    return `错误: ${response.error}`;
  }

  let formatted = response.data || '';

  // 添加元数据信息
  if (response.metadata) {
    const metadata = response.metadata;
    const metaInfo = [];

    if (metadata.modelUsed) {
      metaInfo.push(`模型: ${metadata.modelUsed}`);
    }

    if (metadata.processingTime) {
      metaInfo.push(`处理时间: ${metadata.processingTime}ms`);
    }

    if (metadata.confidence) {
      metaInfo.push(`置信度: ${(metadata.confidence * 100).toFixed(1)}%`);
    }

    if (metaInfo.length > 0) {
      formatted += `\n\n---\n${metaInfo.join(' | ')}`;
    }
  }

  return formatted;
}

/**
 * 创建健康分析提示词
 */
export function createHealthAnalysisPrompt(
  symptoms: string[],
  age: number,
  gender: 'male' | 'female',
  analysisType: 'tcm' | 'western' | 'integrated'
): string {
  const basePrompt = `
请作为专业的健康分析专家，分析以下患者信息：

患者基本信息：
- 年龄：${age}岁
- 性别：${gender === 'male' ? '男性' : '女性'}
- 主要症状：${symptoms.join('、')}

分析要求：
`;

  switch (analysisType) {
    case 'tcm':
      return basePrompt + `
请从中医角度进行分析，包括：
1. 辨证分析（寒热虚实、脏腑经络）
2. 体质判断
3. 病因病机
4. 治疗原则
5. 方药建议
6. 生活调理建议

请用专业但易懂的语言回答。`;

    case 'western':
      return basePrompt + `
请从现代医学角度进行分析，包括：
1. 可能的疾病诊断
2. 建议的检查项目
3. 治疗方案
4. 预防措施
5. 生活方式建议

请用专业但易懂的语言回答。`;

    case 'integrated':
      return basePrompt + `
请结合中西医两种医学体系进行综合分析，包括：
1. 现代医学可能诊断
2. 中医辨证分析
3. 中西医结合治疗建议
4. 预防和调理方案
5. 生活方式指导

请用专业但易懂的语言回答。`;

    default:
      return basePrompt + '请进行综合健康分析。';
  }
}

/**
 * 解析健康分析结果
 */
export function parseHealthAnalysisResult(result: string): {
  diagnosis: string[];
  recommendations: string[];
  riskFactors: string[];
  followUpActions: string[];
} {
  const lines = result.split('\n').filter(line => line.trim());
  
  const diagnosis: string[] = [];
  const recommendations: string[] = [];
  const riskFactors: string[] = [];
  const followUpActions: string[] = [];

  let currentSection = '';

  for (const line of lines) {
    const trimmedLine = line.trim();
    
    if (trimmedLine.includes('诊断') || trimmedLine.includes('可能')) {
      currentSection = 'diagnosis';
      continue;
    } else if (trimmedLine.includes('建议') || trimmedLine.includes('治疗')) {
      currentSection = 'recommendations';
      continue;
    } else if (trimmedLine.includes('风险') || trimmedLine.includes('注意')) {
      currentSection = 'riskFactors';
      continue;
    } else if (trimmedLine.includes('随访') || trimmedLine.includes('复查')) {
      currentSection = 'followUpActions';
      continue;
    }

    if (trimmedLine.startsWith('-') || trimmedLine.match(/^\d+\./)) {
      const content = trimmedLine.replace(/^[-\d.]\s*/, '');
      
      switch (currentSection) {
        case 'diagnosis':
          diagnosis.push(content);
          break;
        case 'recommendations':
          recommendations.push(content);
          break;
        case 'riskFactors':
          riskFactors.push(content);
          break;
        case 'followUpActions':
          followUpActions.push(content);
          break;
      }
    }
  }

  return {
    diagnosis,
    recommendations,
    riskFactors,
    followUpActions
  };
}

/**
 * 生成AI请求的唯一ID
 */
export function generateRequestId(): string {
  return `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 检查API密钥格式
 */
export function validateApiKey(apiKey: string, provider: string): boolean {
  const patterns: Record<string, RegExp> = {
    openai: /^sk-[A-Za-z0-9]{48}$/,
    anthropic: /^sk-ant-[A-Za-z0-9-]{95}$/,
    google: /^[A-Za-z0-9_-]{39}$/
  };

  const pattern = patterns[provider.toLowerCase()];
  return pattern ? pattern.test(apiKey) : apiKey.length > 10;
}

/**
 * 安全地记录AI请求（移除敏感信息）
 */
export function sanitizeRequestForLogging(request: AIRequest): Partial<AIRequest> {
  return {
    taskType: request.taskType,
    input: typeof request.input === 'string' 
      ? request.input.substring(0, 100) + (request.input.length > 100 ? '...' : '')
      : '[Binary Data]',
    modelConfig: {
      modelType: request.modelConfig?.modelType,
      maxTokens: request.modelConfig?.maxTokens,
      temperature: request.modelConfig?.temperature
    }
  };
}

/**
 * 计算成本估算（基于token使用）
 */
export function estimateCost(modelType: LLMModelType, tokensUsed: number): number {
  // 简化的成本计算（实际应该基于最新的定价）
  const costPerToken: Record<LLMModelType, number> = {
    [LLMModelType.GPT4]: 0.00003,
    [LLMModelType.GPT4_TURBO]: 0.00001,
    [LLMModelType.GPT4O]: 0.000005,
    [LLMModelType.CLAUDE_3_OPUS]: 0.000015,
    [LLMModelType.CLAUDE_3_SONNET]: 0.000003,
    [LLMModelType.CLAUDE_3_HAIKU]: 0.00000025,
    [LLMModelType.GEMINI_PRO]: 0.0000005,
    [LLMModelType.GEMINI_ULTRA]: 0.000001,
    [LLMModelType.LLAMA_3_70B]: 0, // 本地模型
    [LLMModelType.LLAMA_3_8B]: 0,
    [LLMModelType.QWEN_72B]: 0,
    [LLMModelType.BAICHUAN_13B]: 0
  };

  return (costPerToken[modelType] || 0) * tokensUsed;
} 