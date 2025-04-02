import { Service } from 'typedi';
import { v4 as uuidv4 } from 'uuid';
import { SmellDiagnosisRequest, SmellDiagnosisType, SmellType, TcmAspect, SampleType } from '../interfaces/smell-diagnosis.interface';
import { SmellAnalysisResultModel, SmellDiagnosisResultModel } from '../models/smell-diagnosis.model';
import { Logger } from '../utils/logger';
import { SmellDiagnosisRepository } from '../repositories/smell-diagnosis.repository';
import { AudioAnalyzerService } from './audio/audio-analyzer.service';

@Service()
export class SmellDiagnosisService {
  private logger: Logger;

  constructor(
    private repository: SmellDiagnosisRepository,
    private audioAnalyzer: AudioAnalyzerService
  ) {
    this.logger = new Logger('SmellDiagnosisService');
  }

  /**
   * 处理闻诊分析请求
   * @param request 闻诊请求
   * @returns 闻诊结果
   */
  async analyzeSmell(request: SmellDiagnosisRequest): Promise<SmellDiagnosisResultModel> {
    this.logger.info('开始闻诊分析', { userId: request.userId, diagnosisType: request.diagnosisType });
    
    try {
      // 根据请求类型执行分析
      const analysisResults = await this.performSmellAnalysis(request);
      
      // 获取中医理论意义
      const tcmImplications = this.generateTcmImplications(analysisResults);
      
      // 生成推荐
      const recommendations = this.generateRecommendations(analysisResults, tcmImplications);
      
      // 计算综合置信度
      const confidence = this.calculateConfidence(analysisResults);
      
      // 创建结果
      const result = new SmellDiagnosisResultModel({
        userId: request.userId,
        requestId: uuidv4(),
        diagnosisType: request.diagnosisType,
        analysisResults,
        tcmImplications,
        recommendations,
        confidence,
        metadata: request.metadata
      });
      
      // 保存分析结果到数据库
      const savedAnalysisResults = [];
      for (const analysisResult of analysisResults) {
        const savedResult = await this.repository.saveAnalysisResult(analysisResult);
        savedAnalysisResults.push(savedResult._id.toString());
      }
      
      // 保存诊断结果到数据库
      await this.repository.saveDiagnosisResult(result, savedAnalysisResults);
      
      this.logger.info('闻诊分析完成', { resultId: result.id, confidence });
      
      return result;
    } catch (error) {
      this.logger.error('闻诊分析失败', { error: (error as Error).message, stack: (error as Error).stack });
      throw error;
    }
  }
  
  /**
   * 获取用户闻诊历史记录
   * @param userId 用户ID
   * @param limit 限制条数
   * @param skip 跳过条数
   */
  async getUserDiagnosisHistory(
    userId: string,
    limit: number = 20,
    skip: number = 0
  ): Promise<SmellDiagnosisResultModel[]> {
    this.logger.info('获取用户闻诊历史', { userId, limit, skip });
    
    try {
      return await this.repository.getUserDiagnosisHistory(userId, limit, skip);
    } catch (error) {
      this.logger.error('获取用户闻诊历史失败', { error: (error as Error).message });
      throw error;
    }
  }
  
  /**
   * 根据ID获取闻诊结果
   * @param id 闻诊结果ID
   */
  async getDiagnosisResultById(id: string): Promise<SmellDiagnosisResultModel | null> {
    this.logger.info('根据ID获取闻诊结果', { id });
    
    try {
      return await this.repository.getDiagnosisResultById(id);
    } catch (error) {
      this.logger.error('根据ID获取闻诊结果失败', { error: (error as Error).message });
      throw error;
    }
  }

  /**
   * 执行气味分析
   * @param request 闻诊请求
   * @returns 气味分析结果数组
   */
  private async performSmellAnalysis(request: SmellDiagnosisRequest): Promise<SmellAnalysisResultModel[]> {
    // 检查是否是音频样本
    if (request.sampleType === SampleType.AUDIO && request.audioData) {
      return await this.analyzeAudioSample(request);
    }
    
    // 文本描述分析
    return await this.analyzeTextDescription(request);
  }
  
  /**
   * 分析音频样本
   * @param request 闻诊请求
   * @returns 气味分析结果数组
   */
  private async analyzeAudioSample(request: SmellDiagnosisRequest): Promise<SmellAnalysisResultModel[]> {
    this.logger.info('分析音频样本', { 
      userId: request.userId,
      diagnosisType: request.diagnosisType,
      audioDataSize: request.audioData instanceof Buffer ? request.audioData.length : 'unknown'
    });
    
    // 确保有音频数据
    if (!request.audioData || !(request.audioData instanceof Buffer)) {
      throw new Error('无效的音频数据');
    }
    
    // 使用音频分析服务分析
    const audioAnalysisResult = await this.audioAnalyzer.analyzeAudioData(request.audioData);
    
    // 根据分析结果生成闻诊结果
    const result = new SmellAnalysisResultModel({
      userId: request.userId,
      smellType: audioAnalysisResult.smellType,
      intensity: audioAnalysisResult.intensity,
      description: this.generateDescriptionFromAudio(audioAnalysisResult, request.diagnosisType),
      relatedConditions: this.getRelatedConditionsForSmell(audioAnalysisResult.smellType),
      confidence: audioAnalysisResult.confidence,
      rawData: { audioFeatures: audioAnalysisResult.features },
      metadata: { 
        ...request.metadata,
        audioDuration: audioAnalysisResult.duration
      }
    });
    
    return [result];
  }
  
  /**
   * 根据音频分析结果生成描述
   * @param audioResult 音频分析结果
   * @param diagnosisType 诊断类型
   * @returns 描述文本
   */
  private generateDescriptionFromAudio(
    audioResult: any,
    diagnosisType: SmellDiagnosisType
  ): string {
    // 根据诊断类型和气味类型生成不同的描述
    switch (diagnosisType) {
      case SmellDiagnosisType.BREATH:
        return `呼吸声分析检测到${this.getSmellTypeDescription(audioResult.smellType)}气息，` +
               `强度为${audioResult.intensity.toFixed(1)}，` + 
               `可能表示${this.getHealthImplicationForSmellType(audioResult.smellType, diagnosisType)}`;
        
      case SmellDiagnosisType.MOUTH:
        return `口腔气息分析检测到${this.getSmellTypeDescription(audioResult.smellType)}气息，` +
               `强度为${audioResult.intensity.toFixed(1)}，` + 
               `提示${this.getHealthImplicationForSmellType(audioResult.smellType, diagnosisType)}`;
        
      default:
        return `声音分析检测到${this.getSmellTypeDescription(audioResult.smellType)}特征，` +
               `强度为${audioResult.intensity.toFixed(1)}`;
    }
  }
  
  /**
   * 分析文本描述
   * @param request 闻诊请求
   * @returns 气味分析结果数组
   */
  private async analyzeTextDescription(request: SmellDiagnosisRequest): Promise<SmellAnalysisResultModel[]> {
    // 基本的文本分析实现
    // 在实际项目中，这里会调用NLP模型或关键词匹配算法
    // 目前使用模拟数据

    let primarySmellType: SmellType;
    let secondarySmellType: SmellType | null = null;
    let intensity = 5 + Math.random() * 5;
    let description = '';
    let relatedConditions: string[] = [];
    
    // 如果有描述文本，尝试从中提取关键词
    if (request.description) {
      // 简单关键词匹配
      if (request.description.includes('酸') || request.description.includes('sour')) {
        primarySmellType = SmellType.SOUR;
        intensity = 7 + Math.random() * 3;
      } else if (request.description.includes('甜') || request.description.includes('sweet')) {
        primarySmellType = SmellType.SWEET;
        intensity = 6 + Math.random() * 4;
      } else if (request.description.includes('苦') || request.description.includes('bitter')) {
        primarySmellType = SmellType.BITTER;
        intensity = 8 + Math.random() * 2;
      } else if (request.description.includes('腥') || request.description.includes('fishy')) {
        primarySmellType = SmellType.FISHY;
        intensity = 7 + Math.random() * 3;
      } else if (request.description.includes('臭') || request.description.includes('foul')) {
        primarySmellType = SmellType.FOUL;
        intensity = 8 + Math.random() * 2;
      } else if (request.description.includes('腐') || request.description.includes('putrid')) {
        primarySmellType = SmellType.PUTRID;
        intensity = 9 + Math.random();
      } else if (request.description.includes('焦') || request.description.includes('scorch')) {
        primarySmellType = SmellType.SCORCHED;
        intensity = 7 + Math.random() * 3;
      } else {
        // 默认值
        primarySmellType = this.getDefaultSmellTypeForDiagnosisType(request.diagnosisType);
      }
    } else {
      // 没有描述文本时使用默认值
      primarySmellType = this.getDefaultSmellTypeForDiagnosisType(request.diagnosisType);
    }
    
    // 确保强度在1-10范围内
    intensity = Math.min(Math.max(intensity, 1), 10);
    
    // 根据诊断类型生成描述
    description = this.generateDescriptionForSmellType(primarySmellType, request.diagnosisType, intensity);
    
    // 获取相关症状
    relatedConditions = this.getRelatedConditionsForSmell(primarySmellType);
    
    // 创建主要气味分析结果
    const primaryResult = new SmellAnalysisResultModel({
      userId: request.userId,
      smellType: primarySmellType,
      intensity,
      description,
      relatedConditions,
      confidence: 0.7 + Math.random() * 0.3
    });
    
    // 可能的次要气味分析结果
    const results: SmellAnalysisResultModel[] = [primaryResult];
    
    // 随机决定是否添加次要气味（约30%概率）
    if (Math.random() > 0.7) {
      // 选择一个不同的气味类型作为次要气味
      do {
        secondarySmellType = this.getRandomSmellType();
      } while (secondarySmellType === primarySmellType);
      
      // 次要气味的强度和置信度较低
      const secondaryResult = new SmellAnalysisResultModel({
        userId: request.userId,
        smellType: secondarySmellType,
        intensity: intensity * 0.6,
        description: `次要气味：${this.getSmellTypeDescription(secondarySmellType)}，较为轻微`,
        relatedConditions: this.getRelatedConditionsForSmell(secondarySmellType).slice(0, 1),
        confidence: 0.5 + Math.random() * 0.2
      });
      
      results.push(secondaryResult);
    }
    
    return results;
  }
  
  /**
   * 根据诊断类型获取默认气味类型
   * @param diagnosisType 诊断类型
   * @returns 默认气味类型
   */
  private getDefaultSmellTypeForDiagnosisType(diagnosisType: SmellDiagnosisType): SmellType {
    switch (diagnosisType) {
      case SmellDiagnosisType.BREATH:
        return Math.random() > 0.5 ? SmellType.SOUR : SmellType.SWEET;
      case SmellDiagnosisType.SWEAT:
        return Math.random() > 0.5 ? SmellType.FISHY : SmellType.FOUL;
      case SmellDiagnosisType.EXCRETION:
        return Math.random() > 0.5 ? SmellType.PUTRID : SmellType.FOUL;
      case SmellDiagnosisType.MOUTH:
        return SmellType.FOUL;
      case SmellDiagnosisType.BODY:
        return Math.random() > 0.5 ? SmellType.FISHY : SmellType.FOUL;
      default:
        return SmellType.NORMAL;
    }
  }
  
  /**
   * 获取随机气味类型
   * @returns 随机气味类型
   */
  private getRandomSmellType(): SmellType {
    const smellTypes = [
      SmellType.SOUR,
      SmellType.SWEET,
      SmellType.BITTER,
      SmellType.FISHY,
      SmellType.FOUL,
      SmellType.PUTRID,
      SmellType.SCORCHED
    ];
    
    return smellTypes[Math.floor(Math.random() * smellTypes.length)];
  }
  
  /**
   * 获取气味类型的描述
   * @param smellType 气味类型
   * @returns 描述
   */
  private getSmellTypeDescription(smellType: SmellType): string {
    switch (smellType) {
      case SmellType.SOUR:
        return '酸';
      case SmellType.SWEET:
        return '甜';
      case SmellType.BITTER:
        return '苦';
      case SmellType.FISHY:
        return '腥';
      case SmellType.FOUL:
        return '臭';
      case SmellType.PUTRID:
        return '腐';
      case SmellType.SCORCHED:
        return '焦';
      case SmellType.FRAGRANT:
        return '芳香';
      case SmellType.ROTTEN:
        return '腐败';
      case SmellType.NORMAL:
        return '正常';
      default:
        return '未知';
    }
  }
  
  /**
   * 为气味类型生成健康含义
   * @param smellType 气味类型
   * @param diagnosisType 诊断类型
   * @returns 健康含义描述
   */
  private getHealthImplicationForSmellType(smellType: SmellType, diagnosisType: SmellDiagnosisType): string {
    // 组合诊断类型和气味类型生成健康含义
    if (diagnosisType === SmellDiagnosisType.BREATH) {
      switch (smellType) {
        case SmellType.SOUR:
          return '肝胆功能失调，气机郁滞';
        case SmellType.SWEET:
          return '血糖代谢异常，可能有内热';
        case SmellType.BITTER:
          return '心火旺盛，或胆热内扰';
        case SmellType.FISHY:
          return '肾阳虚衰，或痰浊内阻';
        case SmellType.FOUL:
          return '胃肠积热，或有食滞';
        default:
          return '气血运行不畅';
      }
    } else if (diagnosisType === SmellDiagnosisType.MOUTH) {
      switch (smellType) {
        case SmellType.SOUR:
          return '胃酸过多，或肝气犯胃';
        case SmellType.SWEET:
          return '脾胃湿热，或有糖尿';
        case SmellType.BITTER:
          return '胆热上炎，或有热毒';
        case SmellType.FOUL:
          return '胃热炽盛，或肠胃不和';
        default:
          return '口腔环境失衡';
      }
    }
    
    // 其他类型
    return '体内环境可能存在异常';
  }
  
  /**
   * 为气味类型和诊断类型生成描述
   * @param smellType 气味类型
   * @param diagnosisType 诊断类型
   * @param intensity 强度
   * @returns 描述
   */
  private generateDescriptionForSmellType(
    smellType: SmellType,
    diagnosisType: SmellDiagnosisType,
    intensity: number
  ): string {
    const intensityDesc = intensity > 8 
      ? '强烈的' 
      : intensity > 5 
        ? '明显的'
        : '轻微的';
    
    const smellDesc = this.getSmellTypeDescription(smellType);
    const healthImplication = this.getHealthImplicationForSmellType(smellType, diagnosisType);
    
    switch (diagnosisType) {
      case SmellDiagnosisType.BREATH:
        return `呼吸中带有${intensityDesc}${smellDesc}味，提示可能${healthImplication}`;
      case SmellDiagnosisType.SWEAT:
        return `汗液带有${intensityDesc}${smellDesc}味，可能与体内湿热或代谢异常有关`;
      case SmellDiagnosisType.EXCRETION:
        return `排泄物带有${intensityDesc}${smellDesc}味，提示消化系统可能存在问题`;
      case SmellDiagnosisType.MOUTH:
        return `口气呈${intensityDesc}${smellDesc}味，提示${healthImplication}`;
      case SmellDiagnosisType.BODY:
        return `体表散发${intensityDesc}${smellDesc}味，可能与血液循环或代谢异常有关`;
      default:
        return `检测到${intensityDesc}${smellDesc}味`;
    }
  }
  
  /**
   * 获取与气味相关的症状
   * @param smellType 气味类型
   * @returns 相关症状数组
   */
  private getRelatedConditionsForSmell(smellType: SmellType): string[] {
    switch (smellType) {
      case SmellType.SOUR:
        return ['肝郁气滞', '胆热', '肝胆湿热', '情志不畅'];
      case SmellType.SWEET:
        return ['脾虚湿困', '血糖异常', '痰湿内生', '脾胃不和'];
      case SmellType.BITTER:
        return ['心火旺', '胆热犯胃', '热毒内盛', '阴虚内热'];
      case SmellType.FISHY:
        return ['血瘀', '湿热蕴结', '肾气亏虚', '痰浊内阻'];
      case SmellType.FOUL:
        return ['胃热上炎', '肺热', '肠胃不和', '食滞中阻'];
      case SmellType.PUTRID:
        return ['脾胃虚弱', '湿热下注', '肠胃积滞', '气血瘀阻'];
      case SmellType.SCORCHED:
        return ['阴虚火旺', '胃阴不足', '肝火上炎', '气血耗伤'];
      case SmellType.NORMAL:
        return [];
      default:
        return ['气血失调'];
    }
  }
  
  /**
   * 生成中医理论意义解释
   * @param analysisResults 气味分析结果
   * @returns 中医理论意义数组
   */
  private generateTcmImplications(analysisResults: SmellAnalysisResultModel[]): any[] {
    // 简单示例实现
    const implications = [];
    
    for (const result of analysisResults) {
      // 根据气味类型推断中医理论意义
      switch (result.smellType) {
        case SmellType.SOUR:
          implications.push({
            aspect: TcmAspect.FIVE_ELEMENTS,
            description: '酸味属木，主肝。提示肝气郁结或肝胆功能异常。',
            significance: 7
          });
          implications.push({
            aspect: TcmAspect.ZANG_FU,
            description: '肝胆功能失调，可能出现情志不畅、胁肋胀痛等症状。',
            significance: 8
          });
          break;
          
        case SmellType.SWEET:
          implications.push({
            aspect: TcmAspect.FIVE_ELEMENTS,
            description: '甜味属土，主脾。提示脾胃功能失调，痰湿内生。',
            significance: 7
          });
          implications.push({
            aspect: TcmAspect.YIN_YANG,
            description: '阴虚内热，消耗津液，代谢异常。',
            significance: 6
          });
          break;
          
        case SmellType.FISHY:
          implications.push({
            aspect: TcmAspect.QI_BLOOD,
            description: '血瘀或血热，可能有血液循环障碍。',
            significance: 8
          });
          break;
          
        case SmellType.FOUL:
          implications.push({
            aspect: TcmAspect.SIX_EXCESSES,
            description: '湿热内蕴，影响气机升降，导致代谢废物排泄不畅。',
            significance: 7
          });
          break;
      }
    }
    
    return implications;
  }
  
  /**
   * 生成调理建议
   * @param analysisResults 气味分析结果
   * @param tcmImplications 中医理论意义
   * @returns 调理建议数组
   */
  private generateRecommendations(analysisResults: SmellAnalysisResultModel[], tcmImplications: any[]): string[] {
    // 简单示例实现
    const recommendations: string[] = [];
    
    for (const result of analysisResults) {
      switch (result.smellType) {
        case SmellType.SOUR:
          recommendations.push('疏肝理气，可食用柴胡、陈皮等食材');
          recommendations.push('保持情绪舒畅，避免过度抑郁或发怒');
          recommendations.push('适当增加绿色蔬菜摄入，减少油腻食物');
          break;
          
        case SmellType.SWEET:
          recommendations.push('健脾化湿，可食用薏米、山药等食材');
          recommendations.push('控制甜食和精细碳水化合物摄入');
          recommendations.push('增加日常活动量，促进代谢');
          break;
          
        case SmellType.FISHY:
          recommendations.push('活血化瘀，可食用红花、桃仁等食材');
          recommendations.push('保持良好作息，避免熬夜');
          recommendations.push('增加适度有氧运动');
          break;
          
        case SmellType.FOUL:
          recommendations.push('清热利湿，可食用绿豆、苦瓜等食材');
          recommendations.push('避免辛辣刺激性食物');
          recommendations.push('保持大便通畅，多饮水');
          break;
          
        default:
          recommendations.push('保持规律作息，均衡饮食');
          recommendations.push('定期进行四诊检查，关注健康变化');
      }
    }
    
    // 去重
    return [...new Set(recommendations)];
  }
  
  /**
   * 计算综合置信度
   * @param analysisResults 气味分析结果数组
   * @returns 综合置信度
   */
  private calculateConfidence(analysisResults: SmellAnalysisResultModel[]): number {
    // 使用加权平均值计算总体置信度
    if (analysisResults.length === 0) {
      return 0;
    }
    
    let totalConfidence = 0;
    let totalWeight = 0;
    
    for (const result of analysisResults) {
      // 使用强度作为权重
      const weight = result.intensity;
      totalConfidence += result.confidence * weight;
      totalWeight += weight;
    }
    
    return totalWeight > 0 ? totalConfidence / totalWeight : 0;
  }
} 