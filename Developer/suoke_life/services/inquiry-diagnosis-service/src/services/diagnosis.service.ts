import { Service } from 'typedi';
import { v4 as uuidv4 } from 'uuid';
import { Logger } from '../utils/logger';
import { 
  DiagnosisRequest, 
  DiagnosisResult, 
  DiagnosisResponse, 
  TCMPattern,
  ConstitutionType,
  ConstitutionAnalysis,
  HealthRecommendation,
  RecommendationType,
  CategorizedSymptom,
  SymptomCategory
} from '../models/diagnosis.model';
import { NotFoundError, BusinessError, AIServiceError } from '../utils/error-handler';
import { DiagnosisResultRepository } from '../db/repositories/diagnosis-result.repository';
import { FourDiagnosisCoordinatorService } from '../integrations/four-diagnosis-coordinator.service';
import axios from 'axios';

/**
 * 诊断服务类
 * 负责处理问诊症状分析和中医辨证诊断
 */
@Service()
export class DiagnosisService {
  private logger: Logger;
  
  constructor(
    private diagnosisResultRepository: DiagnosisResultRepository,
    private coordinatorService: FourDiagnosisCoordinatorService
  ) {
    this.logger = new Logger('DiagnosisService');
  }
  
  /**
   * 生成诊断结果
   * @param request 诊断请求
   * @returns 诊断响应
   */
  async generateDiagnosis(request: DiagnosisRequest): Promise<DiagnosisResponse> {
    this.logger.info(`开始生成诊断，会话ID: ${request.sessionId}, 用户ID: ${request.userId}`);
    const startTime = Date.now();
    
    try {
      // 1. 提取和分类症状
      const categorizedSymptoms = this.categorizeSymptoms(request.symptoms);
      
      // 2. 进行中医辨证
      const tcmPatterns = await this.identifyTCMPatterns(request.symptoms, request.patientInfo);
      
      // 3. 体质辨识
      const constitutionAnalysis = await this.analyzeConstitution(
        request.symptoms, 
        tcmPatterns, 
        request.patientInfo
      );
      
      // 4. 生成健康建议
      const recommendations = await this.generateRecommendations(
        tcmPatterns, 
        constitutionAnalysis, 
        categorizedSymptoms,
        request.preferences
      );
      
      // 5. 生成诊断总结
      const summary = await this.generateSummary(
        tcmPatterns, 
        constitutionAnalysis, 
        categorizedSymptoms, 
        recommendations,
        request.preferences
      );
      
      // 6. 生成后续问题
      const followUpQuestions = await this.generateFollowUpQuestions(
        tcmPatterns, 
        categorizedSymptoms
      );
      
      // 7. 评估警告指标
      const warningIndicators = this.evaluateWarningIndicators(
        categorizedSymptoms, 
        tcmPatterns
      );
      
      // 8. 组装诊断结果
      const diagnosis: DiagnosisResult = {
        diagnosisId: uuidv4(),
        sessionId: request.sessionId,
        userId: request.userId,
        timestamp: new Date().toISOString(),
        tcmPatterns,
        categorizedSymptoms,
        constitutionAnalysis,
        recommendations,
        summary,
        followUpQuestions,
        warningIndicators,
        confidence: this.calculateOverallConfidence(tcmPatterns, categorizedSymptoms),
        metadata: {
          generatedBy: 'inquiry-diagnosis-service',
          version: '1.0.0',
          processingTime: Date.now() - startTime
        }
      };
      
      // 9. 保存诊断结果到数据库
      const savedDiagnosis = await this.diagnosisResultRepository.createDiagnosis(diagnosis);
      
      // 10. 上报诊断结果到四诊协调服务（异步进行，不影响响应）
      this.coordinatorService.reportDiagnosis(savedDiagnosis)
        .then(success => {
          if (success) {
            this.logger.info(`诊断结果上报成功，诊断ID: ${savedDiagnosis.diagnosisId}`);
          } else {
            this.logger.warn(`诊断结果上报失败，诊断ID: ${savedDiagnosis.diagnosisId}`);
          }
        })
        .catch(error => {
          this.logger.error(`诊断结果上报错误: ${error.message}`, { 
            diagnosisId: savedDiagnosis.diagnosisId, 
            error 
          });
        });
      
      // 11. 返回诊断响应
      return {
        diagnosis: savedDiagnosis,
        success: true,
        processingTime: Date.now() - startTime
      };
    } catch (error) {
      this.logger.error(`生成诊断失败: ${error.message}`, { 
        sessionId: request.sessionId, 
        userId: request.userId, 
        error 
      });
      
      throw error instanceof AIServiceError 
        ? error 
        : new AIServiceError(`生成诊断失败: ${error.message}`);
    }
  }
  
  /**
   * 获取诊断结果
   * @param diagnosisId 诊断ID
   * @returns 诊断结果
   */
  async getDiagnosisById(diagnosisId: string): Promise<DiagnosisResult> {
    this.logger.info(`获取诊断结果，诊断ID: ${diagnosisId}`);
    
    try {
      return await this.diagnosisResultRepository.getDiagnosisById(diagnosisId);
    } catch (error) {
      this.logger.error(`获取诊断结果失败: ${error.message}`, { error });
      throw error;
    }
  }
  
  /**
   * 通过会话ID获取诊断结果
   * @param sessionId 会话ID
   * @returns 诊断结果
   */
  async getDiagnosisBySessionId(sessionId: string): Promise<DiagnosisResult> {
    this.logger.info(`通过会话ID获取诊断结果，会话ID: ${sessionId}`);
    
    try {
      return await this.diagnosisResultRepository.getDiagnosisBySessionId(sessionId);
    } catch (error) {
      this.logger.error(`通过会话ID获取诊断结果失败: ${error.message}`, { error });
      throw error;
    }
  }
  
  /**
   * 获取用户的诊断历史
   * @param userId 用户ID
   * @param limit 结果限制
   * @param offset 结果偏移
   * @returns 诊断结果数组
   */
  async getUserDiagnosisHistory(
    userId: string, 
    limit: number = 10, 
    offset: number = 0
  ): Promise<DiagnosisResult[]> {
    this.logger.info(`获取用户诊断历史，用户ID: ${userId}`);
    
    try {
      const { diagnoses } = await this.diagnosisResultRepository.getUserDiagnosisHistory(
        userId, 
        limit, 
        offset
      );
      
      return diagnoses;
    } catch (error) {
      this.logger.error(`获取用户诊断历史失败: ${error.message}`, { error });
      throw error;
    }
  }
  
  /**
   * 对症状进行分类
   * @param symptoms 提取的症状数组
   * @returns 分类后的症状数组
   */
  private categorizeSymptoms(symptoms: any[]): CategorizedSymptom[] {
    // 按照症状的严重度和置信度进行排序
    const sortedSymptoms = [...symptoms].sort((a, b) => {
      const severityA = a.severity || 0;
      const severityB = b.severity || 0;
      const confidenceA = a.confidence || 0;
      const confidenceB = b.confidence || 0;
      
      // 主要按严重度排序，其次按置信度
      return (severityB - severityA) || (confidenceB - confidenceA);
    });
    
    // 进行症状分类
    const categorizedSymptoms: CategorizedSymptom[] = [];
    
    // 将前3个症状作为主症
    sortedSymptoms.slice(0, 3).forEach(symptom => {
      if (symptom.severity >= 7 || (symptom.confidence && symptom.confidence >= 0.8)) {
        categorizedSymptoms.push({
          name: symptom.name,
          category: SymptomCategory.MAIN,
          severity: symptom.severity,
          duration: symptom.duration,
          description: symptom.characteristics?.join('，')
        });
      }
    });
    
    // 将剩余高置信度的症状作为次症
    sortedSymptoms.slice(3).forEach(symptom => {
      if ((symptom.severity && symptom.severity >= 5) || 
          (symptom.confidence && symptom.confidence >= 0.7)) {
        categorizedSymptoms.push({
          name: symptom.name,
          category: SymptomCategory.SECONDARY,
          severity: symptom.severity,
          duration: symptom.duration,
          description: symptom.characteristics?.join('，')
        });
      } else {
        // 其他症状作为兼症
        categorizedSymptoms.push({
          name: symptom.name,
          category: SymptomCategory.ACCOMPANYING,
          severity: symptom.severity,
          duration: symptom.duration,
          description: symptom.characteristics?.join('，')
        });
      }
    });
    
    return categorizedSymptoms;
  }
  
  /**
   * 识别中医辨证分型
   * @param symptoms 症状数组
   * @param patientInfo 患者信息
   * @returns 中医辨证分型数组
   */
  private async identifyTCMPatterns(symptoms: any[], patientInfo?: any): Promise<TCMPattern[]> {
    try {
      // TODO: 调用中医辨证服务进行分析
      // 实际项目中应该调用专门的中医辨证服务
      /*
      const response = await axios.post('http://localhost:3008/api/tcm/pattern-identification', {
        symptoms,
        patientInfo
      });
      return response.data.patterns;
      */
      
      // 模拟中医辨证结果
      const mockPatterns: TCMPattern[] = [
        {
          name: '肝郁气滞',
          confidence: 0.85,
          description: '肝气郁结，气机不畅，以胸胁、情志症状为主。',
          relatedSymptoms: ['胸胁胀痛', '情绪抑郁', '嗳气叹息', '脘腹胀满']
        },
        {
          name: '脾虚湿困',
          confidence: 0.72,
          description: '脾失健运，水湿内停，以消化、代谢症状为主。',
          relatedSymptoms: ['腹胀', '食欲不振', '大便溏薄', '倦怠乏力']
        }
      ];
      
      return mockPatterns;
    } catch (error) {
      this.logger.error('中医辨证分析失败', { error });
      throw new AIServiceError('中医辨证分析失败，请稍后再试');
    }
  }
  
  /**
   * 分析体质类型
   * @param symptoms 症状数组
   * @param tcmPatterns 中医辨证分型
   * @param patientInfo 患者信息
   * @returns 体质分析结果
   */
  private async analyzeConstitution(
    symptoms: any[], 
    tcmPatterns: TCMPattern[], 
    patientInfo?: any
  ): Promise<ConstitutionAnalysis> {
    try {
      // TODO: 调用体质辨识服务进行分析
      // 实际项目中应该调用专门的体质辨识服务
      /*
      const response = await axios.post('http://localhost:3009/api/tcm/constitution-analysis', {
        symptoms,
        tcmPatterns,
        patientInfo
      });
      return response.data.constitutionAnalysis;
      */
      
      // 模拟体质分析结果
      const constitutionAnalysis: ConstitutionAnalysis = {
        primaryType: ConstitutionType.QI_STAGNATION,
        secondaryTypes: [ConstitutionType.PHLEGM_DAMPNESS],
        description: '以气郁体质为主，兼有痰湿体质特征。气机不畅，情志不舒，湿邪内蕴。',
        deviationLevel: 6,
        scoreDetails: {
          [ConstitutionType.BALANCED]: 35,
          [ConstitutionType.QI_STAGNATION]: 78,
          [ConstitutionType.PHLEGM_DAMPNESS]: 65,
          [ConstitutionType.DAMP_HEAT]: 45,
          [ConstitutionType.BLOOD_STASIS]: 40,
          [ConstitutionType.QI_DEFICIENCY]: 50,
          [ConstitutionType.YANG_DEFICIENCY]: 30,
          [ConstitutionType.YIN_DEFICIENCY]: 25,
          [ConstitutionType.SPECIAL]: 10
        }
      };
      
      return constitutionAnalysis;
    } catch (error) {
      this.logger.error('体质分析失败', { error });
      throw new AIServiceError('体质分析失败，请稍后再试');
    }
  }
  
  /**
   * 生成健康建议
   * @param tcmPatterns 中医辨证分型
   * @param constitutionAnalysis 体质分析
   * @param categorizedSymptoms 分类症状
   * @param preferences 偏好设置
   * @returns 健康建议数组
   */
  private async generateRecommendations(
    tcmPatterns: TCMPattern[],
    constitutionAnalysis: ConstitutionAnalysis,
    categorizedSymptoms: CategorizedSymptom[],
    preferences?: any
  ): Promise<HealthRecommendation[]> {
    try {
      // TODO: 调用健康建议生成服务
      // 实际项目中应该调用专门的健康建议生成服务
      /*
      const response = await axios.post('http://localhost:3010/api/tcm/health-recommendations', {
        tcmPatterns,
        constitutionAnalysis,
        categorizedSymptoms,
        preferences
      });
      return response.data.recommendations;
      */
      
      // 模拟健康建议
      const recommendations: HealthRecommendation[] = [
        {
          type: RecommendationType.DIETARY,
          content: '饮食宜清淡，忌辛辣刺激食物，多食用具有疏肝理气作用的食材，如柑橘、薄荷、山楂等。',
          reason: '针对肝郁气滞证和气郁体质特点，疏肝理气饮食有助于改善症状。',
          priority: 5
        },
        {
          type: RecommendationType.LIFESTYLE,
          content: '保持情绪舒畅，避免过度紧张和焦虑；规律作息，避免熬夜；适当进行户外活动，增加阳光接触。',
          reason: '情志因素是导致肝气郁结的主要原因，调畅情志为治本之策。',
          priority: 5
        },
        {
          type: RecommendationType.EXERCISE,
          content: '建议进行舒缓性运动，如太极拳、八段锦、健步走等，每日30-60分钟，以微微出汗为度。',
          reason: '适当运动可促进气血运行，缓解气机郁滞。',
          priority: 4
        },
        {
          type: RecommendationType.HERBS,
          content: '可食用具有健脾化湿作用的食材，如薏苡仁、赤小豆、山药、茯苓等制成粥品食用。',
          reason: '针对脾虚湿困和痰湿体质特点，健脾化湿食材有助于消除湿邪。',
          priority: 4
        },
        {
          type: RecommendationType.MEDITATION,
          content: '每日可进行腹式呼吸练习15-20分钟，或练习导引术，帮助调整气息，疏通气机。',
          reason: '调息法有助于疏通气机，缓解情绪郁结。',
          priority: 3
        }
      ];
      
      return recommendations;
    } catch (error) {
      this.logger.error('生成健康建议失败', { error });
      throw new AIServiceError('生成健康建议失败，请稍后再试');
    }
  }
  
  /**
   * 生成诊断总结
   * @param tcmPatterns 中医辨证分型
   * @param constitutionAnalysis 体质分析
   * @param categorizedSymptoms 分类症状
   * @param recommendations 健康建议
   * @param preferences 偏好设置
   * @returns 诊断总结文本
   */
  private async generateSummary(
    tcmPatterns: TCMPattern[],
    constitutionAnalysis: ConstitutionAnalysis,
    categorizedSymptoms: CategorizedSymptom[],
    recommendations: HealthRecommendation[],
    preferences?: any
  ): Promise<string> {
    try {
      // TODO: 调用总结生成服务
      // 实际项目中应该调用专门的总结生成服务
      /*
      const response = await axios.post('http://localhost:3011/api/tcm/diagnosis-summary', {
        tcmPatterns,
        constitutionAnalysis,
        categorizedSymptoms,
        recommendations,
        preferences
      });
      return response.data.summary;
      */
      
      // 模拟诊断总结
      const useTCMTerminology = preferences?.useTCMTerminology ?? true;
      const mainPatterns = tcmPatterns.map(p => p.name).join('兼');
      const mainSymptoms = categorizedSymptoms
        .filter(s => s.category === SymptomCategory.MAIN)
        .map(s => s.name)
        .join('、');
      
      let summary = '';
      
      if (useTCMTerminology) {
        summary = `根据您的症状描述，结合中医四诊合参，辨证为${mainPatterns}。主症表现为${mainSymptoms}。体质辨识结果显示您属于${constitutionAnalysis.primaryType}`;
        
        if (constitutionAnalysis.secondaryTypes && constitutionAnalysis.secondaryTypes.length > 0) {
          summary += `，兼有${constitutionAnalysis.secondaryTypes.join('、')}特征`;
        }
        
        summary += '。建议从调畅情志、合理饮食、适当运动等方面进行综合调理，以疏肝理气、健脾化湿为原则，逐步改善体质偏颇，恢复阴阳平衡。';
      } else {
        summary = `根据您提供的健康信息和症状描述，分析您目前的主要健康问题是${mainPatterns}综合征，主要表现为${mainSymptoms}等症状。您的体质类型偏向${constitutionAnalysis.primaryType}`;
        
        if (constitutionAnalysis.secondaryTypes && constitutionAnalysis.secondaryTypes.length > 0) {
          summary += `，同时有${constitutionAnalysis.secondaryTypes.join('和')}的特点`;
        }
        
        summary += '。建议您注意情绪管理，保持饮食清淡，规律作息，适量运动，通过综合调理方式改善目前的健康状况。';
      }
      
      return summary;
    } catch (error) {
      this.logger.error('生成诊断总结失败', { error });
      // 返回简单总结而不是抛出异常，确保流程可以继续
      return '根据症状分析，建议您注意调整生活方式，保持情绪舒畅，饮食清淡，适当运动，有助于改善当前健康状况。';
    }
  }
  
  /**
   * 生成后续问题
   * @param tcmPatterns 中医辨证分型
   * @param categorizedSymptoms 分类症状
   * @returns 后续问题数组
   */
  private async generateFollowUpQuestions(
    tcmPatterns: TCMPattern[],
    categorizedSymptoms: CategorizedSymptom[]
  ): Promise<string[]> {
    try {
      // 基于中医辨证分型和症状生成相关的后续问题
      const questions: string[] = [];
      
      // 针对肝郁气滞的后续问题
      if (tcmPatterns.some(p => p.name.includes('肝郁') || p.name.includes('气滞'))) {
        questions.push('您的情绪波动与症状加重是否有明显关联？');
        questions.push('您是否经常感到胸闷、叹息或胸胁部不适？');
      }
      
      // 针对脾虚湿困的后续问题
      if (tcmPatterns.some(p => p.name.includes('脾虚') || p.name.includes('湿困'))) {
        questions.push('您的消化功能如何？是否容易腹胀或食欲不振？');
        questions.push('您是否容易感到疲倦，特别是饭后或湿度较大的天气？');
      }
      
      // 针对未确认症状的问题
      const mainSymptoms = categorizedSymptoms.filter(s => s.category === SymptomCategory.MAIN);
      for (const symptom of mainSymptoms) {
        if (!symptom.duration) {
          questions.push(`您的${symptom.name}症状持续了多长时间？`);
        }
        if (!symptom.description) {
          questions.push(`能否详细描述一下${symptom.name}的具体表现？`);
        }
      }
      
      // 一般性后续问题
      questions.push('您的睡眠质量如何？是否容易入睡，睡眠是否充足？');
      questions.push('您平时有哪些运动习惯？频率和强度如何？');
      
      return questions.slice(0, 5); // 限制返回的问题数量
    } catch (error) {
      this.logger.error('生成后续问题失败', { error });
      // 返回默认问题而不是抛出异常，确保流程可以继续
      return [
        '您的症状持续多久了？',
        '您平时的饮食习惯如何？',
        '您的睡眠质量如何？'
      ];
    }
  }
  
  /**
   * 评估警告指标
   * @param categorizedSymptoms 分类症状
   * @param tcmPatterns 中医辨证分型
   * @returns 警告指标数组
   */
  private evaluateWarningIndicators(
    categorizedSymptoms: CategorizedSymptom[],
    tcmPatterns: TCMPattern[]
  ): Array<{level: 'low' | 'medium' | 'high', content: string, suggestedAction: string}> {
    const warningIndicators: Array<{
      level: 'low' | 'medium' | 'high', 
      content: string, 
      suggestedAction: string
    }> = [];
    
    // 检查高严重度症状
    const severeSymptoms = categorizedSymptoms.filter(s => s.severity && s.severity >= 8);
    if (severeSymptoms.length > 0) {
      warningIndicators.push({
        level: 'medium',
        content: `存在${severeSymptoms.length}项严重症状：${severeSymptoms.map(s => s.name).join('、')}`,
        suggestedAction: '建议密切关注症状变化，若症状持续加重，请及时就医。'
      });
    }
    
    // 检查特定敏感症状
    const sensitiveSymptoms = ['胸痛', '头痛', '呼吸困难', '晕厥', '剧烈腹痛'];
    const hasSensitiveSymptoms = categorizedSymptoms.some(s => 
      sensitiveSymptoms.some(sensitive => s.name.includes(sensitive))
    );
    
    if (hasSensitiveSymptoms) {
      warningIndicators.push({
        level: 'high',
        content: '存在需要警惕的敏感症状，可能需要进一步医学评估。',
        suggestedAction: '建议尽快就医进行专业检查，排除潜在的急性病症。'
      });
    }
    
    // 根据辨证分型进行评估
    const specificPatterns = ['血瘀', '阴虚火旺', '阳虚寒凝'];
    const hasSpecificPattern = tcmPatterns.some(p => 
      specificPatterns.some(pattern => p.name.includes(pattern))
    );
    
    if (hasSpecificPattern) {
      warningIndicators.push({
        level: 'low',
        content: '辨证结果显示存在需要关注的证型，建议适当调理。',
        suggestedAction: '建议遵循健康建议进行调理，并在1-2个月内进行复诊评估。'
      });
    }
    
    return warningIndicators;
  }
  
  /**
   * 计算整体诊断置信度
   * @param tcmPatterns 中医辨证分型
   * @param categorizedSymptoms 分类症状
   * @returns 整体置信度 (0-1)
   */
  private calculateOverallConfidence(
    tcmPatterns: TCMPattern[],
    categorizedSymptoms: CategorizedSymptom[]
  ): number {
    // 证型平均置信度
    const patternConfidenceAvg = tcmPatterns.reduce(
      (sum, pattern) => sum + pattern.confidence, 
      0
    ) / tcmPatterns.length;
    
    // 主症数量因子
    const mainSymptomsCount = categorizedSymptoms.filter(
      s => s.category === SymptomCategory.MAIN
    ).length;
    const mainSymptomsFactor = Math.min(1, mainSymptomsCount / 3);
    
    // 症状与证型匹配度
    const mainSymptoms = categorizedSymptoms
      .filter(s => s.category === SymptomCategory.MAIN)
      .map(s => s.name);
    
    let matchCount = 0;
    let totalRelatedSymptoms = 0;
    
    tcmPatterns.forEach(pattern => {
      if (pattern.relatedSymptoms) {
        totalRelatedSymptoms += pattern.relatedSymptoms.length;
        pattern.relatedSymptoms.forEach(symptom => {
          if (mainSymptoms.some(s => s.includes(symptom) || symptom.includes(s))) {
            matchCount++;
          }
        });
      }
    });
    
    const matchFactor = totalRelatedSymptoms > 0 
      ? matchCount / totalRelatedSymptoms 
      : 0.5;
    
    // 计算加权置信度
    const weightedConfidence = (
      patternConfidenceAvg * 0.5 + 
      mainSymptomsFactor * 0.3 + 
      matchFactor * 0.2
    );
    
    return Math.round(weightedConfidence * 100) / 100;
  }

  /**
   * 获取四诊协调综合诊断结果
   * @param sessionId 会话ID
   * @returns 综合诊断结果
   */
  async getIntegratedDiagnosis(sessionId: string): Promise<any> {
    this.logger.info(`获取综合四诊结果，会话ID: ${sessionId}`);
    
    try {
      // 从四诊协调服务获取综合结果
      const integratedResult = await this.coordinatorService.getIntegratedDiagnosis(sessionId);
      
      if (!integratedResult) {
        this.logger.warn(`未获取到综合四诊结果，会话ID: ${sessionId}`);
        return null;
      }
      
      this.logger.info(`成功获取综合四诊结果，会话ID: ${sessionId}`);
      return integratedResult;
    } catch (error) {
      this.logger.error(`获取综合四诊结果失败: ${error.message}`);
      throw error;
    }
  }
}