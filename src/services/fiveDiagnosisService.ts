import { unifiedApiService } from './unifiedApiService';
// 五诊数据类型定义
export interface LookDiagnosisData {
  faceImage?: string;
  tongueImage?: string;
  eyeImages?: string[];
  skinImages?: string[];
  metadata?: {
    timestamp: number;
    lighting?: string;
    cameraInfo?: any;
};
}
export interface ListenDiagnosisData {
  voiceRecording?: string;
  breathingSound?: string;
  coughSound?: string;
  heartSound?: string;
  metadata?: {
    timestamp: number;
  duration: number;
    quality?: string;
};
}
export interface InquiryDiagnosisData {
  symptoms: string[];
  medicalHistory?: string[];
  currentMedications?: string[];
  lifestyle?: {
    diet?: string;
    exercise?: string;
    sleep?: string;
    stress?: string;
};
  chiefComplaint?: string;
  presentIllness?: string;
  familyHistory?: string[];
}
export interface PalpationDiagnosisData {
  pulseData?: {
    rate?: number;
    rhythm?: string;
    strength?: string;
    quality?: string;
};
  abdominalPalpation?: {
    tenderness?: string[];
    masses?: string[];
    organomegaly?: string[];
  };
  skinPalpation?: {
    temperature?: string;
    moisture?: string;
    texture?: string;
  };
}
export interface CalculationDiagnosisData {
  personalInfo: {;
  birthYear: number;
    birthMonth: number;
  birthDay: number;
    birthHour: number;
  gender: string;
    location?: string;
};
  analysisTypes: {
    ziwuLiuzhu?: boolean;
    constitution?: boolean;
    bagua?: boolean;
    wuyunLiuqi?: boolean;
    comprehensive?: boolean;
  };
  currentTime?: string;
  healthConcerns?: string[];
}
export interface FiveDiagnosisInput {
  userId: string;
  sessionId?: string;
  lookingData?: LookDiagnosisData;
  listeningData?: ListenDiagnosisData;
  inquiryData?: InquiryDiagnosisData;
  palpationData?: PalpationDiagnosisData;
  calculationData?: CalculationDiagnosisData;
  preferences?: {
    language?: string;
    detailLevel?: 'basic' | 'detailed' | 'comprehensive';
    focusAreas?: string[];
};
}
export interface DiagnosisResult {
  type: 'look' | 'listen' | 'inquiry' | 'palpation' | 'calculation';
  confidence: number;
  findings: string[];
  recommendations: string[];
  tcmSyndrome?: string;
  constitution?: string;
  severity?: 'low' | 'medium' | 'high';
  timestamp: number;
}
export interface FiveDiagnosisResult {
  sessionId: string;
  userId: string;
  timestamp: number;
  individualResults: {;
    look?: DiagnosisResult;
    listen?: DiagnosisResult;
    inquiry?: DiagnosisResult;
    palpation?: DiagnosisResult;
    calculation?: DiagnosisResult;
};
  comprehensiveAnalysis: {,
  overallAssessment: string;
    tcmSyndrome: string,
  constitution: string;
    healthRisk: 'low' | 'medium' | 'high',
  confidence: number;
    keyFindings: string[],
  recommendations: {
      immediate: string[],
  shortTerm: string[];
      longTerm: string[];
    };
    lifestyle: {
      diet?: string[];
      exercise?: string[];
      sleep?: string[];
      mentalHealth?: string[];
    };
    followUp?: {
      recommended: boolean;
      timeframe?: string;
      focus?: string[];
    };
  };
  metadata: {,
  processingTime: number;
    dataQuality: {
      look?: number;
      listen?: number;
      inquiry?: number;
      palpation?: number;
      calculation?: number;
    };
    version: string;
  };
}
export interface FiveDiagnosisError {
  code: string;
  message: string;
  details?: any;
  timestamp: number;
}
// 五诊服务类
class FiveDiagnosisService {
  private isInitialized = false;
  private sessionCache = new Map<string, any>();
  async initialize(): Promise<void> {
    try {
      // 检查所有五诊服务的健康状态
      const healthCheck = await unifiedApiService.getServiceHealth('diagnostic-services');
            if (healthCheck && typeof healthCheck.status === 'string' && healthCheck.status !== 'healthy') {
        throw new Error('五诊服务不可用');
      }
      this.isInitialized = true;
      console.log('五诊服务初始化成功');
    } catch (error) {
      console.error('五诊服务初始化失败:', error);
      throw error;
    }
  }
  // 执行单项诊断
  async performSingleDiagnosis(
    type: 'look' | 'listen' | 'inquiry' | 'palpation' | 'calculation',
    data: any;
  ): Promise<DiagnosisResult> {
    this.ensureInitialized();
    try {
      let result;
            switch (type) {
        case 'look':
          result = await unifiedApiService.performLookDiagnosis(data);
          break;
        case 'listen':
          result = await unifiedApiService.performListenDiagnosis(data);
          break;
        case 'inquiry':
          result = await unifiedApiService.performInquiryDiagnosis(data);
          break;
        case 'palpation':
          result = await unifiedApiService.performPalpationDiagnosis(data);
          break;
        case 'calculation':
          result = await unifiedApiService.performCalculationDiagnosis(data);
          break;
        default:
          throw new Error(`不支持的诊断类型: ${type}`);
      }
      return this.formatDiagnosisResult(type, result.data);
    } catch (error) {
      console.error(`${type}诊断失败:`, error);
      throw this.createError('DIAGNOSIS_FAILED', `${type}诊断失败`, error);
    }
  }
  // 执行算诊专项分析
  async performCalculationAnalysis(
    type: 'ziwu' | 'constitution' | 'bagua' | 'wuyun' | 'comprehensive',
    data: any;
  ): Promise<DiagnosisResult> {
    this.ensureInitialized();
    try {
      let result;
            switch (type) {
        case 'ziwu':
          result = await unifiedApiService.performZiwuAnalysis(data);
          break;
        case 'constitution':
          result = await unifiedApiService.performConstitutionAnalysis(data);
          break;
        case 'bagua':
          result = await unifiedApiService.performBaguaAnalysis(data);
          break;
        case 'wuyun':
          result = await unifiedApiService.performWuyunAnalysis(data);
          break;
        case 'comprehensive':
          result = await unifiedApiService.performCalculationComprehensive(data);
          break;
        default:
          throw new Error(`不支持的算诊类型: ${type}`);
      }
      return this.formatDiagnosisResult('calculation', result.data);
    } catch (error) {
      console.error(`算诊${type}分析失败:`, error);
      throw this.createError('CALCULATION_FAILED', `算诊${type}分析失败`, error);
    }
  }
  // 执行五诊综合分析
  async performComprehensiveDiagnosis(input: FiveDiagnosisInput): Promise<FiveDiagnosisResult> {
    this.ensureInitialized();
    const startTime = Date.now();
    const sessionId = input.sessionId || this.generateSessionId();
    try {
      // 缓存会话数据
      this.sessionCache.set(sessionId, input);
      // 并行执行各项诊断
      const diagnosticPromises: Promise<DiagnosisResult | null>[] = [];
      if (input.lookingData) {
        diagnosticPromises.push(
          this.performSingleDiagnosis('look', input.lookingData).catch() => null)
        );
      } else {
        diagnosticPromises.push(Promise.resolve(null));
      }
      if (input.listeningData) {
        diagnosticPromises.push(
          this.performSingleDiagnosis('listen', input.listeningData).catch() => null)
        );
      } else {
        diagnosticPromises.push(Promise.resolve(null));
      }
      if (input.inquiryData) {
        diagnosticPromises.push(
          this.performSingleDiagnosis('inquiry', input.inquiryData).catch() => null)
        );
      } else {
        diagnosticPromises.push(Promise.resolve(null));
      }
      if (input.palpationData) {
        diagnosticPromises.push(
          this.performSingleDiagnosis('palpation', input.palpationData).catch() => null)
        );
      } else {
        diagnosticPromises.push(Promise.resolve(null));
      }
      if (input.calculationData) {
        diagnosticPromises.push(
          this.performSingleDiagnosis('calculation', input.calculationData).catch() => null)
        );
      } else {
        diagnosticPromises.push(Promise.resolve(null));
      }
      // 等待所有诊断完成
      const [lookResult, listenResult, inquiryResult, palpationResult, calculationResult] =
        await Promise.all(diagnosticPromises);
      // 执行综合分析
      const comprehensiveResult = await unifiedApiService.performFiveDiagnosisComprehensive({
        lookData: input.lookingData,
        listenData: input.listeningData,
        inquiryData: input.inquiryData,
        palpationData: input.palpationData,
        calculationData: input.calculationData,
        userId: input.userId,
        sessionId,
      });
      const processingTime = Date.now() - startTime;
      // 构建最终结果
      const result: FiveDiagnosisResult = {
        sessionId,
        userId: input.userId,
        timestamp: Date.now(),
        individualResults: {
          ...(lookResult && { look: lookResult }),
          ...(listenResult && { listen: listenResult }),
          ...(inquiryResult && { inquiry: inquiryResult }),
          ...(palpationResult && { palpation: palpationResult }),
          ...(calculationResult && { calculation: calculationResult }),
        },
        comprehensiveAnalysis: comprehensiveResult.data,
        metadata: {
          processingTime,
          dataQuality: this.calculateDataQuality({,
  look: lookResult,
            listen: listenResult,
            inquiry: inquiryResult,
            palpation: palpationResult,
            calculation: calculationResult,
          }),
          version: '1.0.0',
        },
      };
      return result;
    } catch (error) {
      console.error('五诊综合分析失败:', error);
      throw this.createError("COMPREHENSIVE_DIAGNOSIS_FAILED",五诊综合分析失败', error);
    }
  }
  // 获取诊断历史
  async getDiagnosisHistory(userId?: string): Promise<FiveDiagnosisResult[]> {
    this.ensureInitialized();
    try {
      const result = await unifiedApiService.getDiagnosisHistory(userId);
      return result.data;
    } catch (error) {
      console.error('获取诊断历史失败:', error);
      throw this.createError("HISTORY_FETCH_FAILED",获取诊断历史失败', error);
    }
  }
  // 工具方法
  private ensureInitialized(): void {
    if (!this.isInitialized) {
      throw new Error('五诊服务未初始化，请先调用 initialize()');
    }
  }
  private generateSessionId(): string {
    return `five_diagnosis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  private formatDiagnosisResult(type: string, data: any): DiagnosisResult {
    return {
      type: type as any,
      confidence: data.confidence || 0.8,
      findings: data.findings || [],
      recommendations: data.recommendations || [],
      tcmSyndrome: data.tcmSyndrome,
      constitution: data.constitution,
      severity: data.severity || 'medium',
      timestamp: Date.now(),
    };
  }
  private calculateDataQuality(results: Record<string, DiagnosisResult | null>): Record<string, number> {
    const quality: Record<string, number> = {};
        Object.entries(results).forEach([key, result]) => {
      if (result) {
        quality[key] = result.confidence;
      }
    });
    return quality;
  }
  private createError(code: string, message: string, details?: any): FiveDiagnosisError {
    return {
      code,
      message,
      details,
      timestamp: Date.now(),
    };
  }
  // 清理会话缓存
  clearSessionCache(sessionId?: string): void {
    if (sessionId) {
      this.sessionCache.delete(sessionId);
    } else {
      this.sessionCache.clear();
    }
  }
  // 获取服务状态
  async getServiceStatus(): Promise<any> {
    try {
      return await unifiedApiService.getServiceHealth('diagnostic-services');
    } catch (error) {
      return {
      status: "error",
      error: error instanceof Error ? error.message : String(error) };
    }
  }
}
// 导出单例实例
export const fiveDiagnosisService = new FiveDiagnosisService();
// 类型已在上面定义并导出