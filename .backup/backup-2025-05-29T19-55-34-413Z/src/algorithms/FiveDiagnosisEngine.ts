import { AlgorithmConfig } from "./config/AlgorithmConfig";
import { TCMKnowledgeBase } from "./knowledge/TCMKnowledgeBase";
import { QualityController } from "./quality/QualityController";
import { PerformanceMonitor } from "./monitoring/PerformanceMonitor";
import {
import {
import {
import {
import {
import {

  CalculationDiagnosisAlgorithm,
  CalculationData as CalcData,
  CalculationResult as CalcResult,
} from "./modules/CalculationDiagnosisAlgorithm";
  LookingDiagnosisAlgorithm,
  LookingData as LookData,
  LookingResult as LookResult,
} from "./modules/LookingDiagnosisAlgorithm";
  ListeningDiagnosisAlgorithm,
  ListeningData as ListenData,
  ListeningResult as ListenResult,
} from "./modules/ListeningDiagnosisAlgorithm";
  InquiryDiagnosisAlgorithm,
  InquiryData as InqData,
  InquiryResult as InqResult,
} from "./modules/InquiryDiagnosisAlgorithm";
  PalpationDiagnosisAlgorithm,
  PalpationData as PalpData,
  PalpationResult as PalpResult,
} from "./modules/PalpationDiagnosisAlgorithm";
  DiagnosisFusionAlgorithm,
  FusionInput,
  FusionResult,
} from "./modules/DiagnosisFusionAlgorithm";

/**
 * 中医五诊算法引擎
 *
 * 整合望、闻、问、切、算五种诊法的核心引擎
 * 提供完整的中医诊断分析能力
 *
 * @author 索克生活技术团队
 * @version 1.0.0
 */

// 基础类型定义
export interface UserProfile {
  age: number;
  gender: "male" | "female" | "other";
  height: number;
  weight: number;
  occupation: string;
  medicalHistory: string[];
  allergies: string[];
  medications: string[];
}

export interface DiagnosisInput {
  userProfile?: UserProfile;
  lookingData?: LookData;
  listeningData?: ListenData;
  inquiryData?: InqData;
  palpationData?: PalpData;
  calculationData?: CalcData;
  timestamp?: number;
  sessionId: string;
  userId: string;
}

export interface ImageData {
  data: ArrayBuffer;
  format: string;
  width: number;
  height: number;
}

export interface SessionContext {
  sessionId: string;
  timestamp: number;
  environment: {
    temperature: number;
    humidity: number;
    season: string;
    timeOfDay: string;
  };
  previousSessions?: string[];
}

export interface DiagnosisResult {
  sessionId: string;
  userId: string;
  timestamp: number;
  confidence: number;
  overallAssessment: string;
  diagnosisResults: {
    looking?: LookingResult;
    calculation?: CalculationResult;
  };
  fusionResult: FusionResult;
  syndromeAnalysis: any;
  constitutionAnalysis: any;
  treatmentRecommendation: any;
  qualityReport: any;
  performanceMetrics: any;
}

export interface LookingResult {
  confidence: number;
  features: any[];
  analysis: string;
}

export interface CalculationResult {
  confidence: number;
  fiveElements: any;
  analysis: string;
}

export interface LocalFusionResult {
  confidence: number;
  fusedFeatures: any[];
  analysis: string;
}

export enum DiagnosisType {
  LOOKING = "looking",
  LISTENING = "listening",
  INQUIRY = "inquiry",
  PALPATION = "palpation",
  CALCULATION = "calculation",
}

export enum ProcessingStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

/**
 * 中医五诊算法核心引擎
 */
export class FiveDiagnosisEngine {
  private config: AlgorithmConfig;
  private knowledgeBase: TCMKnowledgeBase;
  private qualityController: QualityController;
  private performanceMonitor: PerformanceMonitor;

  // 运行时状态
  private isInitialized: boolean = false;
  private sessionCount: number = 0;
  private lastMaintenanceTime: number = Date.now();
  private eventListeners: Map<string, Function[]> = new Map();

  // 算法模块
  private calculationAlgorithm!: CalculationDiagnosisAlgorithm;
  private lookingAlgorithm!: LookingDiagnosisAlgorithm;
  private listeningAlgorithm!: ListeningDiagnosisAlgorithm;
  private inquiryAlgorithm!: InquiryDiagnosisAlgorithm;
  private palpationAlgorithm!: PalpationDiagnosisAlgorithm;
  private fusionAlgorithm!: DiagnosisFusionAlgorithm;

  constructor(config?: Partial<AlgorithmConfig>) {
    // 初始化配置
    this.config = new AlgorithmConfig(config);

    // 初始化知识库
    this.knowledgeBase = new TCMKnowledgeBase(this.config.knowledgeBase);

    // 初始化质量控制器
    this.qualityController = new QualityController(this.config.qualityControl);

    // 初始化性能监控器
    this.performanceMonitor = new PerformanceMonitor(this.config.monitoring);

    this.initializeEngine();
  }

  /**
   * 初始化引擎
   */
  private async initializeEngine(): Promise<void> {
    try {
      this.emit("engine:initializing");

      // 等待知识库加载完成
      await this.waitForKnowledgeBase();

      this.isInitialized = true;
      this.emit("engine:initialized");

      // 初始化算法模块
      this.initializeAlgorithms();
    } catch (error) {
      this.emit("engine:initialization_failed", { error });
      throw error;
    }
  }

  /**
   * 等待知识库加载完成
   */
  private async waitForKnowledgeBase(): Promise<void> {
    // 简化实现，实际应该等待知识库加载完成
    return new Promise((resolve) => setTimeout(resolve, 100));
  }

  /**
   * 初始化算法模块
   */
  private initializeAlgorithms(): void {
    try {
      // 初始化各诊法算法
      this.calculationAlgorithm = new CalculationDiagnosisAlgorithm(
        this.config.calculation,
        this.knowledgeBase
      );

      this.lookingAlgorithm = new LookingDiagnosisAlgorithm(
        this.config.looking,
        this.knowledgeBase
      );

      this.listeningAlgorithm = new ListeningDiagnosisAlgorithm(
        this.config.listening,
        this.knowledgeBase
      );

      this.inquiryAlgorithm = new InquiryDiagnosisAlgorithm(
        this.config.inquiry,
        this.knowledgeBase
      );

      this.palpationAlgorithm = new PalpationDiagnosisAlgorithm(
        this.config.palpation,
        this.knowledgeBase
      );

      this.fusionAlgorithm = new DiagnosisFusionAlgorithm(
        this.config.fusion,
        this.knowledgeBase
      );

      this.emit("algorithms:initialized", {
        algorithms: [
          "calculation",
          "looking",
          "listening",
          "inquiry",
          "palpation",
          "fusion",
        ],
      });
    } catch (error) {
      this.emit("algorithms:error", { error, stage: "initialization" });
      throw new Error(`算法模块初始化失败: ${error}`);
    }
  }

  /**
   * 执行五诊分析
   */
  public async analyze(input: DiagnosisInput): Promise<DiagnosisResult> {
    if (!this.isInitialized) {
      throw new Error("引擎尚未初始化完成");
    }

    const sessionId = input.sessionId;
    const startTime = Date.now();

    try {
      this.sessionCount++;
      this.emit("diagnosis:started", { sessionId, userId: input.userId });

      // 数据验证
      await this.validateInput(input);

      // 数据标准化
      await this.normalizeInput(input);

      // 执行各诊法分析
      const diagnosisResults: any = {};

      // 望诊分析
      if (input.lookingData) {
        this.emit("algorithm:progress", {
          stage: "looking_analysis",
          progress: 0.3,
        });
        diagnosisResults.looking = await this.lookingAlgorithm.analyze(
          input.lookingData,
          input.userProfile
        );
      }

      // 闻诊分析
      if (input.listeningData) {
        this.emit("algorithm:progress", {
          stage: "listening_analysis",
          progress: 0.4,
        });
        diagnosisResults.listening = await this.listeningAlgorithm.analyze(
          input.listeningData,
          input.userProfile
        );
      }

      // 问诊分析
      if (input.inquiryData) {
        this.emit("algorithm:progress", {
          stage: "inquiry_analysis",
          progress: 0.5,
        });
        diagnosisResults.inquiry = await this.inquiryAlgorithm.analyze(
          input.inquiryData,
          input.userProfile
        );
      }

      // 切诊分析
      if (input.palpationData) {
        this.emit("algorithm:progress", {
          stage: "palpation_analysis",
          progress: 0.6,
        });
        diagnosisResults.palpation = await this.palpationAlgorithm.analyze(
          input.palpationData,
          input.userProfile
        );
      }

      // 算诊分析
      if (input.calculationData) {
        this.emit("algorithm:progress", {
          stage: "calculation_analysis",
          progress: 0.7,
        });
        diagnosisResults.calculation = await this.calculationAlgorithm.analyze(
          input.calculationData,
          input.userProfile
        );
      }

      // 执行融合分析
      const fusionResult = await this.performFusionAnalysis(
        diagnosisResults,
        input
      );

      // 执行辨证分析
      const syndromeAnalysis = await this.performSyndromeAnalysis(fusionResult);

      // 执行体质分析
      const constitutionAnalysis = await this.performConstitutionAnalysis(
        fusionResult,
        input.userProfile
      );

      // 生成治疗建议
      const treatmentRecommendation =
        await this.generateTreatmentRecommendation(
          syndromeAnalysis,
          constitutionAnalysis,
          input.userProfile
        );

      // 质量控制
      const qualityReport = await this.qualityController.validate({
        input,
        diagnosisResults,
        fusionResult,
        syndromeAnalysis,
        constitutionAnalysis,
        treatmentRecommendation,
      });

      // 性能监控
      const responseTime = Date.now() - startTime;
      this.performanceMonitor.recordResponseTime(
        responseTime,
        "full_diagnosis"
      );

      // 计算整体置信度
      const confidence = this.calculateOverallConfidence(
        diagnosisResults,
        fusionResult,
        qualityReport
      );

      // 生成综合评估
      const overallAssessment = await this.generateOverallAssessment(
        diagnosisResults,
        fusionResult,
        syndromeAnalysis,
        constitutionAnalysis
      );

      const result: DiagnosisResult = {
        sessionId,
        userId: input.userId,
        timestamp: Date.now(),
        confidence,
        overallAssessment,
        diagnosisResults,
        fusionResult,
        syndromeAnalysis,
        constitutionAnalysis,
        treatmentRecommendation,
        qualityReport,
        performanceMetrics: this.performanceMonitor.getMetrics(),
      };

      this.sessionCount--;
      this.emit("diagnosis:completed", { sessionId, result });

      return result;
    } catch (error) {
      this.sessionCount--;
      this.emit("diagnosis:failed", { sessionId, error });
      throw error;
    }
  }

  /**
   * 验证输入数据
   */
  private async validateInput(input: DiagnosisInput): Promise<void> {
    if (!input.sessionId) {
      throw new Error("缺少会话ID");
    }

    if (!input.userId) {
      throw new Error("缺少用户ID");
    }

    // 检查是否至少有一种诊法数据
    const hasData = !!(input.lookingData || input.calculationData);

    if (!hasData) {
      throw new Error("至少需要提供一种诊法的数据");
    }

    // 验证图像数据格式
    if (input.lookingData?.tongueImage) {
      await this.validateImageData(input.lookingData.tongueImage, "tongue");
    }

    // 验证计算数据格式
    if (input.calculationData) {
      await this.validateCalculationData(input.calculationData);
    }
  }

  /**
   * 标准化输入数据
   */
  private async normalizeInput(input: DiagnosisInput): Promise<void> {
    // 标准化图像数据
    if (input.lookingData) {
      await this.normalizeLookingData(input.lookingData);
    }

    // 标准化计算数据
    if (input.calculationData) {
      await this.normalizeCalculationData(input.calculationData);
    }
  }

  /**
   * 执行融合分析
   */
  private async performFusionAnalysis(
    diagnosisResults: any,
    input: DiagnosisInput
  ): Promise<FusionResult> {
    // 使用融合算法模块
    const fusionInput: FusionInput = {
      lookingResult: diagnosisResults.looking,
      listeningResult: diagnosisResults.listening,
      inquiryResult: diagnosisResults.inquiry,
      palpationResult: diagnosisResults.palpation,
      calculationResult: diagnosisResults.calculation,
      userProfile: input.userProfile,
    };

    return await this.fusionAlgorithm.analyze(fusionInput);
  }

  /**
   * 执行辨证分析
   */
  private async performSyndromeAnalysis(
    fusionResult: FusionResult
  ): Promise<any> {
    // 简化实现
    return {
      primarySyndrome: "气虚证",
      confidence: 0.7,
      analysis: "基于融合结果的辨证分析",
    };
  }

  /**
   * 执行体质分析
   */
  private async performConstitutionAnalysis(
    fusionResult: FusionResult,
    userProfile?: UserProfile
  ): Promise<any> {
    // 简化实现
    return {
      primaryType: "平和质",
      confidence: 0.8,
      analysis: "体质分析结果",
    };
  }

  /**
   * 生成治疗建议
   */
  private async generateTreatmentRecommendation(
    syndromeAnalysis: any,
    constitutionAnalysis: any,
    userProfile?: UserProfile
  ): Promise<any> {
    // 简化实现
    return {
      treatments: ["四君子汤"],
      lifestyle: ["规律作息", "适度运动"],
      diet: ["健脾益气食物"],
      analysis: "基于辨证和体质的治疗建议",
    };
  }

  /**
   * 计算整体置信度
   */
  private calculateOverallConfidence(
    diagnosisResults: any,
    fusionResult: FusionResult,
    qualityReport: any
  ): number {
    const weights = {
      looking: 0.4,
      calculation: 0.3,
      fusion: 0.2,
      quality: 0.1,
    };

    let totalWeight = 0;
    let weightedSum = 0;

    if (diagnosisResults.looking) {
      weightedSum += diagnosisResults.looking.confidence * weights.looking;
      totalWeight += weights.looking;
    }

    if (diagnosisResults.calculation) {
      weightedSum +=
        diagnosisResults.calculation.confidence * weights.calculation;
      totalWeight += weights.calculation;
    }

    weightedSum += fusionResult.confidence * weights.fusion;
    totalWeight += weights.fusion;

    if (qualityReport?.score) {
      weightedSum += qualityReport.score * weights.quality;
      totalWeight += weights.quality;
    }

    return totalWeight > 0 ? weightedSum / totalWeight : 0.5;
  }

  /**
   * 生成综合评估
   */
  private async generateOverallAssessment(
    diagnosisResults: any,
    fusionResult: FusionResult,
    syndromeAnalysis: any,
    constitutionAnalysis: any
  ): Promise<string> {
    const assessmentParts: string[] = [];

    if (syndromeAnalysis?.primarySyndrome) {
      assessmentParts.push(`主要证候：${syndromeAnalysis.primarySyndrome}`);
    }

    if (constitutionAnalysis?.primaryType) {
      assessmentParts.push(`体质类型：${constitutionAnalysis.primaryType}`);
    }

    assessmentParts.push(
      `综合置信度：${(fusionResult.confidence * 100).toFixed(1)}%`
    );

    return (
      assessmentParts.join("，") + "。建议结合专业医师意见进行进一步诊疗。"
    );
  }

  // 辅助方法
  private async validateImageData(
    imageData: ImageData,
    type: string
  ): Promise<void> {
    // 实现图像数据验证逻辑
  }

  private async validateCalculationData(calcData: CalcData): Promise<void> {
    // 实现计算数据验证逻辑
  }

  private async normalizeLookingData(data: LookData): Promise<void> {
    // 实现望诊数据标准化逻辑
  }

  private async normalizeCalculationData(data: CalcData): Promise<void> {
    // 实现计算数据标准化逻辑
  }

  /**
   * 获取引擎状态
   */
  public getStatus(): any {
    return {
      isRunning: this.isInitialized,
      sessionCount: this.sessionCount,
      algorithmVersion: this.config.version,
      knowledgeBaseVersion: "1.0.0",
      lastMaintenanceTime: this.lastMaintenanceTime,
    };
  }

  /**
   * 事件处理
   */
  public on(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(callback);
  }

  public emit(event: string, data?: any): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error(`事件处理错误 [${event}]:`, error);
        }
      });
    }
  }

  /**
   * 清理资源
   */
  public async cleanup(): Promise<void> {
    this.sessionCount = 0;
    this.eventListeners.clear();
    this.emit("engine:cleanup_completed");
  }
}

export default FiveDiagnosisEngine;
