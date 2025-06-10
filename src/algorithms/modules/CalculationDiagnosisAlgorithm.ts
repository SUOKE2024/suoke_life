import { CalculationConfig } from '../config/AlgorithmConfig';
import { TCMKnowledgeBase } from '../knowledge/TCMKnowledgeBase';

/**
 * 中医算诊算法模块
 * 实现基于易学、天文历法的计算诊断功能
 * 这是五诊中的创新诊法，结合传统易学理论与现代计算技术
 * @author 索克生活技术团队
 * @version 1.0.0
 */

// 类型定义
export interface CalculationData {
  birthDate: string;
  birthTime: string;
  birthPlace: string;
  currentDate: string;
  currentTime: string;
  currentLocation: string;
  lunarData?: LunarData;
  metadata?: Record<string, any>;
}

export interface LunarData {
  year: string;
  month: string;
  day: string;
  hour: string;
  yearStem: string;
  yearBranch: string;
  monthStem: string;
  monthBranch: string;
  dayStem: string;
  dayBranch: string;
  hourStem: string;
  hourBranch: string;
  zodiac: string;
  solarTerm: string;
}

export interface CalculationResult {
  confidence: number;
  fiveElements: FiveElementsAnalysis;
  yinYang: YinYangAnalysis;
  qiFlow: QiFlowAnalysis;
  constitution: ConstitutionCalculation;
  seasonalInfluence: SeasonalInfluence;
  timeInfluence: TimeInfluence;
  analysis: string;
  recommendations: string[];
  warnings: string[];
  processingTime?: number;
}

export interface FiveElementsAnalysis {
  birthElements: {
    wood: number;
    fire: number;
    earth: number;
    metal: number;
    water: number;
  };
  currentElements: {
    wood: number;
    fire: number;
    earth: number;
    metal: number;
    water: number;
  };
  balance: {
    overall: number;
    deficiency: string[];
    excess: string[];
    harmony: number;
  };
  interactions: {
    generation: ElementInteraction[];
    restriction: ElementInteraction[];
    overacting: ElementInteraction[];
    insulting: ElementInteraction[];
  };
  organCorrelation: {
    liver: number;
    heart: number;
    spleen: number;
    lung: number;
    kidney: number;
  };
}

export interface ElementInteraction {
  from: string;
  to: string;
  strength: number;
  type: 'generation' | 'restriction' | 'overacting' | 'insulting';
  description: string;
}

export interface YinYangAnalysis {
  birthYinYang: {
    yin: number;
    yang: number;
    balance: number;
  };
  currentYinYang: {
    yin: number;
    yang: number;
    balance: number;
  };
  dynamicBalance: {
    trend: 'increasing_yin' | 'increasing_yang' | 'stable' | 'fluctuating';
    stability: number;
    harmony: number;
  };
  organYinYang: {
    liver: { yin: number; yang: number };
    heart: { yin: number; yang: number };
    spleen: { yin: number; yang: number };
    lung: { yin: number; yang: number };
    kidney: { yin: number; yang: number };
  };
  recommendations: string[];
}

export interface QiFlowAnalysis {
  meridianFlow: {
    [meridian: string]: {
      strength: number;
      direction: 'forward' | 'reverse' | 'stagnant';
      blockages: string[];
      openness: number;
    };
  };
  dailyRhythm: {
    [hour: string]: {
      dominantMeridian: string;
      qiStrength: number;
      recommendations: string[];
    };
  };
  seasonalFlow: {
    currentSeason: string;
    qiDirection: string;
    strength: number;
    adaptability: number;
  };
  overallFlow: {
    circulation: number;
    vitality: number;
    balance: number;
    blockages: string[];
  };
}

export interface ConstitutionCalculation {
  primaryConstitution: string;
  secondaryConstitution?: string;
  constitutionStrength: number;
  adaptability: number;
  vulnerabilities: string[];
  strengths: string[];
  seasonalVariations: {
    spring: number;
    summer: number;
    autumn: number;
    winter: number;
  };
  lifeStageInfluence: {
    current: string;
    characteristics: string[];
    recommendations: string[];
  };
}

export interface SeasonalInfluence {
  currentSeason: string;
  seasonalQi: {
    dominant: string;
    strength: number;
    direction: string;
  };
  solarTerm: {
    current: string;
    influence: string;
    recommendations: string[];
  };
  climaticFactors: {
    wind: number;
    cold: number;
    heat: number;
    dampness: number;
    dryness: number;
    fire: number;
  };
  adaptation: {
    required: string[];
    difficulty: number;
    support: string[];
  };
}

export interface TimeInfluence {
  currentHour: string;
  dominantMeridian: string;
  qiActivity: {
    level: number;
    direction: string;
    quality: string;
  };
  optimalActivities: string[];
  healthFocus: string[];
  energyLevel: number;
}

export interface UserProfile {
  age: number;
  gender: 'male' | 'female' | 'other';
  height: number;
  weight: number;
  occupation: string;
  medicalHistory: string[];
  allergies: string[];
  medications: string[];
}

interface LocationData {
  latitude: number;
  longitude: number;
  timezone: string;
}

/**
 * 中医算诊算法类
 */
export class CalculationDiagnosisAlgorithm {
  private config: CalculationConfig;
  private knowledgeBase: TCMKnowledgeBase;

  constructor(config: CalculationConfig, knowledgeBase: TCMKnowledgeBase) {
    this.config = config;
    this.knowledgeBase = knowledgeBase;
  }

  /**
   * 执行算诊分析
   */
  public async analyze(
    data: CalculationData,
    userProfile?: UserProfile
  ): Promise<CalculationResult> {
    const startTime = Date.now();

    try {
      // 数据预处理
      const processedData = await this.preprocessData(data);
      
      // 计算农历数据
      const lunarData = await this.calculateLunarData(processedData);
      
      // 五行分析
      const fiveElements = await this.analyzeFiveElements(lunarData, userProfile);
      
      // 阴阳分析
      const yinYang = await this.analyzeYinYang(lunarData, userProfile);
      
      // 气机分析
      const qiFlow = await this.analyzeQiFlow(lunarData, userProfile);
      
      // 体质计算
      const constitution = await this.calculateConstitution(lunarData, userProfile);
      
      // 季节影响分析
      const seasonalInfluence = await this.analyzeSeasonalInfluence(lunarData);
      
      // 时间影响分析
      const timeInfluence = await this.analyzeTimeInfluence(lunarData);
      
      // 生成分析报告
      const analysis = await this.generateAnalysis({
        fiveElements,
        yinYang,
        qiFlow,
        constitution,
        seasonalInfluence,
        timeInfluence
      });
      
      // 生成建议
      const recommendations = await this.generateRecommendations({
        fiveElements,
        yinYang,
        qiFlow,
        constitution,
        seasonalInfluence,
        timeInfluence
      });
      
      // 生成警告
      const warnings = await this.generateWarnings({
        fiveElements,
        yinYang,
        qiFlow,
        constitution
      });
      
      // 计算置信度
      const confidence = this.calculateConfidence({
        fiveElements,
        yinYang,
        qiFlow,
        constitution
      });

      const processingTime = Date.now() - startTime;

      return {
        confidence,
        fiveElements,
        yinYang,
        qiFlow,
        constitution,
        seasonalInfluence,
        timeInfluence,
        analysis,
        recommendations,
        warnings,
        processingTime
      };
    } catch (error) {
      throw new Error(`算诊分析失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  }

  /**
   * 数据预处理
   */
  private async preprocessData(data: CalculationData): Promise<CalculationData> {
    // 验证输入数据
    this.validateInputData(data);
    
    // 标准化日期时间格式
    const processedData = {
      ...data,
      birthDate: this.standardizeDate(data.birthDate),
      birthTime: this.standardizeTime(data.birthTime),
      currentDate: this.standardizeDate(data.currentDate),
      currentTime: this.standardizeTime(data.currentTime)
    };

    return processedData;
  }

  /**
   * 验证输入数据
   */
  private validateInputData(data: CalculationData): void {
    if (!data.birthDate || !data.birthTime) {
      throw new Error('出生日期和时间不能为空');
    }
    
    if (!data.currentDate || !data.currentTime) {
      throw new Error('当前日期和时间不能为空');
    }

    // 验证日期格式
    if (!this.isValidDate(data.birthDate) || !this.isValidDate(data.currentDate)) {
      throw new Error('日期格式无效');
    }

    // 验证时间格式
    if (!this.isValidTime(data.birthTime) || !this.isValidTime(data.currentTime)) {
      throw new Error('时间格式无效');
    }
  }

  /**
   * 验证日期格式
   */
  private isValidDate(dateString: string): boolean {
    const date = new Date(dateString);
    return !isNaN(date.getTime());
  }

  /**
   * 验证时间格式
   */
  private isValidTime(timeString: string): boolean {
    const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
    return timeRegex.test(timeString);
  }

  /**
   * 标准化日期格式
   */
  private standardizeDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toISOString().split('T')[0];
  }

  /**
   * 标准化时间格式
   */
  private standardizeTime(timeString: string): string {
    const [hours, minutes] = timeString.split(':');
    return `${hours.padStart(2, '0')}:${minutes.padStart(2, '0')}`;
  }

  /**
   * 计算农历数据
   */
  private async calculateLunarData(data: CalculationData): Promise<LunarData> {
    // 这里应该实现真正的农历计算逻辑
    // 目前返回模拟数据
    return {
      year: '甲子',
      month: '丙寅',
      day: '戊辰',
      hour: '庚午',
      yearStem: '甲',
      yearBranch: '子',
      monthStem: '丙',
      monthBranch: '寅',
      dayStem: '戊',
      dayBranch: '辰',
      hourStem: '庚',
      hourBranch: '午',
      zodiac: '鼠',
      solarTerm: '立春'
    };
  }

  /**
   * 五行分析
   */
  private async analyzeFiveElements(
    lunarData: LunarData,
    userProfile?: UserProfile
  ): Promise<FiveElementsAnalysis> {
    // 实现五行分析逻辑
    return {
      birthElements: {
        wood: 0.2,
        fire: 0.3,
        earth: 0.2,
        metal: 0.15,
        water: 0.15
      },
      currentElements: {
        wood: 0.25,
        fire: 0.2,
        earth: 0.25,
        metal: 0.15,
        water: 0.15
      },
      balance: {
        overall: 0.8,
        deficiency: ['金'],
        excess: ['火'],
        harmony: 0.75
      },
      interactions: {
        generation: [],
        restriction: [],
        overacting: [],
        insulting: []
      },
      organCorrelation: {
        liver: 0.8,
        heart: 0.9,
        spleen: 0.7,
        lung: 0.6,
        kidney: 0.7
      }
    };
  }

  /**
   * 阴阳分析
   */
  private async analyzeYinYang(
    lunarData: LunarData,
    userProfile?: UserProfile
  ): Promise<YinYangAnalysis> {
    // 实现阴阳分析逻辑
    return {
      birthYinYang: {
        yin: 0.45,
        yang: 0.55,
        balance: 0.8
      },
      currentYinYang: {
        yin: 0.5,
        yang: 0.5,
        balance: 0.9
      },
      dynamicBalance: {
        trend: 'stable',
        stability: 0.85,
        harmony: 0.8
      },
      organYinYang: {
        liver: { yin: 0.6, yang: 0.4 },
        heart: { yin: 0.3, yang: 0.7 },
        spleen: { yin: 0.5, yang: 0.5 },
        lung: { yin: 0.7, yang: 0.3 },
        kidney: { yin: 0.8, yang: 0.2 }
      },
      recommendations: ['保持阴阳平衡', '适度运动', '规律作息']
    };
  }

  /**
   * 气机分析
   */
  private async analyzeQiFlow(
    lunarData: LunarData,
    userProfile?: UserProfile
  ): Promise<QiFlowAnalysis> {
    // 实现气机分析逻辑
    return {
      meridianFlow: {
        '肺经': {
          strength: 0.8,
          direction: 'forward',
          blockages: [],
          openness: 0.9
        }
      },
      dailyRhythm: {
        '3-5': {
          dominantMeridian: '肺经',
          qiStrength: 0.9,
          recommendations: ['深呼吸', '养肺']
        }
      },
      seasonalFlow: {
        currentSeason: '春',
        qiDirection: '升发',
        strength: 0.8,
        adaptability: 0.7
      },
      overallFlow: {
        circulation: 0.8,
        vitality: 0.85,
        balance: 0.75,
        blockages: []
      }
    };
  }

  /**
   * 体质计算
   */
  private async calculateConstitution(
    lunarData: LunarData,
    userProfile?: UserProfile
  ): Promise<ConstitutionCalculation> {
    // 实现体质计算逻辑
    return {
      primaryConstitution: '平和质',
      secondaryConstitution: '气虚质',
      constitutionStrength: 0.8,
      adaptability: 0.75,
      vulnerabilities: ['易感冒'],
      strengths: ['适应力强'],
      seasonalVariations: {
        spring: 0.8,
        summer: 0.9,
        autumn: 0.7,
        winter: 0.6
      },
      lifeStageInfluence: {
        current: '青年期',
        characteristics: ['精力充沛', '新陈代谢旺盛'],
        recommendations: ['保持运动', '合理饮食']
      }
    };
  }

  /**
   * 季节影响分析
   */
  private async analyzeSeasonalInfluence(lunarData: LunarData): Promise<SeasonalInfluence> {
    // 实现季节影响分析逻辑
    return {
      currentSeason: '春',
      seasonalQi: {
        dominant: '木',
        strength: 0.8,
        direction: '升发'
      },
      solarTerm: {
        current: lunarData.solarTerm,
        influence: '阳气初生',
        recommendations: ['养肝', '疏肝理气']
      },
      climaticFactors: {
        wind: 0.7,
        cold: 0.3,
        heat: 0.2,
        dampness: 0.4,
        dryness: 0.2,
        fire: 0.1
      },
      adaptation: {
        required: ['防风', '养肝'],
        difficulty: 0.3,
        support: ['适度运动', '调节情志']
      }
    };
  }

  /**
   * 时间影响分析
   */
  private async analyzeTimeInfluence(lunarData: LunarData): Promise<TimeInfluence> {
    // 实现时间影响分析逻辑
    return {
      currentHour: lunarData.hour,
      dominantMeridian: '肺经',
      qiActivity: {
        level: 0.8,
        direction: '升',
        quality: '清'
      },
      optimalActivities: ['深呼吸', '冥想'],
      healthFocus: ['养肺', '调息'],
      energyLevel: 0.8
    };
  }

  /**
   * 生成分析报告
   */
  private async generateAnalysis(data: {
    fiveElements: FiveElementsAnalysis;
    yinYang: YinYangAnalysis;
    qiFlow: QiFlowAnalysis;
    constitution: ConstitutionCalculation;
    seasonalInfluence: SeasonalInfluence;
    timeInfluence: TimeInfluence;
  }): Promise<string> {
    // 生成综合分析报告
    return `基于您的出生信息和当前时间的算诊分析显示：
您的主要体质类型为${data.constitution.primaryConstitution}，
五行平衡度为${(data.fiveElements.balance.overall * 100).toFixed(1)}%，
阴阳平衡度为${(data.yinYang.currentYinYang.balance * 100).toFixed(1)}%。
当前季节${data.seasonalInfluence.currentSeason}对您的影响较为适中，
建议重点关注${data.timeInfluence.healthFocus.join('、')}。`;
  }

  /**
   * 生成建议
   */
  private async generateRecommendations(data: {
    fiveElements: FiveElementsAnalysis;
    yinYang: YinYangAnalysis;
    qiFlow: QiFlowAnalysis;
    constitution: ConstitutionCalculation;
    seasonalInfluence: SeasonalInfluence;
    timeInfluence: TimeInfluence;
  }): Promise<string[]> {
    const recommendations: string[] = [];
    
    // 基于体质的建议
    recommendations.push(...data.constitution.lifeStageInfluence.recommendations);
    
    // 基于阴阳的建议
    recommendations.push(...data.yinYang.recommendations);
    
    // 基于季节的建议
    recommendations.push(...data.seasonalInfluence.solarTerm.recommendations);
    
    // 基于时间的建议
    recommendations.push(...data.timeInfluence.optimalActivities);

    return [...new Set(recommendations)]; // 去重
  }

  /**
   * 生成警告
   */
  private async generateWarnings(data: {
    fiveElements: FiveElementsAnalysis;
    yinYang: YinYangAnalysis;
    qiFlow: QiFlowAnalysis;
    constitution: ConstitutionCalculation;
  }): Promise<string[]> {
    const warnings: string[] = [];
    
    // 五行失衡警告
    if (data.fiveElements.balance.overall < 0.6) {
      warnings.push('五行失衡较为严重，建议及时调理');
    }
    
    // 阴阳失衡警告
    if (data.yinYang.currentYinYang.balance < 0.6) {
      warnings.push('阴阳失衡，需要重点关注');
    }
    
    // 气机不畅警告
    if (data.qiFlow.overallFlow.circulation < 0.6) {
      warnings.push('气机运行不畅，建议加强运动');
    }
    
    // 体质脆弱性警告
    if (data.constitution.vulnerabilities.length > 0) {
      warnings.push(`注意防范：${data.constitution.vulnerabilities.join('、')}`);
    }

    return warnings;
  }

  /**
   * 计算置信度
   */
  private calculateConfidence(data: {
    fiveElements: FiveElementsAnalysis;
    yinYang: YinYangAnalysis;
    qiFlow: QiFlowAnalysis;
    constitution: ConstitutionCalculation;
  }): number {
    const factors = [
      data.fiveElements.balance.overall,
      data.yinYang.currentYinYang.balance,
      data.qiFlow.overallFlow.balance,
      data.constitution.constitutionStrength
    ];
    
    return factors.reduce((sum, factor) => sum + factor, 0) / factors.length;
  }
}

export default CalculationDiagnosisAlgorithm; 