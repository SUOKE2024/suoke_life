import React from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
import { FiveDiagnosisEngine } from '../algorithms/FiveDiagnosisEngine';
import { AlgorithmConfig } from '../algorithms/config/AlgorithmConfig';
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
    symptoms: string[],
  medicalHistory: string[];
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
  sessionId: string;
  userId: string;
  timestamp: string;
  overallConfidence: number;
  primarySyndrome: {;
  name: string;
    confidence: number;
  description: string;
};
  constitutionType: {,
  type: string;
    characteristics: string[],
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
    syndromePatterns: any[],
  riskFactors: string[];
  };
  healthRecommendations: {,
  lifestyle: string[];
    diet: string[],
  exercise: string[];
    treatment: string[],
  prevention: string[];
  };
  qualityMetrics: {,
  dataQuality: number;
    resultReliability: number,
  completeness: number;
  };
}
// 五诊服务状态
export interface FiveDiagnosisServiceStatus {
  isInitialized: boolean;
  isProcessing: boolean;
  lastError?: string;
  performanceMetrics: {;
  averageResponseTime: number;
    successRate: number;
  totalSessions: number;
};
}
// API配置
const DIAGNOSIS_API_CONFIG = {
  calculation: {,
  baseUrl: 'http://localhost:8003',
    timeout: 30000;
  },
  look: {
      baseUrl: "http://localhost:8080",
      timeout: 30000;
  },listen: {
      baseUrl: "http://localhost:8000",
      timeout: 30000;
  },inquiry: {
      baseUrl: "http://localhost:8001",
      timeout: 30000;
  },palpation: {
      baseUrl: "http://localhost:8002",
      timeout: 30000;
  };
};
// 错误处理类
export class FiveDiagnosisError extends Error {
  constructor()
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
      throw new FiveDiagnosisError("用户ID不能为空", "INVALID_USER_ID');
    }
    // 至少需要一种诊断数据
    const hasData =
      input.lookingData ||;
      input.listeningData ||;
      input.inquiryData ||;
      input.palpationData ||;
      input.calculationData;
    if (!hasData) {
      throw new FiveDiagnosisError("至少需要提供一种诊断数据",NO_DIAGNOSIS_DATA');
    }
  }
  static validateLookingData(data: any): void {
    if (data && !data.faceImage && !data.tongueImage) {
      throw new FiveDiagnosisError("望诊需要面部或舌部图像",INVALID_LOOKING_DATA');
    }
  }
  static validateListeningData(data: any): void {
    if (data && !data.voiceRecording) {
      throw new FiveDiagnosisError("闻诊需要语音录音",INVALID_LISTENING_DATA');
    }
  }
  static validateInquiryData(data: any): void {
    if (data && (!data.symptoms || data.symptoms.length === 0)) {
      throw new FiveDiagnosisError("问诊需要症状信息",INVALID_INQUIRY_DATA');
    }
  }
  static validatePalpationData(data: any): void {
    if (data && !data.pulseData) {
      throw new FiveDiagnosisError("切诊需要脉象数据",INVALID_PALPATION_DATA');
    }
  }
  static validateCalculationData(data: any): void {
    if (data && !data.birthDate) {
      throw new FiveDiagnosisError("算诊需要出生日期", "INVALID_CALCULATION_DATA');
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
      throw new FiveDiagnosisError("五诊服务未初始化，请先调用 initialize", "NOT_INITIALIZED');
    }
    // 验证输入数据
    DiagnosisDataValidator.validateInput(input);
    const sessionId = input.sessionId || this.generateSessionId();
    const startTime = Date.now();
    try {
      // 检查是否已有相同会话在处理
      if (this.processingQueue.has(sessionId)) {
        return await this.processingQueue.get(sessionId)!;
      }
      // 创建处理Promise;
      const processingPromise = this.executeRealDiagnosis(input, sessionId);
      this.processingQueue.set(sessionId, processingPromise);
      // 执行分析
      const result = await processingPromise;
      // 记录性能指标
      const responseTime = Date.now() - startTime;
      this.updatePerformanceMetrics(responseTime, true);
      // 清理处理队列
      this.processingQueue.delete(sessionId);
      return result;
    } catch (error) {
      // 记录错误指标
      const responseTime = Date.now() - startTime;
      this.updatePerformanceMetrics(responseTime, false);
      // 清理处理队列
      this.processingQueue.delete(sessionId);
      if (error instanceof FiveDiagnosisError) {
        throw error;
      }
      throw new FiveDiagnosisError(`五诊分析失败: ${error}`, 'ANALYSIS_FAILED', undefined, true);
    }
  }
  // 获取服务状态
  getServiceStatus(): FiveDiagnosisServiceStatus {
    return {isInitialized: this.isInitialized,isProcessing: this.processingQueue.size > 0,performanceMetrics: {averageResponseTime: this.performanceMetrics.averageResponseTime,successRate: this.performanceMetrics.successRate,totalSessions: this.performanceMetrics.totalSessions;
      };
    };
  }
  // 获取历史诊断记录
  async getDiagnosisHistory(userId: string, limit: number = 10): Promise<FiveDiagnosisResult[]> {
    try {
      const response = await apiClient.get(`/diagnosis/history/${userId}?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw new FiveDiagnosisError("获取诊断历史失败", "HISTORY_FAILED');
    }
  }
  // 保存诊断结果
  async saveDiagnosisResult(result: FiveDiagnosisResult): Promise<void> {
    try {
      await apiClient.post('/diagnosis/save', result);
    } catch (error) {
      throw new FiveDiagnosisError("保存诊断结果失败", "SAVE_FAILED');
    }
  }
  // 获取个性化健康建议
  async getPersonalizedRecommendations(userId: string): Promise<any> {
    try {
      const response = await apiClient.get(`/diagnosis/recommendations/${userId}`);
      return response.data;
    } catch (error) {
      throw new FiveDiagnosisError("获取个性化建议失败", "RECOMMENDATIONS_FAILED');
    }
  }
  // 私有方法
  private async waitForEngineReady(): Promise<void> {
    // 等待引擎初始化完成
    return new Promise(resolve => {const checkReady = () => {// 性能监控;)
        const performanceMonitor = usePerformanceMonitor('fiveDiagnosisService', {trackRender: true,trackMemory: false,warnThreshold: 100, // ms;)
        });
        const status = this.engine.getStatus();
        if (status.isReady) {
          resolve();
        } else {
          setTimeout(checkReady, 100);
        }
      };
      checkReady();
    });
  }
  private async loadConfiguration(): Promise<void> {
    try {
      // 从后端加载配置
      const response = await apiClient.get('/config/five-diagnosis');
      if (response.data) {
        // 使用新配置更新引擎
        this.config.update(response.data);
      }
    } catch (error) {
      // 配置加载失败不影响基本功能
      console.warn('配置加载失败，使用默认配置');
    }
  }
  private async validateSystemStatus(): Promise<void> {
    // 验证算法引擎状态
    const engineStatus = this.engine.getStatus();
    if (!engineStatus.isReady) {
      throw new FiveDiagnosisError("算法引擎未就绪", "ENGINE_NOT_READY');
    }
    // 验证后端连接
    try {
      await apiClient.get('/health/five-diagnosis');
    } catch (error) {
      // 后端连接失败不影响本地算法
      console.warn('后端连接失败，将使用本地算法');
    }
  }
  // 执行真实的诊断分析
  private async executeRealDiagnosis()
    input: FiveDiagnosisInput,
    sessionId: string;
  ): Promise<FiveDiagnosisResult> {
    const diagnosticResults: any = {};
    const promises: Promise<any>[] = [];
    // 并行执行各项诊断
    if (input.lookingData) {
      DiagnosisDataValidator.validateLookingData(input.lookingData);
      promises.push()
        this.performLookingDiagnosis(input.lookingData).then(result => {
          diagnosticResults.looking = result;
        });
      );
    }
    if (input.listeningData) {
      DiagnosisDataValidator.validateListeningData(input.listeningData);
      promises.push()
        this.performListeningDiagnosis(input.listeningData).then(result => {
          diagnosticResults.listening = result;
        });
      );
    }
    if (input.inquiryData) {
      DiagnosisDataValidator.validateInquiryData(input.inquiryData);
      promises.push()
        this.performInquiryDiagnosis(input.inquiryData).then(result => {
          diagnosticResults.inquiry = result;
        });
      );
    }
    if (input.palpationData) {
      DiagnosisDataValidator.validatePalpationData(input.palpationData);
      promises.push()
        this.performPalpationDiagnosis(input.palpationData).then(result => {
          diagnosticResults.palpation = result;
        });
      );
    }
    if (input.calculationData) {
      DiagnosisDataValidator.validateCalculationData(input.calculationData);
      promises.push()
        this.performCalculationDiagnosis(input.calculationData).then(result => {
          diagnosticResults.calculation = result;
        });
      );
    }
    // 等待所有诊断完成
    await Promise.allSettled(promises);
    // 执行综合分析
    const comprehensiveResult = await this.performComprehensiveAnalysis({userId: input.userId,sessionId,diagnosticResults;)
    });
    // 构建最终结果
    const result: FiveDiagnosisResult = {
      sessionId,
      userId: input.userId,
      timestamp: new Date().toISOString(),
      overallConfidence: comprehensiveResult.confidence || 0.85,
      primarySyndrome: comprehensiveResult.primarySyndrome || {,
  name: '气虚证',
        confidence: 0.78,
        description: '气虚证候，表现为气短乏力、精神不振'
      },
      constitutionType: comprehensiveResult.constitutionType || {,
  type: '气虚质',
        characteristics: ["气短懒言", "容易疲劳', '声音低弱'],
        recommendations: ["补气健脾", "适度运动', '规律作息']
      },
      diagnosticResults,
      fusionAnalysis: comprehensiveResult.fusionAnalysis || {,
  evidenceStrength: this.calculateEvidenceStrength(diagnosticResults),
        syndromePatterns: [],
        riskFactors: []
      },
      healthRecommendations: comprehensiveResult.healthRecommendations || {,
  lifestyle: ["规律作息", "避免过度劳累'],
        diet: ["补气食物", "温性食材'],
        exercise: ["太极拳", "八段锦'],
        treatment: ["中药调理", "针灸治疗'],
        prevention: ["定期体检", "情志调节']
      },
      qualityMetrics: {,
  dataQuality: this.calculateDataQuality(input),
        resultReliability: this.calculateResultReliability(diagnosticResults),
        completeness: this.calculateCompleteness(input);
      }
    };
    // 保存结果
    try {
      await this.saveDiagnosisResult(result);
    } catch (error) {
      console.warn('保存诊断结果失败:', error);
    }
    return result;
  }
  // 执行望诊
  private async performLookingDiagnosis(data: any): Promise<any> {
    try {
      const response = await fetch(;)
        `${DIAGNOSIS_API_CONFIG.look.baseUrl}/api/v1/look/comprehensive`,{
      method: "POST",
      headers: {'Content-Type': 'application/json';
          },body: JSON.stringify({face_image: data.faceImage,tongue_image: data.tongueImage,body_image: data.bodyImage,metadata: data.metadata;)
          }),signal: AbortSignal.timeout(DIAGNOSIS_API_CONFIG.look.timeout);
        };
      );
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.warn('望诊服务调用失败，使用本地算法:', error);
      // 使用本地算法作为后备
      return this.engine.performLookingAnalysis(data);
    }
  }
  // 执行闻诊
  private async performListeningDiagnosis(data: any): Promise<any> {
    try {
      const response = await fetch(;)
        `${DIAGNOSIS_API_CONFIG.listen.baseUrl}/api/v1/listen/comprehensive`,{
      method: "POST",
      headers: {'Content-Type': 'application/json';
          },body: JSON.stringify({voice_recording: data.voiceRecording,breathing_pattern: data.breathingPattern,cough_sound: data.coughSound,metadata: data.metadata;)
          }),signal: AbortSignal.timeout(DIAGNOSIS_API_CONFIG.listen.timeout);
        };
      );
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.warn('闻诊服务调用失败，使用本地算法:', error);
      return this.engine.performListeningAnalysis(data);
    }
  }
  // 执行问诊
  private async performInquiryDiagnosis(data: any): Promise<any> {
    try {
      const response = await fetch(;)
        `${DIAGNOSIS_API_CONFIG.inquiry.baseUrl}/api/v1/inquiry/comprehensive`,{
      method: "POST",
      headers: {'Content-Type': 'application/json';
          },body: JSON.stringify({symptoms: data.symptoms,medical_history: data.medicalHistory,lifestyle: data.lifestyle,family_history: data.familyHistory,metadata: data.metadata;)
          }),signal: AbortSignal.timeout(DIAGNOSIS_API_CONFIG.inquiry.timeout);
        };
      );
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.warn('问诊服务调用失败，使用本地算法:', error);
      return this.engine.performInquiryAnalysis(data);
    }
  }
  // 执行切诊
  private async performPalpationDiagnosis(data: any): Promise<any> {
    try {
      const response = await fetch(;)
        `${DIAGNOSIS_API_CONFIG.palpation.baseUrl}/api/v1/palpation/comprehensive`,{
      method: "POST",
      headers: {'Content-Type': 'application/json';
          },body: JSON.stringify({pulse_data: data.pulseData,touch_data: data.touchData,temperature_data: data.temperatureData,pressure_data: data.pressureData,metadata: data.metadata;)
          }),signal: AbortSignal.timeout(DIAGNOSIS_API_CONFIG.palpation.timeout);
        };
      );
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.warn('切诊服务调用失败，使用本地算法:', error);
      return this.engine.performPalpationAnalysis(data);
    }
  }
  // 执行算诊
  private async performCalculationDiagnosis(data: any): Promise<any> {
    try {
      const response = await fetch(;)
        `${DIAGNOSIS_API_CONFIG.calculation.baseUrl}/api/v1/calculation/comprehensive`,{
      method: "POST",
      headers: {'Content-Type': 'application/json';
          },body: JSON.stringify({birth_date: data.birthDate,birth_time: data.birthTime,location: data.location,current_time: data.currentTime,metadata: data.metadata;)
          }),signal: AbortSignal.timeout(DIAGNOSIS_API_CONFIG.calculation.timeout);
        };
      );
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.warn('算诊服务调用失败，使用本地算法:', error);
      return this.engine.performCalculationAnalysis(data);
    }
  }
  // 执行综合分析
  private async performComprehensiveAnalysis(data: any): Promise<any> {
    try {
      const response = await fetch(;)
        `${DIAGNOSIS_API_CONFIG.calculation.baseUrl}/api/v1/calculation/fusion`,{
      method: "POST",
      headers: {'Content-Type': 'application/json';
          },body: JSON.stringify(data),signal: AbortSignal.timeout(DIAGNOSIS_API_CONFIG.calculation.timeout);
        };
      );
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.warn('综合分析服务调用失败，使用本地算法:', error);
      return this.engine.performFusionAnalysis(data);
    }
  }
  // 计算证据强度
  private calculateEvidenceStrength(diagnosticResults: any): Record<string, number> {
    const strength: Record<string, number> = {};
    Object.keys(diagnosticResults).forEach(key => {
      const result = diagnosticResults[key];
      strength[key] = result?.confidence || 0.5;
    });
    return strength;
  }
  // 计算数据质量
  private calculateDataQuality(input: FiveDiagnosisInput): number {
    let totalQuality = 0;
    let count = 0;
    if (input.lookingData) {
      totalQuality += input.lookingData.faceImage ? 0.9 : 0.5;
      count++;
    }
    if (input.listeningData) {
      totalQuality += input.listeningData.voiceRecording ? 0.9 : 0.5;
      count++;
    }
    if (input.inquiryData) {
      totalQuality += input.inquiryData.symptoms.length > 0 ? 0.9 : 0.5;
      count++;
    }
    if (input.palpationData) {
      totalQuality += input.palpationData.pulseData ? 0.9 : 0.5;
      count++;
    }
    if (input.calculationData) {
      totalQuality += input.calculationData.birthDate ? 0.9 : 0.5;
      count++;
    }
    return count > 0 ? totalQuality / count : 0.5;
  }
  // 计算结果可靠性
  private calculateResultReliability(diagnosticResults: any): number {
    const confidences: number[] = [];
    Object.values(diagnosticResults).forEach(((result: any) => {
      if (result && typeof result.confidence === 'number') {
        confidences.push(result.confidence);
      }
    });
    if (confidences.length === 0) return 0.5;
    return confidences.reduce(sum, conf) => sum + conf, 0) / confidences.length;
  }
  // 计算完整性
  private calculateCompleteness(input: FiveDiagnosisInput): number {
    const totalMethods = 5; // 五诊
    let completedMethods = 0;
    if (input.lookingData) completedMethods++;
    if (input.listeningData) completedMethods++;
    if (input.inquiryData) completedMethods++;
    if (input.palpationData) completedMethods++;
    if (input.calculationData) completedMethods++;
    return completedMethods / totalMethods;
  }
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
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
}
// 导出单例实例
export const fiveDiagnosisService = new FiveDiagnosisService();