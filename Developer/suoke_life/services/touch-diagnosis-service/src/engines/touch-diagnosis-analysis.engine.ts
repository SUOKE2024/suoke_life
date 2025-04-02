import axios from 'axios';
import { Logger } from '../utils/logger';
import { IPulseDiagnosis, IAbdominalDiagnosis } from '../models/touch-diagnosis.model';

/**
 * 分析结果接口
 */
interface IAnalysisResult {
  constitutionTypes: string[];
  healthImbalances: string[];
  severity: 'mild' | 'moderate' | 'severe';
  confidence: number;
}

/**
 * 触诊分析引擎
 * 负责分析脉诊和腹诊数据，生成TCM诊断结果
 */
export class TouchDiagnosisAnalysisEngine {
  private tcmKnowledgeServiceUrl: string;

  constructor() {
    this.tcmKnowledgeServiceUrl = process.env.TCM_KNOWLEDGE_SERVICE_URL || 'http://localhost:3006/api/tcm-knowledge';
  }

  /**
   * 分析触诊数据
   * @param patientId 患者ID
   * @param pulseData 脉诊数据
   * @param abdominalData 腹诊数据
   * @returns 分析结果
   */
  public async analyze(
    patientId: string, 
    pulseData: IPulseDiagnosis[], 
    abdominalData: IAbdominalDiagnosis[]
  ): Promise<IAnalysisResult> {
    try {
      Logger.info(`开始分析患者 ${patientId} 的触诊数据`);
      
      // 分析脉诊数据
      const pulseAnalysisResult = await this.analyzePulseData(pulseData);
      
      // 分析腹诊数据
      const abdominalAnalysisResult = await this.analyzeAbdominalData(abdominalData);
      
      // 整合分析结果
      const integratedResult = this.integrateResults(pulseAnalysisResult, abdominalAnalysisResult);
      
      // 调用知识服务进行深度分析（可选）
      let enhancedResult = integratedResult;
      try {
        enhancedResult = await this.enhanceAnalysisWithKnowledgeService(patientId, integratedResult);
      } catch (error) {
        Logger.warn('调用知识服务增强分析失败，使用本地分析结果', { error });
      }
      
      Logger.info(`患者 ${patientId} 的触诊数据分析完成`);
      return enhancedResult;
    } catch (error) {
      Logger.error(`触诊数据分析失败`, { error, patientId });
      throw error;
    }
  }

  /**
   * 分析脉诊数据
   * @param pulseData 脉诊数据
   * @returns 脉诊分析结果
   */
  private async analyzePulseData(pulseData: IPulseDiagnosis[]): Promise<{
    constitutionIndications: string[];
    patterns: string[];
    severity: 'mild' | 'moderate' | 'severe';
    confidence: number;
  }> {
    // 如果没有脉诊数据，返回空结果
    if (!pulseData || pulseData.length === 0) {
      return {
        constitutionIndications: [],
        patterns: [],
        severity: 'mild',
        confidence: 0
      };
    }

    // 分析脉位特征
    const positionPatterns = this.analyzePulsePositions(pulseData);
    
    // 分析脉象特征
    const characteristicPatterns = this.analyzePulseCharacteristics(pulseData);
    
    // 分析脉搏深度
    const depthPatterns = this.analyzePulseDepth(pulseData);
    
    // 分析脉搏强度
    const strengthPatterns = this.analyzePulseStrength(pulseData);
    
    // 整合所有特征
    const allPatterns = [
      ...positionPatterns.patterns,
      ...characteristicPatterns.patterns,
      ...depthPatterns.patterns,
      ...strengthPatterns.patterns
    ];
    
    // 整合所有体质指征
    const allConstitutionIndications = [
      ...positionPatterns.constitutionIndications,
      ...characteristicPatterns.constitutionIndications,
      ...depthPatterns.constitutionIndications,
      ...strengthPatterns.constitutionIndications
    ];
    
    // 计算整体严重程度和置信度
    const severity = this.calculateOverallSeverity([
      positionPatterns.severity,
      characteristicPatterns.severity,
      depthPatterns.severity,
      strengthPatterns.severity
    ]);
    
    const confidence = (
      positionPatterns.confidence +
      characteristicPatterns.confidence +
      depthPatterns.confidence +
      strengthPatterns.confidence
    ) / 4;
    
    return {
      constitutionIndications: Array.from(new Set(allConstitutionIndications)),
      patterns: Array.from(new Set(allPatterns)),
      severity,
      confidence: Math.min(confidence, 1.0)
    };
  }

  /**
   * 分析脉位特征
   */
  private analyzePulsePositions(pulseData: IPulseDiagnosis[]): {
    constitutionIndications: string[];
    patterns: string[];
    severity: 'mild' | 'moderate' | 'severe';
    confidence: number;
  } {
    // 简化版分析逻辑，实际系统中会更复杂
    const patterns: string[] = [];
    const constitutionIndications: string[] = [];
    
    // 根据不同脉位进行分析
    for (const data of pulseData) {
      switch (data.position) {
        case 'LEFT_CUN':
          patterns.push('心肺相关');
          break;
        case 'LEFT_GUAN':
          patterns.push('肝脾相关');
          break;
        case 'LEFT_CHI':
          patterns.push('肾与膀胱相关');
          break;
        case 'RIGHT_CUN':
          patterns.push('肺气相关');
          break;
        case 'RIGHT_GUAN':
          patterns.push('胃相关');
          break;
        case 'RIGHT_CHI':
          patterns.push('小肠相关');
          break;
      }
    }
    
    return {
      constitutionIndications,
      patterns,
      severity: 'mild',
      confidence: 0.7
    };
  }

  /**
   * 分析脉象特征
   */
  private analyzePulseCharacteristics(pulseData: IPulseDiagnosis[]): {
    constitutionIndications: string[];
    patterns: string[];
    severity: 'mild' | 'moderate' | 'severe';
    confidence: number;
  } {
    const patterns: string[] = [];
    const constitutionIndications: string[] = [];
    let severeCount = 0;
    let moderateCount = 0;
    
    // 分析每个脉诊数据中的脉象特征
    for (const data of pulseData) {
      if (!data.characteristics || data.characteristics.length === 0) continue;
      
      for (const characteristic of data.characteristics) {
        switch (characteristic) {
          case 'FLOATING':
            patterns.push('表证');
            constitutionIndications.push('气虚体质');
            moderateCount++;
            break;
          case 'SINKING':
            patterns.push('里证');
            break;
          case 'SLOW':
            patterns.push('寒证');
            constitutionIndications.push('阳虚体质');
            break;
          case 'RAPID':
            patterns.push('热证');
            constitutionIndications.push('湿热体质');
            severeCount++;
            break;
          case 'SURGING':
            patterns.push('实热证');
            constitutionIndications.push('湿热体质');
            severeCount++;
            break;
          case 'FINE':
            patterns.push('气血不足');
            constitutionIndications.push('气虚体质');
            constitutionIndications.push('血虚体质');
            moderateCount++;
            break;
          case 'WIRY':
            patterns.push('肝胆病证');
            constitutionIndications.push('肝郁体质');
            moderateCount++;
            break;
          case 'SLIPPERY':
            patterns.push('痰湿证');
            constitutionIndications.push('痰湿体质');
            moderateCount++;
            break;
        }
      }
    }
    
    // 确定严重程度
    let severity: 'mild' | 'moderate' | 'severe' = 'mild';
    if (severeCount > 0) {
      severity = 'severe';
    } else if (moderateCount > 0) {
      severity = 'moderate';
    }
    
    return {
      constitutionIndications,
      patterns,
      severity,
      confidence: 0.85
    };
  }

  /**
   * 分析脉搏深度
   */
  private analyzePulseDepth(pulseData: IPulseDiagnosis[]): {
    constitutionIndications: string[];
    patterns: string[];
    severity: 'mild' | 'moderate' | 'severe';
    confidence: number;
  } {
    const patterns: string[] = [];
    const constitutionIndications: string[] = [];
    
    // 分析每个脉诊数据中的脉搏深度
    for (const data of pulseData) {
      switch (data.depth) {
        case 'SUPERFICIAL':
          patterns.push('表证');
          constitutionIndications.push('气虚体质');
          break;
        case 'MIDDLE':
          patterns.push('半表半里证');
          break;
        case 'DEEP':
          patterns.push('里证');
          constitutionIndications.push('阳虚体质');
          break;
      }
    }
    
    return {
      constitutionIndications,
      patterns,
      severity: 'mild',
      confidence: 0.75
    };
  }

  /**
   * 分析脉搏强度
   */
  private analyzePulseStrength(pulseData: IPulseDiagnosis[]): {
    constitutionIndications: string[];
    patterns: string[];
    severity: 'mild' | 'moderate' | 'severe';
    confidence: number;
  } {
    const patterns: string[] = [];
    const constitutionIndications: string[] = [];
    
    // 分析每个脉诊数据中的脉搏强度
    for (const data of pulseData) {
      switch (data.strength) {
        case 'WEAK':
          patterns.push('虚证');
          constitutionIndications.push('气虚体质');
          constitutionIndications.push('阳虚体质');
          break;
        case 'MODERATE':
          // 正常强度，不添加特殊模式
          break;
        case 'STRONG':
          patterns.push('实证');
          constitutionIndications.push('湿热体质');
          constitutionIndications.push('阴虚体质');
          break;
      }
    }
    
    return {
      constitutionIndications,
      patterns,
      severity: 'mild',
      confidence: 0.7
    };
  }

  /**
   * 分析腹诊数据
   * @param abdominalData 腹诊数据
   * @returns 腹诊分析结果
   */
  private async analyzeAbdominalData(abdominalData: IAbdominalDiagnosis[]): Promise<{
    constitutionIndications: string[];
    patterns: string[];
    severity: 'mild' | 'moderate' | 'severe';
    confidence: number;
  }> {
    // 如果没有腹诊数据，返回空结果
    if (!abdominalData || abdominalData.length === 0) {
      return {
        constitutionIndications: [],
        patterns: [],
        severity: 'mild',
        confidence: 0
      };
    }

    const patterns: string[] = [];
    const constitutionIndications: string[] = [];
    let severeCount = 0;
    let moderateCount = 0;
    
    // 分析每个腹诊数据
    for (const data of abdominalData) {
      // 分析区域相关的病证
      switch (data.region) {
        case 'EPIGASTRIUM':
          patterns.push('胃脘相关');
          break;
        case 'RIGHT_HYPOCHONDRIUM':
          patterns.push('肝胆相关');
          break;
        case 'LEFT_HYPOCHONDRIUM':
          patterns.push('脾相关');
          break;
        case 'UMBILICAL':
          patterns.push('脾胃相关');
          break;
        case 'HYPOGASTRIUM':
          patterns.push('小肠膀胱相关');
          break;
      }
      
      // 分析状态
      if (data.status && data.status.length > 0) {
        for (const status of data.status) {
          switch (status) {
            case 'DISTENSION':
              patterns.push('气滞证');
              constitutionIndications.push('肝郁体质');
              moderateCount++;
              break;
            case 'TENDERNESS':
              patterns.push('实证');
              severeCount++;
              break;
            case 'MASS':
              patterns.push('痰瘀互结');
              constitutionIndications.push('瘀血体质');
              severeCount++;
              break;
            case 'RIGIDITY':
              patterns.push('肝胆实证');
              constitutionIndications.push('肝郁体质');
              severeCount++;
              break;
            case 'FLUID':
              patterns.push('水湿内停');
              constitutionIndications.push('痰湿体质');
              severeCount++;
              break;
            case 'GURGLING':
              patterns.push('肠鸣');
              moderateCount++;
              break;
            case 'PULSATION':
              patterns.push('气机不顺');
              moderateCount++;
              break;
          }
        }
      }
      
      // 分析温度
      if (data.temperature) {
        switch (data.temperature) {
          case 'cold':
            patterns.push('寒证');
            constitutionIndications.push('阳虚体质');
            moderateCount++;
            break;
          case 'hot':
            patterns.push('热证');
            constitutionIndications.push('湿热体质');
            severeCount++;
            break;
        }
      }
      
      // 分析紧张度
      if (data.tension) {
        switch (data.tension) {
          case 'tight':
            patterns.push('肝郁气滞');
            constitutionIndications.push('肝郁体质');
            moderateCount++;
            break;
          case 'loose':
            patterns.push('气虚证');
            constitutionIndications.push('气虚体质');
            moderateCount++;
            break;
        }
      }
    }
    
    // 确定严重程度
    let severity: 'mild' | 'moderate' | 'severe' = 'mild';
    if (severeCount > 0) {
      severity = 'severe';
    } else if (moderateCount > 0) {
      severity = 'moderate';
    }
    
    return {
      constitutionIndications,
      patterns,
      severity,
      confidence: 0.8
    };
  }

  /**
   * 整合脉诊和腹诊分析结果
   */
  private integrateResults(
    pulseResult: {
      constitutionIndications: string[];
      patterns: string[];
      severity: 'mild' | 'moderate' | 'severe';
      confidence: number;
    },
    abdominalResult: {
      constitutionIndications: string[];
      patterns: string[];
      severity: 'mild' | 'moderate' | 'severe';
      confidence: number;
    }
  ): IAnalysisResult {
    // 整合所有体质指征
    const allConstitutionIndications = [
      ...pulseResult.constitutionIndications,
      ...abdominalResult.constitutionIndications
    ];
    
    // 整合所有模式
    const allPatterns = [
      ...pulseResult.patterns,
      ...abdominalResult.patterns
    ];
    
    // 计算整体严重程度
    const severity = this.calculateOverallSeverity([
      pulseResult.severity,
      abdominalResult.severity
    ]);
    
    // 整合置信度
    const totalConfidence = pulseResult.confidence * 0.6 + abdominalResult.confidence * 0.4;
    
    // 整合结果
    const constitutionCountMap = new Map<string, number>();
    for (const constitution of allConstitutionIndications) {
      const count = constitutionCountMap.get(constitution) || 0;
      constitutionCountMap.set(constitution, count + 1);
    }
    
    // 选择出现频率最高的3个体质
    const sortedConstitutions = Array.from(constitutionCountMap.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(entry => entry[0]);
    
    // 去重健康不平衡
    const uniquePatterns = Array.from(new Set(allPatterns));
    
    return {
      constitutionTypes: sortedConstitutions,
      healthImbalances: uniquePatterns,
      severity,
      confidence: Math.min(totalConfidence, 1.0)
    };
  }

  /**
   * 计算整体严重程度
   */
  private calculateOverallSeverity(
    severities: ('mild' | 'moderate' | 'severe')[]
  ): 'mild' | 'moderate' | 'severe' {
    if (severities.includes('severe')) {
      return 'severe';
    }
    if (severities.includes('moderate')) {
      return 'moderate';
    }
    return 'mild';
  }

  /**
   * 使用知识服务增强分析结果
   */
  private async enhanceAnalysisWithKnowledgeService(
    patientId: string,
    basicResult: IAnalysisResult
  ): Promise<IAnalysisResult> {
    try {
      const response = await axios.post(`${this.tcmKnowledgeServiceUrl}/analyze/touch-diagnosis`, {
        patientId,
        basicResult
      });
      
      return response.data.enhancedResult;
    } catch (error) {
      Logger.warn('调用知识服务增强分析失败', { error, patientId });
      return basicResult;
    }
  }
} 