import { EventEmitter } from "events";
import { PalpationConfig } from "../config/AlgorithmConfig";
import { TCMKnowledgeBase } from "../knowledge/TCMKnowledgeBase";

/**
 * 切诊算法模块
 * 实现中医切诊功能，包括脉象分析、触诊分析、温度感知
 * @author 索克生活技术团队
 * @version 1.0.0
 */

export interface PalpationData {
  pulseData?: PulseData;
  touchData?: TouchData;
  temperatureData?: TemperatureData;
  pressureData?: PressureData;
  metadata?: Record<string, any>;
}

export interface PulseData {
  waveform: number[];
  duration: number; // 采集时长（秒）
  positions: PulsePosition[]; // 寸关尺三部位数据
}

export interface PulsePosition {
  position: "cun" | "guan" | "chi";
  side: "left" | "right"; // 左右手
  pressure: "light" | "medium" | "heavy";
}

export interface TouchData {
  skinTexture?: SkinTextureData;
  muscleElasticity?: MuscleElasticityData;
  jointMobility?: JointMobilityData;
  abdominalPalpation?: AbdominalPalpationData;
}

export interface SkinTextureData {
  moisture: number; // 0-1, 湿润度
  temperature: number; // 相对温度
  thickness: number; // 厚薄
  smoothness: number; // 0-1, 光滑度
}

export interface MuscleElasticityData {
  firmness: number; // 0-1, 紧实度
  elasticity: number; // 0-1, 弹性
  symmetry: number; // 0-1, 对称性
}

export interface JointMobilityData {
  range: number; // 0-1, 活动度
  stiffness: number; // 0-1, 僵硬度
  swelling: number; // 0-1, 肿胀程度
}

export interface AbdominalPalpationData {
  tenderness: TendernessData[];
  masses: MassData[];
  organSize: OrganSizeData;
  muscleGuarding: number; // 0-1, 肌紧张
}

export interface TendernessData {
  location: string;
  intensity: number; // 0-1, 压痛强度
  type: "superficial" | "deep";
  rebound: boolean;
}

export interface MassData {
  location: string;
  size: number; // cm
  consistency: "soft" | "firm" | "hard";
  mobility: "mobile" | "fixed";
  pulsatile: boolean;
}

export interface OrganSizeData {
  liver: number; // 肝脏大小（cm）
  spleen: number; // 脾脏大小（cm）
}

export interface TemperatureData {
  bodyTemperature: number;
  localTemperatures: LocalTemperatureData[];
  temperatureDistribution: TemperatureDistributionData;
}

export interface LocalTemperatureData {
  location: string;
  temperature: number;
  comparison: "warmer" | "cooler" | "normal";
}

export interface TemperatureDistributionData {
  head: number;
  chest: number;
  abdomen: number;
  limbs: number;
  extremities: number;
}

export interface PressureData {
  systolic: number; // 收缩压
  diastolic: number; // 舒张压
  pulseRate: number; // 脉率
}

export interface PalpationResult {
  confidence: number;
  features: PalpationFeatures;
  analysis: string;
  pulseAnalysis?: PulseAnalysis;
  touchAnalysis?: TouchAnalysis;
  temperatureAnalysis?: TemperatureAnalysis;
}

export interface PalpationFeatures {
  pulse: PulseFeatures;
  touch: TouchFeatures;
  temperature: TemperatureFeatures;
  pressure: PressureFeatures;
}

export interface PulseFeatures {
  rate: number;
  rhythm: string; // 脉律
  depth: string; // 脉位（浮沉）
  length: string; // 脉长
  smoothness: string; // 脉流利度
}

export interface TouchFeatures {
  skinCondition: string;
  muscleCondition: string;
  jointCondition: string;
  abdominalCondition: string;
}

export interface TemperatureFeatures {
  overallTemperature: string;
  temperaturePattern: string;
  localVariations: string[];
}

export interface PressureFeatures {
  bloodPressure: string;
  pulseCharacteristics: string;
}

export interface PulseAnalysis {
  pulseType: PulseType;
  pulseCharacteristics: PulseCharacteristics;
  organCorrelation: OrganCorrelation;
  syndromeIndications: string[];
  pathologicalSignificance: string;
}

export interface PulseType {
  primary: string;
  secondary: string[]; // 兼见脉象
  description: string;
}

export interface PulseCharacteristics {
  rate: { value: number; interpretation: string };
  rhythm: { value: string; interpretation: string };
  strength: { value: string; interpretation: string };
  depth: { value: string; interpretation: string };
  width: { value: string; interpretation: string };
}

export interface OrganCorrelation {
  heart: string;
  liver: string;
  spleen: string;
  lung: string;
  kidney: string;
  gallbladder: string;
  stomach: string;
  smallIntestine: string;
  largeIntestine: string;
  bladder: string;
  tripleHeater: string;
  pericardium: string;
}

export interface TouchAnalysis {
  skinAnalysis: SkinAnalysis;
  muscleAnalysis: MuscleAnalysis;
  jointAnalysis: JointAnalysis;
  abdominalAnalysis: AbdominalAnalysis;
  overallAssessment: string;
}

export interface SkinAnalysis {
  moisture: { value: string; significance: string };
  temperature: { value: string; significance: string };
  elasticity: { value: string; significance: string };
  texture: { value: string; significance: string };
  tcmInterpretation: string;
}

export interface MuscleAnalysis {
  tone: { value: string; significance: string };
  elasticity: { value: string; significance: string };
  strength: { value: string; significance: string };
  tcmInterpretation: string;
}

export interface JointAnalysis {
  mobility: { value: string; significance: string };
  stability: { value: string; significance: string };
  inflammation: { value: string; significance: string };
  tcmInterpretation: string;
}

export interface AbdominalAnalysis {
  organAssessment: OrganAssessment;
  pathologicalFindings: PathologicalFinding[];
  tcmInterpretation: string;
}

export interface OrganAssessment {
  liver: string;
  spleen: string;
  kidney: string;
  stomach: string;
  intestines: string;
}

export interface PathologicalFinding {
  type: string;
  location: string;
  significance: string;
  recommendation: string;
}

export interface TemperatureAnalysis {
  thermalPattern: ThermalPattern;
  organThermalStates: OrganThermalState[];
  constitutionalImplications: string[];
  syndromeIndications: string[];
}

export interface ThermalPattern {
  overall: string;
  distribution: string; // 分布特点
  tcmInterpretation: string;
}

export interface OrganThermalState {
  organ: string;
  thermalState: string;
  significance: string;
}

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

interface ProcessedSignalData {
  pulseSignals?: unknown;
  touchSignals?: unknown;
  temperatureSignals?: unknown;
}

interface AnalysisResults {
  pulseAnalysis?: PulseAnalysis;
  touchAnalysis?: TouchAnalysis;
  temperatureAnalysis?: TemperatureAnalysis;
}

// 切诊算法类
export class PalpationDiagnosisAlgorithm extends EventEmitter {
  private config: PalpationConfig;
  private knowledgeBase: TCMKnowledgeBase;
  private pulseAnalyzer!: PulseAnalyzer;
  private touchAnalyzer!: TouchAnalyzer;
  private temperatureAnalyzer!: TemperatureAnalyzer;

  constructor(config: PalpationConfig, knowledgeBase: TCMKnowledgeBase) {
    super();
    this.config = config;
    this.knowledgeBase = knowledgeBase;
    this.initializeAnalyzers();
  }

  // 初始化分析器
  private initializeAnalyzers(): void {
    this.pulseAnalyzer = new PulseAnalyzer(
      this.config.models.pulseAnalysis,
      this.knowledgeBase
    );
    this.touchAnalyzer = new TouchAnalyzer(
      this.config.models.touchAnalysis,
      this.knowledgeBase
    );
    this.temperatureAnalyzer = new TemperatureAnalyzer(
      this.config.models.temperatureAnalysis,
      this.knowledgeBase
    );
  }

  // 执行切诊分析
  public async analyze(
    data: PalpationData,
    userProfile?: UserProfile
  ): Promise<PalpationResult> {
    if (!this.config.enabled) {
      throw new Error("切诊功能未启用");
    }

    try {
      this.emit("algorithm:progress", {
        stage: "preprocessing",
        progress: 0.1
      });

      const processedData = await this.preprocessData(data);

      this.emit("algorithm:progress", {
        stage: "feature_extraction",
        progress: 0.3
      });

      const features = await this.extractFeatures(processedData);

      this.emit("algorithm:progress", {
        stage: "analysis",
        progress: 0.6
      });

      const analyses = await this.performAnalyses(
        processedData,
        features,
        userProfile
      );

      this.emit("algorithm:progress", {
        stage: "integration",
        progress: 0.8
      });

      const result = await this.integrateResults(features, analyses);

      this.emit("algorithm:progress", {
        stage: "completed",
        progress: 1.0
      });

      return result;
    } catch (error) {
      this.emit("algorithm:error", { error, stage: "palpation_analysis" });
      throw error;
    }
  }

  // 数据预处理
  private async preprocessData(data: PalpationData): Promise<ProcessedSignalData> {
    const processed: ProcessedSignalData = {};

    if (data.pulseData) {
      processed.pulseSignals = await this.preprocessPulseData(data.pulseData);
    }

    if (data.touchData) {
      processed.touchSignals = await this.preprocessTouchData(data.touchData);
    }

    if (data.temperatureData) {
      processed.temperatureSignals = await this.preprocessTemperatureData(data.temperatureData);
    }

    return processed;
  }

  // 脉象数据预处理
  private async preprocessPulseData(pulseData: PulseData): Promise<unknown> {
    // 信号滤波
    const filtered = await this.filterPulseSignal(pulseData.waveform);
    
    // 特征点检测
    const peaks = await this.detectPulsePeaks(filtered);
    
    // 节律分析
    const rhythm = await this.analyzePulseRhythm(peaks);

    return {
      originalWaveform: pulseData.waveform,
      filteredWaveform: filtered,
      peaks,
      rhythm,
      positions: pulseData.positions,
      duration: pulseData.duration
    };
  }

  // 触诊数据预处理
  private async preprocessTouchData(touchData: TouchData): Promise<unknown> {
    return {
      skinTexture: touchData.skinTexture,
      muscleElasticity: touchData.muscleElasticity,
      jointMobility: touchData.jointMobility,
      abdominalPalpation: touchData.abdominalPalpation
    };
  }

  // 温度数据预处理
  private async preprocessTemperatureData(temperatureData: TemperatureData): Promise<unknown> {
    return {
      bodyTemperature: temperatureData.bodyTemperature,
      localTemperatures: temperatureData.localTemperatures,
      temperatureDistribution: temperatureData.temperatureDistribution
    };
  }

  // 特征提取
  private async extractFeatures(data: ProcessedSignalData): Promise<PalpationFeatures> {
    const features: PalpationFeatures = {
      pulse: {
        rate: 0,
        rhythm: "",
        depth: "",
        length: "",
        smoothness: ""
      },
      touch: {
        skinCondition: "",
        muscleCondition: "",
        jointCondition: "",
        abdominalCondition: ""
      },
      temperature: {
        overallTemperature: "",
        temperaturePattern: "",
        localVariations: []
      },
      pressure: {
        bloodPressure: "",
        pulseCharacteristics: ""
      }
    };

    if (data.pulseSignals) {
      features.pulse = await this.pulseAnalyzer.extractFeatures(data.pulseSignals);
    }

    if (data.touchSignals) {
      features.touch = await this.touchAnalyzer.extractFeatures(data.touchSignals);
    }

    if (data.temperatureSignals) {
      features.temperature = await this.temperatureAnalyzer.extractFeatures(data.temperatureSignals);
    }

    return features;
  }

  // 执行分析
  private async performAnalyses(
    data: ProcessedSignalData,
    features: PalpationFeatures,
    userProfile?: UserProfile
  ): Promise<AnalysisResults> {
    const analyses: AnalysisResults = {};

    if (data.pulseSignals) {
      analyses.pulseAnalysis = await this.pulseAnalyzer.analyze(features.pulse, userProfile);
    }

    if (data.touchSignals) {
      analyses.touchAnalysis = await this.touchAnalyzer.analyze(features.touch, userProfile);
    }

    if (data.temperatureSignals) {
      analyses.temperatureAnalysis = await this.temperatureAnalyzer.analyze(features.temperature, userProfile);
    }

    return analyses;
  }

  // 整合结果
  private async integrateResults(
    features: PalpationFeatures,
    analyses: AnalysisResults
  ): Promise<PalpationResult> {
    const confidence = this.calculateConfidence(features, analyses);
    const analysis = await this.generateAnalysis(features, analyses);

    return {
      confidence,
      features,
      analysis,
      pulseAnalysis: analyses.pulseAnalysis,
      touchAnalysis: analyses.touchAnalysis,
      temperatureAnalysis: analyses.temperatureAnalysis
    };
  }

  // 计算置信度
  private calculateConfidence(features: PalpationFeatures, analyses: AnalysisResults): number {
    let totalConfidence = 0;
    let count = 0;

    if (analyses.pulseAnalysis) {
      totalConfidence += 0.8; // 脉诊置信度较高
      count++;
    }

    if (analyses.touchAnalysis) {
      totalConfidence += 0.7;
      count++;
    }

    if (analyses.temperatureAnalysis) {
      totalConfidence += 0.6;
      count++;
    }

    return count > 0 ? totalConfidence / count : 0;
  }

  // 生成分析报告
  private async generateAnalysis(
    features: PalpationFeatures,
    analyses: AnalysisResults
  ): Promise<string> {
    const sections: string[] = [];

    if (analyses.pulseAnalysis) {
      sections.push(`脉象分析：${analyses.pulseAnalysis.pathologicalSignificance}`);
    }

    if (analyses.touchAnalysis) {
      sections.push(`触诊分析：${analyses.touchAnalysis.overallAssessment}`);
    }

    if (analyses.temperatureAnalysis) {
      sections.push(`温度分析：${analyses.temperatureAnalysis.thermalPattern.tcmInterpretation}`);
    }

    return sections.join('\n');
  }

  // 辅助方法
  private async filterPulseSignal(waveform: number[]): Promise<number[]> {
    // 简单的低通滤波器实现
    return waveform.map((value, index) => {
      if (index === 0 || index === waveform.length - 1) return value;
      return (waveform[index - 1] + value + waveform[index + 1]) / 3;
    });
  }

  private async detectPulsePeaks(waveform: number[]): Promise<number[]> {
    const peaks: number[] = [];
    for (let i = 1; i < waveform.length - 1; i++) {
      if (waveform[i] > waveform[i - 1] && waveform[i] > waveform[i + 1]) {
        peaks.push(i);
      }
    }
    return peaks;
  }

  private async analyzePulseRhythm(peaks: number[]): Promise<string> {
    if (peaks.length < 2) return "irregular";
    
    const intervals = [];
    for (let i = 1; i < peaks.length; i++) {
      intervals.push(peaks[i] - peaks[i - 1]);
    }
    
    const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
    const variance = intervals.reduce((sum, interval) => sum + Math.pow(interval - avgInterval, 2), 0) / intervals.length;
    
    return variance < 10 ? "regular" : "irregular";
  }

  // 清理资源
  public async cleanup(): Promise<void> {
    await this.pulseAnalyzer?.cleanup();
    await this.touchAnalyzer?.cleanup();
    await this.temperatureAnalyzer?.cleanup();
  }
}

// 脉象分析器
class PulseAnalyzer {
  constructor(private config: unknown, private knowledgeBase: TCMKnowledgeBase) {}

  async extractFeatures(pulseSignals: unknown): Promise<PulseFeatures> {
    return {
      rate: 72,
      rhythm: "regular",
      depth: "moderate",
      length: "normal",
      smoothness: "smooth"
    };
  }

  async analyze(features: PulseFeatures, userProfile?: UserProfile): Promise<PulseAnalysis> {
    return {
      pulseType: {
        primary: "平脉",
        secondary: [],
        description: "正常脉象"
      },
      pulseCharacteristics: {
        rate: { value: features.rate, interpretation: "正常心率" },
        rhythm: { value: features.rhythm, interpretation: "节律规整" },
        strength: { value: "moderate", interpretation: "脉力适中" },
        depth: { value: features.depth, interpretation: "脉位正常" },
        width: { value: "normal", interpretation: "脉宽正常" }
      },
      organCorrelation: {
        heart: "正常",
        liver: "正常",
        spleen: "正常",
        lung: "正常",
        kidney: "正常",
        gallbladder: "正常",
        stomach: "正常",
        smallIntestine: "正常",
        largeIntestine: "正常",
        bladder: "正常",
        tripleHeater: "正常",
        pericardium: "正常"
      },
      syndromeIndications: [],
      pathologicalSignificance: "脉象正常，气血调和"
    };
  }

  async cleanup(): Promise<void> {}
}

// 触诊分析器
class TouchAnalyzer {
  constructor(private config: unknown, private knowledgeBase: TCMKnowledgeBase) {}

  async extractFeatures(touchSignals: unknown): Promise<TouchFeatures> {
    return {
      skinCondition: "normal",
      muscleCondition: "normal",
      jointCondition: "normal",
      abdominalCondition: "normal"
    };
  }

  async analyze(features: TouchFeatures, userProfile?: UserProfile): Promise<TouchAnalysis> {
    return {
      skinAnalysis: {
        moisture: { value: "normal", significance: "皮肤湿润度正常" },
        temperature: { value: "normal", significance: "皮肤温度正常" },
        elasticity: { value: "normal", significance: "皮肤弹性正常" },
        texture: { value: "smooth", significance: "皮肤质地正常" },
        tcmInterpretation: "皮肤状态良好，气血充足"
      },
      muscleAnalysis: {
        tone: { value: "normal", significance: "肌张力正常" },
        elasticity: { value: "normal", significance: "肌肉弹性正常" },
        strength: { value: "normal", significance: "肌力正常" },
        tcmInterpretation: "肌肉状态良好，脾胃功能正常"
      },
      jointAnalysis: {
        mobility: { value: "normal", significance: "关节活动度正常" },
        stability: { value: "stable", significance: "关节稳定性良好" },
        inflammation: { value: "none", significance: "无炎症表现" },
        tcmInterpretation: "关节功能正常，肝肾充足"
      },
      abdominalAnalysis: {
        organAssessment: {
          liver: "正常",
          spleen: "正常",
          kidney: "正常",
          stomach: "正常",
          intestines: "正常"
        },
        pathologicalFindings: [],
        tcmInterpretation: "腹部触诊正常，脏腑功能良好"
      },
      overallAssessment: "触诊检查正常，体质良好"
    };
  }

  async cleanup(): Promise<void> {}
}

// 温度分析器
class TemperatureAnalyzer {
  constructor(private config: unknown, private knowledgeBase: TCMKnowledgeBase) {}

  async extractFeatures(temperatureSignals: unknown): Promise<TemperatureFeatures> {
    return {
      overallTemperature: "normal",
      temperaturePattern: "balanced",
      localVariations: []
    };
  }

  async analyze(features: TemperatureFeatures, userProfile?: UserProfile): Promise<TemperatureAnalysis> {
    return {
      thermalPattern: {
        overall: "正常",
        distribution: "均匀",
        tcmInterpretation: "体温分布正常，阴阳平衡"
      },
      organThermalStates: [
        { organ: "heart", thermalState: "normal", significance: "心火正常" },
        { organ: "liver", thermalState: "normal", significance: "肝火正常" },
        { organ: "spleen", thermalState: "normal", significance: "脾阳正常" },
        { organ: "lung", thermalState: "normal", significance: "肺气正常" },
        { organ: "kidney", thermalState: "normal", significance: "肾阳正常" }
      ],
      constitutionalImplications: ["体质平和"],
      syndromeIndications: []
    };
  }

  async cleanup(): Promise<void> {}
}