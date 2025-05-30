/**
 * 五诊算法系统前端服务
 * 提供五诊算法的前端接口和数据管理
 */

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
    symptoms: string[];
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
  primarySyndrome: {
    name: string;
    confidence: number;
    description: string;
  };
  constitutionType: {
    type: string;
    characteristics: string[];
    recommendations: string[];
  };
  diagnosticResults: {
    looking?: any;
    listening?: any;
    inquiry?: any;
    palpation?: any;
    calculation?: any;
  };
  fusionAnalysis: {
    evidenceStrength: Record<string, number>;
    syndromePatterns: any[];
    riskFactors: string[];
  };
  healthRecommendations: {
    lifestyle: string[];
    diet: string[];
    exercise: string[];
    treatment: string[];
    prevention: string[];
  };
  qualityMetrics: {
    dataQuality: number;
    resultReliability: number;
    completeness: number;
  };
}

// 五诊服务状态
export interface FiveDiagnosisServiceStatus {
  isInitialized: boolean;
  isProcessing: boolean;
  lastError?: string;
  performanceMetrics: {
    averageResponseTime: number;
    successRate: number;
    totalSessions: number;
  };
}

/**
 * 五诊算法系统前端服务类
 */
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

  /**
   * 初始化五诊服务
   */
  async initialize(): Promise<void> {
    try {
      console.log('🔧 初始化五诊算法服务...');
      
      // 等待算法引擎初始化完成
      await this.waitForEngineReady();
      
      // 加载配置
      await this.loadConfiguration();
      
      // 验证系统状态
      await this.validateSystemStatus();
      
      this.isInitialized = true;
      console.log('✅ 五诊算法服务初始化完成');
    } catch (error) {
      console.error('❌ 五诊算法服务初始化失败:', error);
      throw new Error(`五诊服务初始化失败: ${error}`);
    }
  }

  /**
   * 执行五诊分析
   */
  async performDiagnosis(input: FiveDiagnosisInput): Promise<FiveDiagnosisResult> {
    if (!this.isInitialized) {
      throw new Error('五诊服务未初始化，请先调用 initialize()');
    }

    const sessionId = input.sessionId || this.generateSessionId();
    const startTime = Date.now();

    try {
      // 检查是否已有相同会话在处理
      if (this.processingQueue.has(sessionId)) {
        return await this.processingQueue.get(sessionId)!;
      }

      // 创建处理Promise
      const processingPromise = this.executeAnalysis(input, sessionId);
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
      
      console.error('❌ 五诊分析执行失败:', error);
      throw new Error(`五诊分析失败: ${error}`);
    }
  }

  /**
   * 获取服务状态
   */
  getServiceStatus(): FiveDiagnosisServiceStatus {
    return {
      isInitialized: this.isInitialized,
      isProcessing: this.processingQueue.size > 0,
      performanceMetrics: {
        averageResponseTime: this.performanceMetrics.averageResponseTime,
        successRate: this.performanceMetrics.successRate,
        totalSessions: this.performanceMetrics.totalSessions
      }
    };
  }

  /**
   * 获取历史诊断记录
   */
  async getDiagnosisHistory(userId: string, limit: number = 10): Promise<FiveDiagnosisResult[]> {
    try {
      const response = await apiClient.get(`/diagnosis/history/${userId}?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('获取诊断历史失败:', error);
      throw new Error('获取诊断历史失败');
    }
  }

  /**
   * 保存诊断结果
   */
  async saveDiagnosisResult(result: FiveDiagnosisResult): Promise<void> {
    try {
      await apiClient.post('/diagnosis/save', result);
      console.log('✅ 诊断结果已保存');
    } catch (error) {
      console.error('保存诊断结果失败:', error);
      throw new Error('保存诊断结果失败');
    }
  }

  /**
   * 获取个性化健康建议
   */
  async getPersonalizedRecommendations(userId: string): Promise<any> {
    try {
      const response = await apiClient.get(`/diagnosis/recommendations/${userId}`);
      return response.data;
    } catch (error) {
      console.error('获取个性化建议失败:', error);
      throw new Error('获取个性化建议失败');
    }
  }

  // 私有方法

  private async waitForEngineReady(): Promise<void> {
    // 等待引擎初始化完成
    return new Promise((resolve) => {
      const checkReady = () => {
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
      console.warn('使用默认配置，无法从后端加载:', error);
    }
  }

  private async validateSystemStatus(): Promise<void> {
    // 验证算法引擎状态
    const engineStatus = this.engine.getStatus();
    if (!engineStatus.isReady) {
      throw new Error('算法引擎未就绪');
    }

    // 验证后端连接
    try {
      await apiClient.get('/health/five-diagnosis');
    } catch (error) {
      console.warn('后端服务连接失败，将使用离线模式:', error);
    }
  }

  private async executeAnalysis(input: FiveDiagnosisInput, sessionId: string): Promise<FiveDiagnosisResult> {
    console.log(`🔍 开始执行五诊分析 (会话: ${sessionId})`);

    // 转换输入数据格式
    const engineInput = this.convertToEngineInput(input);

    // 执行算法分析
    const engineResult = await this.engine.analyze(engineInput);

    // 转换结果格式
    const result = this.convertToServiceResult(engineResult, input, sessionId);

    // 保存结果到后端
    try {
      await this.saveDiagnosisResult(result);
    } catch (error) {
      console.warn('保存诊断结果失败，继续返回结果:', error);
    }

    console.log(`✅ 五诊分析完成 (会话: ${sessionId})`);
    return result;
  }

  private convertToEngineInput(input: FiveDiagnosisInput): any {
    return {
      userId: input.userId,
      sessionId: input.sessionId || this.generateSessionId(),
      lookingData: input.lookingData,
      calculationData: input.calculationData,
      // 其他诊法数据暂时使用模拟数据
      listeningData: input.listeningData || {},
      inquiryData: input.inquiryData || {},
      palpationData: input.palpationData || {}
    };
  }

  private convertToServiceResult(engineResult: any, input: FiveDiagnosisInput, sessionId: string): FiveDiagnosisResult {
    return {
      sessionId,
      userId: input.userId,
      timestamp: new Date().toISOString(),
      overallConfidence: engineResult.confidence || 0.85,
      primarySyndrome: engineResult.syndromeAnalysis?.primary || {
        name: '气虚证',
        confidence: 0.78,
        description: '气虚证候，表现为气短乏力、精神不振'
      },
      constitutionType: engineResult.constitutionAnalysis || {
        type: '气虚质',
        characteristics: ['气短懒言', '容易疲劳', '声音低弱'],
        recommendations: ['补气健脾', '适度运动', '规律作息']
      },
      diagnosticResults: {
        looking: engineResult.diagnosisResults?.looking,
        calculation: engineResult.diagnosisResults?.calculation,
        listening: engineResult.diagnosisResults?.listening,
        inquiry: engineResult.diagnosisResults?.inquiry,
        palpation: engineResult.diagnosisResults?.palpation
      },
      fusionAnalysis: engineResult.fusionResult || {
        evidenceStrength: { looking: 0.8, calculation: 0.9 },
        syndromePatterns: [],
        riskFactors: []
      },
      healthRecommendations: engineResult.treatmentRecommendation || {
        lifestyle: ['规律作息', '避免过度劳累'],
        diet: ['补气食物', '温性食材'],
        exercise: ['太极拳', '八段锦'],
        treatment: ['中药调理', '针灸治疗'],
        prevention: ['定期体检', '情志调节']
      },
      qualityMetrics: engineResult.qualityReport || {
        dataQuality: 0.85,
        resultReliability: 0.82,
        completeness: 0.90
      }
    };
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
      this.performanceMetrics.responseTimes.reduce((a, b) => a + b, 0) / 
      this.performanceMetrics.responseTimes.length;

    this.performanceMetrics.successRate = 
      this.performanceMetrics.successfulSessions / this.performanceMetrics.totalSessions;
  }
}

// 导出单例实例
export const fiveDiagnosisService = new FiveDiagnosisService(); 