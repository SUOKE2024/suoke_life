import { FiveDiagnosisEngine } from '../algorithms/FiveDiagnosisEngine';
import { AlgorithmConfig } from '../algorithms/config/AlgorithmConfig';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
import { apiClient } from './apiClient';

// 五诊数据接口
export interface FiveDiagnosisInput {
  userId: string;
  sessionId?: string;
  lookingData?: {
    tongueImage?: string;
    faceImage?: string;
    bodyImage?: string;
    metadata?: Record<string, any>;
  };
  listeningData?: {
    voiceRecording?: string;
    breathingPattern?: number[];
    coughSound?: string;
    metadata?: Record<string, any>;
  };
  inquiryData?: {
    symptoms: string[];,
  medicalHistory: string[];,
  lifestyle: Record<string, any>;
    familyHistory?: string[];
    metadata?: Record<string, any>;
  };
  palpationData?: {
    pulseData?: number[];
    touchData?: Record<string, any>;
    temperatureData?: number[];
    pressureData?: number[];
    metadata?: Record<string, any>;
  };
  calculationData?: {
    birthDate: string;
    birthTime?: string;
    location?: string;
    currentTime?: string;
    metadata?: Record<string, any>;
  };
}

// 五诊结果接口
export interface FiveDiagnosisResult {
  sessionId: string;,
  userId: string;,
  timestamp: string;,
  overallConfidence: number;,
  primarySyndrome: {,
  name: string;,
  confidence: number;,
  description: string;
  };
  constitutionType: {,
  type: string;,
  characteristics: string[];,
  recommendations: string[];
  };
  diagnosticResults: {
    looking?: any;
    listening?: any;
    inquiry?: any;
    palpation?: any;
    calculation?: any;
  };
  fusionAnalysis: {,
  evidenceStrength: Record<string, number>;
    syndromePatterns: any[];,
  riskFactors: string[];
  };
  healthRecommendations: {,
  lifestyle: string[];,
  diet: string[];,
  exercise: string[];,
  treatment: string[];,
  prevention: string[];
  };
  qualityMetrics: {,
  dataQuality: number;,
  resultReliability: number;,
  completeness: number;
  };
}

// 五诊服务状态
export interface FiveDiagnosisServiceStatus {
  isInitialized: boolean;,
  isProcessing: boolean;
  lastError?: string;
  performanceMetrics: {,
  averageResponseTime: number;,
  successRate: number;,
  totalSessions: number;
  };
}

// API配置
const DIAGNOSIS_API_CONFIG = {
  calculation: {,
  baseUrl: 'http://localhost:8003',
    timeout: 30000;
  },
  look: {,
  baseUrl: "http://localhost:8080",
    timeout: 30000;
  },
  listen: {,
  baseUrl: "http://localhost:8000",
    timeout: 30000;
  },
  inquiry: {,
  baseUrl: "http://localhost:8001",
    timeout: 30000;
  },
  palpation: {,
  baseUrl: "http://localhost:8002",
    timeout: 30000;
  }
};

// 错误处理类
export class FiveDiagnosisError extends Error {
  constructor(
    message: string,
    public code?: string,
    public service?: string,
    public retryable: boolean = false;
  ) {
    super(message);
    this.name = 'FiveDiagnosisError';
  }
}

// 数据验证器
class DiagnosisDataValidator {
  static validateInput(input: FiveDiagnosisInput): void {
    if (!input.userId) {
      throw new FiveDiagnosisError("用户ID不能为空", "INVALID_USER_ID");
    }
    
    // 至少需要一种诊断数据
    const hasData =
      input.lookingData ||
      input.listeningData ||
      input.inquiryData ||
      input.palpationData ||
      input.calculationData;
      
    if (!hasData) {
      throw new FiveDiagnosisError("至少需要提供一种诊断数据", "NO_DIAGNOSIS_DATA");
    }
  }

  static validateLookingData(data: any): void {
    if (data && !data.faceImage && !data.tongueImage) {
      throw new FiveDiagnosisError("望诊需要面部或舌部图像", "INVALID_LOOKING_DATA");
    }
  }

  static validateListeningData(data: any): void {
    if (data && !data.voiceRecording) {
      throw new FiveDiagnosisError("闻诊需要语音录音", "INVALID_LISTENING_DATA");
    }
  }

  static validateInquiryData(data: any): void {
    if (data && (!data.symptoms || data.symptoms.length === 0)) {
      throw new FiveDiagnosisError("问诊需要症状信息", "INVALID_INQUIRY_DATA");
    }
  }

  static validatePalpationData(data: any): void {
    if (data && !data.pulseData) {
      throw new FiveDiagnosisError("切诊需要脉象数据", "INVALID_PALPATION_DATA");
    }
  }

  static validateCalculationData(data: any): void {
    if (data && !data.birthDate) {
      throw new FiveDiagnosisError("算诊需要出生日期", "INVALID_CALCULATION_DATA");
    }
  }
}

// 五诊算法系统前端服务类
export class FiveDiagnosisService {
  private engine: FiveDiagnosisEngine;
  private config: AlgorithmConfig;
  private isInitialized: boolean = false;
  private processingQueue: Map<string, Promise<FiveDiagnosisResult>> = new Map();
  private performanceMetrics = {
    averageResponseTime: 0,
    successRate: 0,
    totalSessions: 0,
    successfulSessions: 0,
    responseTimes: [] as number[]
  };

  constructor() {
    this.config = new AlgorithmConfig();
    this.engine = new FiveDiagnosisEngine(this.config);
  }

  // 初始化五诊服务
  async initialize(): Promise<void> {
    try {
      // 等待算法引擎初始化完成
      await this.waitForEngineReady();
      
      // 加载配置
      await this.loadConfiguration();
      
      // 验证系统状态
      await this.validateSystemStatus();
      
      this.isInitialized = true;
    } catch (error) {
      throw new FiveDiagnosisError(`五诊服务初始化失败: ${error}`, 'INIT_FAILED');
    }
  }

  // 执行五诊分析
  async performDiagnosis(input: FiveDiagnosisInput): Promise<FiveDiagnosisResult> {
    if (!this.isInitialized) {
      throw new FiveDiagnosisError("服务未初始化", "SERVICE_NOT_INITIALIZED");
    }

    // 验证输入数据
    DiagnosisDataValidator.validateInput(input);

    const sessionId = input.sessionId || this.generateSessionId();
    const startTime = Date.now();

    try {
      // 检查是否已在处理中
      if (this.processingQueue.has(sessionId)) {
        return await this.processingQueue.get(sessionId)!;
      }

      // 创建处理Promise;
      const processingPromise = this.executeComprehensiveDiagnosis(input, sessionId);
      this.processingQueue.set(sessionId, processingPromise);

      const result = await processingPromise;
      
      // 更新性能指标
      this.updatePerformanceMetrics(Date.now() - startTime, true);
      
      // 保存结果
      await this.saveDiagnosisResult(result);
      
      return result;
    } catch (error) {
      this.updatePerformanceMetrics(Date.now() - startTime, false);
      throw error;
    } finally {
      this.processingQueue.delete(sessionId);
    }
  }

  // 获取诊断历史
  async getDiagnosisHistory(userId: string, limit: number = 10): Promise<FiveDiagnosisResult[]> {
    try {
      const response = await apiClient.get(`/diagnosis/history/${userId}?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw new FiveDiagnosisError(`获取诊断历史失败: ${error}`, 'HISTORY_FETCH_FAILED');
    }
  }

  // 保存诊断结果
  async saveDiagnosisResult(result: FiveDiagnosisResult): Promise<void> {
    try {
      await apiClient.post('/diagnosis/save', result);
    } catch (error) {
      console.error('保存诊断结果失败:', error);
      // 不抛出错误，避免影响主流程
    }
  }

  // 获取个性化建议
  async getPersonalizedRecommendations(userId: string): Promise<any> {
    try {
      const response = await apiClient.get(`/diagnosis/recommendations/${userId}`);
      return response.data;
    } catch (error) {
      throw new FiveDiagnosisError(`获取个性化建议失败: ${error}`, 'RECOMMENDATIONS_FETCH_FAILED');
    }
  }

  // 等待引擎就绪
  private async waitForEngineReady(): Promise<void> {
    return new Promise(resolve) => {
      const checkReady = () => {
        if (this.engine && this.engine.isReady()) {
          resolve();
        } else {
          setTimeout(checkReady, 100);
        }
      };
      checkReady();
    });
  }

  // 加载配置
  private async loadConfiguration(): Promise<void> {
    try {
      // 加载算法配置
      await this.config.loadFromRemote();
      
      // 更新引擎配置
      this.engine.updateConfig(this.config);
    } catch (error) {
      console.warn('加载远程配置失败，使用默认配置:', error);
    }
  }

  // 验证系统状态
  private async validateSystemStatus(): Promise<void> {
    const services = Object.keys(DIAGNOSIS_API_CONFIG);
    const healthChecks = services.map(async (service) => {
      try {
        const config = DIAGNOSIS_API_CONFIG[service as keyof typeof DIAGNOSIS_API_CONFIG];
        const response = await fetch(`${config.baseUrl}/health`, {
          method: 'GET',
          timeout: 5000;
        } as any);
        return { service, status: response.ok ? 'healthy' : 'unhealthy' };
      } catch (error) {
        return { service, status: 'unhealthy', error };
      }
    });

    const results = await Promise.all(healthChecks);
    const unhealthyServices = results.filter(r => r.status === 'unhealthy');
    
    if (unhealthyServices.length > 0) {
      console.warn('部分诊断服务不可用:', unhealthyServices);
    }
  }

  // 执行综合诊断
  private async executeComprehensiveDiagnosis(
    input: FiveDiagnosisInput,
    sessionId: string;
  ): Promise<FiveDiagnosisResult> {
    const diagnosticResults: any = {};
    const promises: Promise<any>[] = [];

    // 望诊
    if (input.lookingData) {
      DiagnosisDataValidator.validateLookingData(input.lookingData);
      promises.push(
        this.performLookingDiagnosis(input.lookingData)
          .then(result => { diagnosticResults.looking = result; })
          .catch(error => { diagnosticResults.looking = { error: error.message }; })
      );
    }

    // 闻诊
    if (input.listeningData) {
      DiagnosisDataValidator.validateListeningData(input.listeningData);
      promises.push(
        this.performListeningDiagnosis(input.listeningData)
          .then(result => { diagnosticResults.listening = result; })
          .catch(error => { diagnosticResults.listening = { error: error.message }; })
      );
    }

    // 问诊
    if (input.inquiryData) {
      DiagnosisDataValidator.validateInquiryData(input.inquiryData);
      promises.push(
        this.performInquiryDiagnosis(input.inquiryData)
          .then(result => { diagnosticResults.inquiry = result; })
          .catch(error => { diagnosticResults.inquiry = { error: error.message }; })
      );
    }

    // 切诊
    if (input.palpationData) {
      DiagnosisDataValidator.validatePalpationData(input.palpationData);
      promises.push(
        this.performPalpationDiagnosis(input.palpationData)
          .then(result => { diagnosticResults.palpation = result; })
          .catch(error => { diagnosticResults.palpation = { error: error.message }; })
      );
    }

    // 算诊
    if (input.calculationData) {
      DiagnosisDataValidator.validateCalculationData(input.calculationData);
      promises.push(
        this.performCalculationDiagnosis(input.calculationData)
          .then(result => { diagnosticResults.calculation = result; })
          .catch(error => { diagnosticResults.calculation = { error: error.message }; })
      );
    }

    // 等待所有诊断完成
    await Promise.all(promises);

    // 执行综合分析
    const comprehensiveResult = await this.performComprehensiveAnalysis({
      userId: input.userId,
      sessionId,
      diagnosticResults;
    });

    return comprehensiveResult;
  }

  // 望诊分析
  private async performLookingDiagnosis(data: any): Promise<any> {
    try {
      const response = await fetch(`${DIAGNOSIS_API_CONFIG.look.baseUrl}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        timeout: DIAGNOSIS_API_CONFIG.look.timeout;
      } as any);
      
      if (!response.ok) {
        throw new Error(`望诊服务错误: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      throw new FiveDiagnosisError(`望诊分析失败: ${error}`, 'LOOKING_ANALYSIS_FAILED', 'look', true);
    }
  }

  // 闻诊分析
  private async performListeningDiagnosis(data: any): Promise<any> {
    try {
      const response = await fetch(`${DIAGNOSIS_API_CONFIG.listen.baseUrl}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        timeout: DIAGNOSIS_API_CONFIG.listen.timeout;
      } as any);
      
      if (!response.ok) {
        throw new Error(`闻诊服务错误: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      throw new FiveDiagnosisError(`闻诊分析失败: ${error}`, 'LISTENING_ANALYSIS_FAILED', 'listen', true);
    }
  }

  // 问诊分析
  private async performInquiryDiagnosis(data: any): Promise<any> {
    try {
      const response = await fetch(`${DIAGNOSIS_API_CONFIG.inquiry.baseUrl}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        timeout: DIAGNOSIS_API_CONFIG.inquiry.timeout;
      } as any);
      
      if (!response.ok) {
        throw new Error(`问诊服务错误: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      throw new FiveDiagnosisError(`问诊分析失败: ${error}`, 'INQUIRY_ANALYSIS_FAILED', 'inquiry', true);
    }
  }

  // 切诊分析
  private async performPalpationDiagnosis(data: any): Promise<any> {
    try {
      const response = await fetch(`${DIAGNOSIS_API_CONFIG.palpation.baseUrl}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        timeout: DIAGNOSIS_API_CONFIG.palpation.timeout;
      } as any);
      
      if (!response.ok) {
        throw new Error(`切诊服务错误: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      throw new FiveDiagnosisError(`切诊分析失败: ${error}`, 'PALPATION_ANALYSIS_FAILED', 'palpation', true);
    }
  }

  // 算诊分析
  private async performCalculationDiagnosis(data: any): Promise<any> {
    try {
      const response = await fetch(`${DIAGNOSIS_API_CONFIG.calculation.baseUrl}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        timeout: DIAGNOSIS_API_CONFIG.calculation.timeout;
      } as any);
      
      if (!response.ok) {
        throw new Error(`算诊服务错误: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      throw new FiveDiagnosisError(`算诊分析失败: ${error}`, 'CALCULATION_ANALYSIS_FAILED', 'calculation', true);
    }
  }

  // 综合分析
  private async performComprehensiveAnalysis(params: {,
  userId: string;,
  sessionId: string;,
  diagnosticResults: any;
  }): Promise<FiveDiagnosisResult> {
    try {
      // 使用算法引擎进行综合分析
      const fusionResult = await this.engine.performFusionAnalysis(params.diagnosticResults);
      
      return {
        sessionId: params.sessionId,
        userId: params.userId,
        timestamp: new Date().toISOString(),
        overallConfidence: fusionResult.confidence || 0.8,
        primarySyndrome: fusionResult.primarySyndrome || {,
  name: "待进一步分析",
          confidence: 0.5,
          description: "需要更多诊断数据"
        },
        constitutionType: fusionResult.constitutionType || {,
  type: "平和质",
          characteristics: ["体质平衡"],
          recommendations: ["保持现有生活方式"]
        },
        diagnosticResults: params.diagnosticResults,
        fusionAnalysis: fusionResult.fusionAnalysis || {,
  evidenceStrength: {},
          syndromePatterns: [],
          riskFactors: []
        },
        healthRecommendations: fusionResult.recommendations || {,
  lifestyle: ["规律作息"],
          diet: ["均衡饮食"],
          exercise: ["适量运动"],
          treatment: ["定期检查"],
          prevention: ["预防为主"]
        },
        qualityMetrics: {,
  dataQuality: this.calculateDataQuality(params.diagnosticResults),
          resultReliability: fusionResult.confidence || 0.8,
          completeness: this.calculateCompleteness(params.diagnosticResults)
        }
      };
    } catch (error) {
      throw new FiveDiagnosisError(`综合分析失败: ${error}`, 'COMPREHENSIVE_ANALYSIS_FAILED');
    }
  }

  // 计算数据质量
  private calculateDataQuality(diagnosticResults: any): number {
    let totalQuality = 0;
    let count = 0;

    Object.values(diagnosticResults).forEach(result: any) => {
      if (result && typeof result.confidence === 'number') {
        totalQuality += result.confidence;
        count++;
      }
    });

    return count > 0 ? totalQuality / count : 0.5;
  }

  // 计算完整性
  private calculateCompleteness(diagnosticResults: any): number {
    const totalMethods = 5; // 五诊方法
    const completedMethods = Object.keys(diagnosticResults).filter(
      key => diagnosticResults[key] && !diagnosticResults[key].error;
    ).length;
    
    return completedMethods / totalMethods;
  }

  // 更新性能指标
  private updatePerformanceMetrics(responseTime: number, success: boolean): void {
    this.performanceMetrics.totalSessions++;
    if (success) {
      this.performanceMetrics.successfulSessions++;
    }
    
    this.performanceMetrics.responseTimes.push(responseTime);
    if (this.performanceMetrics.responseTimes.length > 100) {
      this.performanceMetrics.responseTimes.shift();
    }
    
    this.performanceMetrics.averageResponseTime = 
      this.performanceMetrics.responseTimes.reduce(a, b) => a + b, 0) / 
      this.performanceMetrics.responseTimes.length;
      
    this.performanceMetrics.successRate = 
      this.performanceMetrics.successfulSessions / this.performanceMetrics.totalSessions;
  }

  // 生成会话ID;
  private generateSessionId(): string {
    return `diagnosis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // 获取服务状态
  getStatus(): FiveDiagnosisServiceStatus {
    return {
      isInitialized: this.isInitialized,
      isProcessing: this.processingQueue.size > 0,
      performanceMetrics: {,
  averageResponseTime: this.performanceMetrics.averageResponseTime,
        successRate: this.performanceMetrics.successRate,
        totalSessions: this.performanceMetrics.totalSessions;
      }
    };
  }

  // 清理资源
  async cleanup(): Promise<void> {
    // 等待所有处理完成
    await Promise.all(Array.from(this.processingQueue.values()));
    
    // 清理引擎
    if (this.engine) {
      await this.engine.cleanup();
    }
    
    this.isInitialized = false;
  }
}

// 创建单例实例
export const fiveDiagnosisService = new FiveDiagnosisService();

// React Hook;
export const useFiveDiagnosis = () => {
  const performanceMonitor = usePerformanceMonitor();
  
  return {
    service: fiveDiagnosisService,
    performanceMonitor,
    
    // 便捷方法
    diagnose: async (input: FiveDiagnosisInput) => {
      const startTime = Date.now();
      try {
        const result = await fiveDiagnosisService.performDiagnosis(input);
        performanceMonitor.recordMetric('diagnosis_success', Date.now() - startTime);
        return result;
      } catch (error) {
        performanceMonitor.recordMetric('diagnosis_error', Date.now() - startTime);
        throw error;
      }
    },
    
    getHistory: (userId: string, limit?: number) => 
      fiveDiagnosisService.getDiagnosisHistory(userId, limit),
      
    getRecommendations: (userId: string) => 
      fiveDiagnosisService.getPersonalizedRecommendations(userId),
      
    getStatus: () => fiveDiagnosisService.getStatus()
  };
};
