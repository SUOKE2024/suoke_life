/**
 * 自定义 Jest 匹配器
 * 为 Agentic AI 测试提供专用的断言方法
 */

import { expect } from '@jest/globals';

// 扩展 Jest 匹配器类型
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeValidAgenticTask(): R;
      toBeValidWorkflowResult(): R;
      toBeValidReflectionResult(): R;
      toBeValidCollaborationResult(): R;
      toHaveQualityScore(min: number, max?: number): R;
      toHaveResponseTimeBelow(maxTime: number): R;
      toBeValidDiagnosis(): R;
      toBeValidTreatmentPlan(): R;
      toBeValidHealthPlan(): R;
      toHaveValidAgentContributions(): R;
      toBeWithinPerformanceThreshold(metric: string, threshold: number): R;
    }
  }
}

// 验证 Agentic 任务格式
expect.extend({
  toBeValidAgenticTask(received) {
    const pass = (
      received &&
      typeof received === 'object' &&
      typeof received.id === 'string' &&
      received.id.length > 0 &&
      typeof received.type === 'string' &&
      ['consultation', 'diagnosis', 'treatment', 'lifestyle', 'emergency', 'monitoring'].includes(received.type) &&
      typeof received.description === 'string' &&
      typeof received.priority === 'string' &&
      ['low', 'medium', 'high', 'urgent'].includes(received.priority) &&
      received.context &&
      typeof received.context === 'object' &&
      typeof received.context.userId === 'string' &&
      typeof received.context.sessionId === 'string' &&
      received.context.userProfile &&
      Array.isArray(received.requirements) &&
      typeof received.expectedOutcome === 'string'
    );

    return {
      message: () => 
        pass 
          ? `Expected ${JSON.stringify(received)} not to be a valid Agentic task`
          : `Expected ${JSON.stringify(received)} to be a valid Agentic task`,
      pass,
    };
  },
});

// 验证工作流结果格式
expect.extend({
  toBeValidWorkflowResult(received) {
    const pass = (
      received &&
      typeof received === 'object' &&
      typeof received.success === 'boolean' &&
      received.result !== undefined &&
      typeof received.qualityScore === 'number' &&
      received.qualityScore >= 0 &&
      received.qualityScore <= 1 &&
      typeof received.executionTime === 'number' &&
      received.executionTime > 0
    );

    return {
      message: () => 
        pass 
          ? `Expected ${JSON.stringify(received)} not to be a valid workflow result`
          : `Expected ${JSON.stringify(received)} to be a valid workflow result`,
      pass,
    };
  },
});

// 验证反思结果格式
expect.extend({
  toBeValidReflectionResult(received) {
    const pass = (
      received &&
      typeof received === 'object' &&
      typeof received.qualityScore === 'number' &&
      received.qualityScore >= 0 &&
      received.qualityScore <= 1 &&
      typeof received.confidence === 'number' &&
      received.confidence >= 0 &&
      received.confidence <= 1 &&
      Array.isArray(received.improvements) &&
      Array.isArray(received.nextActions) &&
      typeof received.shouldIterate === 'boolean'
    );

    return {
      message: () => 
        pass 
          ? `Expected ${JSON.stringify(received)} not to be a valid reflection result`
          : `Expected ${JSON.stringify(received)} to be a valid reflection result`,
      pass,
    };
  },
});

// 验证协作结果格式
expect.extend({
  toBeValidCollaborationResult(received) {
    const pass = (
      received &&
      typeof received === 'object' &&
      typeof received.success === 'boolean' &&
      received.agentContributions &&
      typeof received.agentContributions === 'object' &&
      typeof received.consensusScore === 'number' &&
      received.consensusScore >= 0 &&
      received.consensusScore <= 1 &&
      received.collaborationMetrics &&
      typeof received.collaborationMetrics === 'object'
    );

    return {
      message: () => 
        pass 
          ? `Expected ${JSON.stringify(received)} not to be a valid collaboration result`
          : `Expected ${JSON.stringify(received)} to be a valid collaboration result`,
      pass,
    };
  },
});

// 验证质量分数范围
expect.extend({
  toHaveQualityScore(received, min: number, max: number = 1) {
    const qualityScore = received?.qualityScore;
    const pass = (
      typeof qualityScore === 'number' &&
      qualityScore >= min &&
      qualityScore <= max
    );

    return {
      message: () => 
        pass 
          ? `Expected quality score ${qualityScore} not to be between ${min} and ${max}`
          : `Expected quality score ${qualityScore} to be between ${min} and ${max}`,
      pass,
    };
  },
});

// 验证响应时间
expect.extend({
  toHaveResponseTimeBelow(received, maxTime: number) {
    const responseTime = received?.responseTime || received?.executionTime;
    const pass = (
      typeof responseTime === 'number' &&
      responseTime < maxTime
    );

    return {
      message: () => 
        pass 
          ? `Expected response time ${responseTime}ms not to be below ${maxTime}ms`
          : `Expected response time ${responseTime}ms to be below ${maxTime}ms`,
      pass,
    };
  },
});

// 验证诊断结果格式
expect.extend({
  toBeValidDiagnosis(received) {
    const pass = (
      received &&
      typeof received === 'object' &&
      (received.syndrome || received.diagnosis) &&
      (received.constitution || received.condition) &&
      (received.severity || received.confidence) &&
      (received.evidence || received.symptoms || received.analysis)
    );

    return {
      message: () => 
        pass 
          ? `Expected ${JSON.stringify(received)} not to be a valid diagnosis`
          : `Expected ${JSON.stringify(received)} to be a valid diagnosis`,
      pass,
    };
  },
});

// 验证治疗方案格式
expect.extend({
  toBeValidTreatmentPlan(received) {
    const pass = (
      received &&
      typeof received === 'object' &&
      (received.prescription || received.treatment || received.recommendations) &&
      (received.dosage || received.instructions || received.duration)
    );

    return {
      message: () => 
        pass 
          ? `Expected ${JSON.stringify(received)} not to be a valid treatment plan`
          : `Expected ${JSON.stringify(received)} to be a valid treatment plan`,
      pass,
    };
  },
});

// 验证健康计划格式
expect.extend({
  toBeValidHealthPlan(received) {
    const pass = (
      received &&
      typeof received === 'object' &&
      (received.dailyRoutine || received.lifestyle || received.recommendations) &&
      (received.goals || received.targets || received.objectives)
    );

    return {
      message: () => 
        pass 
          ? `Expected ${JSON.stringify(received)} not to be a valid health plan`
          : `Expected ${JSON.stringify(received)} to be a valid health plan`,
      pass,
    };
  },
});

// 验证智能体贡献格式
expect.extend({
  toHaveValidAgentContributions(received) {
    const contributions = received?.agentContributions;
    const pass = (
      contributions &&
      typeof contributions === 'object' &&
      Object.keys(contributions).length > 0 &&
      Object.values(contributions).every(contribution => 
        contribution &&
        typeof contribution === 'object' &&
        (contribution.analysis || contribution.recommendation || contribution.result)
      )
    );

    return {
      message: () => 
        pass 
          ? `Expected agent contributions to be invalid`
          : `Expected valid agent contributions`,
      pass,
    };
  },
});

// 验证性能指标
expect.extend({
  toBeWithinPerformanceThreshold(received, metric: string, threshold: number) {
    const value = received?.[metric];
    const pass = (
      typeof value === 'number' &&
      value <= threshold
    );

    return {
      message: () => 
        pass 
          ? `Expected ${metric} ${value} not to be within threshold ${threshold}`
          : `Expected ${metric} ${value} to be within threshold ${threshold}`,
      pass,
    };
  },
});

// 辅助函数：创建性能断言
export const expectPerformance = (result: any) => ({
  toMeetResponseTimeTarget: (target: number) => {
    expect(result).toHaveResponseTimeBelow(target);
  },
  toMeetQualityTarget: (target: number) => {
    expect(result).toHaveQualityScore(target);
  },
  toMeetThroughputTarget: (target: number) => {
    expect(result).toBeWithinPerformanceThreshold('throughput', target);
  }
});

// 辅助函数：创建健康管理断言
export const expectHealthManagement = (result: any) => ({
  toHaveValidDiagnosis: () => {
    expect(result.diagnosis || result).toBeValidDiagnosis();
  },
  toHaveValidTreatment: () => {
    expect(result.treatmentPlan || result.treatment || result).toBeValidTreatmentPlan();
  },
  toHaveValidHealthPlan: () => {
    expect(result.healthPlan || result).toBeValidHealthPlan();
  },
  toHaveQualityAbove: (threshold: number) => {
    expect(result).toHaveQualityScore(threshold);
  }
});

// 辅助函数：创建协作断言
export const expectCollaboration = (result: any) => ({
  toHaveValidContributions: () => {
    expect(result).toHaveValidAgentContributions();
  },
  toHaveConsensusAbove: (threshold: number) => {
    expect(result.consensusScore).toBeGreaterThan(threshold);
  },
  toHaveKnowledgeSharingAbove: (threshold: number) => {
    expect(result.collaborationMetrics?.knowledgeSharing).toBeGreaterThan(threshold);
  }
});

// 辅助函数：创建系统集成断言
export const expectSystemIntegration = (result: any) => ({
  toHaveValidServiceStatus: () => {
    expect(result.serviceStatus).toBeDefined();
    expect(typeof result.serviceStatus).toBe('object');
  },
  toHaveValidDataFlow: () => {
    expect(result.dataFlowValidation?.isValid).toBe(true);
  },
  toHaveValidCommunication: () => {
    expect(result.communicationTest?.allPassed).toBe(true);
  }
});

// 辅助函数：验证五诊数据
export const expectFiveDiagnosis = (data: any) => ({
  toBeComplete: () => {
    expect(data.wang).toBeDefined();
    expect(data.wen).toBeDefined();
    expect(data.wen2).toBeDefined();
    expect(data.qie).toBeDefined();
    expect(data.suan).toBeDefined();
  },
  toHaveValidTongue: () => {
    expect(data.wang?.tongue).toBeDefined();
    expect(typeof data.wang.tongue.color).toBe('string');
    expect(typeof data.wang.tongue.coating).toBe('string');
  },
  toHaveValidPulse: () => {
    expect(data.qie?.pulse).toBeDefined();
    expect(typeof data.qie.pulse.position).toBe('string');
    expect(typeof data.qie.pulse.rate).toBe('string');
  }
});

// 导出所有自定义匹配器
export {
  expectPerformance,
  expectHealthManagement,
  expectCollaboration,
  expectSystemIntegration,
  expectFiveDiagnosis
};