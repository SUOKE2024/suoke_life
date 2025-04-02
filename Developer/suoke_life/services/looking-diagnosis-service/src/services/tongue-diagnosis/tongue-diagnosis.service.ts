import { Service } from 'typedi';
import { ImageProcessorService } from '../image-processing/image-processor.service';
import { Logger } from '../../utils/logger';
import { TongueDiagnosisResult, TongueFeatures } from '../../models/diagnosis/tongue.model';
import { TongueDiagnosisRepository } from '../../repositories/tongue-diagnosis.repository';
import { CoordinatorClientService } from '../four-diagnosis-coordinator/coordinator-client.service';

@Service()
export class TongueDiagnosisService {
  private logger = new Logger('TongueDiagnosisService');

  constructor(
    private imageProcessorService: ImageProcessorService,
    private tongueDiagnosisRepository: TongueDiagnosisRepository,
    private coordinatorClient: CoordinatorClientService
  ) {}

  /**
   * 分析舌象照片并生成诊断结果
   * @param imageBuffer 舌象照片图像缓冲区
   * @param sessionId 诊断会话ID
   * @param metadata 元数据信息
   * @param userId 可选的用户ID
   * @returns 舌诊分析结果
   */
  async analyze(imageBuffer: Buffer, sessionId: string, metadata: any, userId?: string): Promise<TongueDiagnosisResult> {
    try {
      this.logger.info(`开始舌诊分析，会话ID: ${sessionId}`);

      // 1. 预处理图像
      const processedImage = await this.imageProcessorService.preprocessImage(imageBuffer);
      
      // 2. 提取舌头区域
      const tongueRegion = await this.imageProcessorService.extractRegionOfInterest(processedImage, 'tongue');
      
      // 3. 去噪和增强
      const enhancedTongue = await this.imageProcessorService.enhanceImage(
        await this.imageProcessorService.denoiseImage(tongueRegion)
      );
      
      // 4. 提取舌头特征
      const imageFeatures = await this.imageProcessorService.extractImageFeatures(enhancedTongue);
      
      // 5. 分析舌头特征
      const tongueFeatures = await this.extractTongueFeatures(enhancedTongue, imageFeatures);
      
      // 6. 生成中医辨证结果
      const tcmImplications = await this.analyzeTCMImplications(tongueFeatures);
      
      // 7. 生成建议
      const recommendations = await this.generateRecommendations(tcmImplications);

      this.logger.info(`舌诊分析完成，会话ID: ${sessionId}`);
      
      // 8. 创建诊断结果
      const diagnosisResult: TongueDiagnosisResult = {
        diagnosisId: `ld-tongue-${Date.now()}`,
        sessionId,
        timestamp: new Date().toISOString(),
        features: tongueFeatures,
        tcmImplications,
        recommendations,
        metadata: {
          ...metadata,
          processingSteps: [
            '图像预处理',
            '舌头区域提取',
            '图像增强',
            '特征提取',
            'TCM辨证分析',
            '建议生成'
          ]
        }
      };
      
      // 9. 保存到数据库
      await this.tongueDiagnosisRepository.saveDiagnosis(diagnosisResult, userId);
      
      // 10. 上报结果到四诊协调服务
      this.coordinatorClient.reportTongueDiagnosis(diagnosisResult)
        .then(success => {
          if (success) {
            this.logger.info(`舌诊结果已上报到四诊协调服务，诊断ID: ${diagnosisResult.diagnosisId}`);
          } else {
            this.logger.warn(`舌诊结果上报失败，诊断ID: ${diagnosisResult.diagnosisId}`);
          }
        })
        .catch(error => {
          this.logger.error(`舌诊结果上报错误: ${error.message}`);
        });
      
      return diagnosisResult;
    } catch (error) {
      this.logger.error(`舌诊分析失败: ${error.message}`);
      throw new Error(`舌诊分析失败: ${error.message}`);
    }
  }

  /**
   * 根据诊断ID获取舌诊结果
   * @param diagnosisId 诊断ID
   * @returns 舌诊分析结果
   */
  async getDiagnosisById(diagnosisId: string): Promise<TongueDiagnosisResult | null> {
    try {
      this.logger.info(`获取舌诊结果，诊断ID: ${diagnosisId}`);
      
      // 从数据库获取诊断结果
      const diagnosis = await this.tongueDiagnosisRepository.getDiagnosisById(diagnosisId);
      
      if (!diagnosis) {
        return null;
      }
      
      // 转换为API响应格式
      const result: TongueDiagnosisResult = {
        diagnosisId: diagnosis.diagnosisId,
        sessionId: diagnosis.sessionId,
        timestamp: diagnosis.timestamp,
        features: diagnosis.features,
        tcmImplications: diagnosis.tcmImplications,
        recommendations: diagnosis.recommendations,
        metadata: diagnosis.metadata
      };
      
      return result;
    } catch (error) {
      this.logger.error(`获取舌诊结果失败: ${error.message}`);
      throw new Error(`获取舌诊结果失败: ${error.message}`);
    }
  }

  /**
   * 获取舌诊历史记录
   * @param userId 用户ID
   * @param sessionId 会话ID
   * @param limit 返回记录数限制
   * @param offset 分页偏移量
   * @returns 舌诊历史记录和总数
   */
  async getDiagnosisHistory(
    userId?: string,
    sessionId?: string,
    limit: number = 10,
    offset: number = 0
  ): Promise<{ records: TongueDiagnosisResult[]; total: number }> {
    try {
      this.logger.info(`获取舌诊历史记录，用户ID: ${userId}, 会话ID: ${sessionId}`);
      
      // 至少需要提供userId或sessionId之一
      if (!userId && !sessionId) {
        throw new Error('获取历史记录需要提供用户ID或会话ID');
      }
      
      // 从数据库获取历史记录
      const { results, total } = await this.tongueDiagnosisRepository.getDiagnosisHistory(
        { userId, sessionId },
        limit,
        offset
      );
      
      // 转换为API响应格式
      const records = results.map(doc => ({
        diagnosisId: doc.diagnosisId,
        sessionId: doc.sessionId,
        timestamp: doc.timestamp,
        features: doc.features,
        tcmImplications: doc.tcmImplications,
        recommendations: doc.recommendations,
        metadata: doc.metadata
      }));
      
      return { records, total };
    } catch (error) {
      this.logger.error(`获取舌诊历史记录失败: ${error.message}`);
      throw new Error(`获取舌诊历史记录失败: ${error.message}`);
    }
  }

  /**
   * 获取综合四诊结果
   * @param sessionId 会话ID
   * @returns 综合四诊结果
   */
  async getIntegratedDiagnosis(sessionId: string): Promise<any> {
    try {
      this.logger.info(`获取综合四诊结果，会话ID: ${sessionId}`);
      
      // 从四诊协调服务获取综合结果
      const integratedResult = await this.coordinatorClient.getIntegratedDiagnosis(sessionId);
      
      if (!integratedResult) {
        this.logger.warn(`未获取到综合四诊结果，会话ID: ${sessionId}`);
        return null;
      }
      
      this.logger.info(`成功获取综合四诊结果，会话ID: ${sessionId}`);
      return integratedResult;
    } catch (error) {
      this.logger.error(`获取综合四诊结果失败: ${error.message}`);
      throw new Error(`获取综合四诊结果失败: ${error.message}`);
    }
  }

  /**
   * 提取舌头特征
   * @param tongueImage 处理后的舌头图像
   * @param imageFeatures 基本图像特征
   * @returns 舌头特征
   */
  private async extractTongueFeatures(tongueImage: Buffer, imageFeatures: any): Promise<TongueFeatures> {
    try {
      this.logger.info('开始提取舌头特征');
      
      // 在实际实现中，这里应该使用更先进的图像分析/ML技术
      // 以下是基于简单规则的舌象特征分析模拟

      // 基于红色通道分析舌质颜色
      const redChannel = imageFeatures.colorStats[0];
      let tongueColor = '淡红';
      
      if (redChannel.mean > 180) {
        tongueColor = '淡白';
      } else if (redChannel.mean > 140) {
        tongueColor = '淡红';
      } else if (redChannel.mean > 100) {
        tongueColor = '红';
      } else if (redChannel.mean > 80) {
        tongueColor = '绛';
      } else {
        tongueColor = '紫暗';
      }
      
      // 基于明度分析舌苔
      let tongueCoating = '薄白';
      if (imageFeatures.brightness > 70) {
        tongueCoating = '厚白';
      } else if (imageFeatures.brightness > 50) {
        tongueCoating = '薄白';
      } else if (imageFeatures.brightness > 40) {
        tongueCoating = '薄黄';
      } else {
        tongueCoating = '黄腻';
      }
      
      // 根据RGB分布分析舌体状态
      let tongueShape = '正常';
      let moisture = '适中';
      
      // 在实际实现中，这里应该基于边缘检测和形态分析
      // 如果红/蓝通道比值高，通常表示较干燥
      const dryness = redChannel.mean / imageFeatures.colorStats[2].mean;
      if (dryness > 1.8) {
        moisture = '干燥';
      } else if (dryness < 1.2) {
        moisture = '偏湿';
      }
      
      // 在此添加更详细的形态分析...
      
      this.logger.info('舌头特征提取完成');
      return {
        tongueColor,
        tongueShape,
        tongueCoating,
        moisture,
        cracks: false, // 在实际实现中应检测裂纹
        spots: false,  // 在实际实现中应检测斑点
        teethMarks: false, // 在实际实现中应检测齿痕
        deviation: false // 在实际实现中应检测偏斜
      };
    } catch (error) {
      this.logger.error(`提取舌头特征失败: ${error.message}`);
      throw new Error(`提取舌头特征失败: ${error.message}`);
    }
  }

  /**
   * 分析中医辨证含义
   * @param features 舌头特征
   * @returns 中医辨证结果
   */
  private async analyzeTCMImplications(features: TongueFeatures): Promise<Array<{concept: string, confidence: number}>> {
    try {
      this.logger.info('开始分析中医辨证含义');
      
      // 在实际实现中，这里应该使用更复杂的推理模型或知识图谱
      // 以下是基于简单规则的辨证分析
      
      const implications: Array<{concept: string, confidence: number}> = [];
      
      // 分析舌质颜色的辨证意义
      switch (features.tongueColor) {
        case '淡白':
          implications.push({ concept: '气血两虚', confidence: 0.85 });
          implications.push({ concept: '脾胃虚弱', confidence: 0.75 });
          break;
        case '淡红':
          implications.push({ concept: '正常', confidence: 0.90 });
          break;
        case '红':
          implications.push({ concept: '热证', confidence: 0.80 });
          implications.push({ concept: '阴虚内热', confidence: 0.65 });
          break;
        case '绛':
          implications.push({ concept: '热入营血', confidence: 0.85 });
          implications.push({ concept: '血瘀', confidence: 0.70 });
          break;
        case '紫暗':
          implications.push({ concept: '严重血瘀', confidence: 0.90 });
          implications.push({ concept: '寒凝血瘀', confidence: 0.65 });
          break;
        default:
          break;
      }
      
      // 分析舌苔的辨证意义
      switch (features.tongueCoating) {
        case '薄白':
          implications.push({ concept: '表证', confidence: 0.60 });
          break;
        case '厚白':
          implications.push({ concept: '寒湿', confidence: 0.75 });
          implications.push({ concept: '脾胃湿浊', confidence: 0.80 });
          break;
        case '薄黄':
          implications.push({ concept: '湿热', confidence: 0.70 });
          break;
        case '黄腻':
          implications.push({ concept: '湿热内蕴', confidence: 0.85 });
          implications.push({ concept: '脾胃湿热', confidence: 0.80 });
          break;
        default:
          break;
      }
      
      // 分析舌体湿度的辨证意义
      switch (features.moisture) {
        case '干燥':
          implications.push({ concept: '阴虚', confidence: 0.80 });
          implications.push({ concept: '津液不足', confidence: 0.85 });
          break;
        case '偏湿':
          implications.push({ concept: '湿证', confidence: 0.75 });
          implications.push({ concept: '痰湿', confidence: 0.65 });
          break;
        default:
          break;
      }
      
      // 对其他特征进行分析...
      if (features.cracks) {
        implications.push({ concept: '阴虚久病', confidence: 0.80 });
      }
      
      if (features.spots) {
        implications.push({ concept: '瘀血', confidence: 0.75 });
      }
      
      if (features.teethMarks) {
        implications.push({ concept: '脾虚', confidence: 0.80 });
        implications.push({ concept: '水湿停滞', confidence: 0.70 });
      }
      
      this.logger.info('中医辨证分析完成');
      return implications;
    } catch (error) {
      this.logger.error(`分析中医辨证含义失败: ${error.message}`);
      throw new Error(`分析中医辨证含义失败: ${error.message}`);
    }
  }

  /**
   * 生成健康建议
   * @param tcmImplications 中医辨证结果
   * @returns 健康建议列表
   */
  private async generateRecommendations(tcmImplications: Array<{concept: string, confidence: number}>): Promise<string[]> {
    try {
      this.logger.info('开始生成健康建议');
      
      // 在实际实现中，这里应该接入知识库或推荐系统
      // 以下是基于简单规则的建议生成
      
      const recommendations: string[] = [];
      const concepts = tcmImplications.map(i => i.concept);
      
      // 基于辨证概念生成建议
      if (concepts.includes('气血两虚') || concepts.includes('脾胃虚弱')) {
        recommendations.push('饮食宜清淡易消化，可适当进食健脾养胃的食物如山药、薏米等');
        recommendations.push('注意劳逸结合，避免过度疲劳');
        recommendations.push('可考虑使用四君子汤等调理脾胃');
      }
      
      if (concepts.includes('热证') || concepts.includes('阴虚内热')) {
        recommendations.push('饮食宜清淡，避免辛辣刺激食物');
        recommendations.push('多饮水，保持充分休息');
        recommendations.push('可食用梨、银耳等滋阴清热食物');
      }
      
      if (concepts.includes('血瘀') || concepts.includes('严重血瘀') || concepts.includes('寒凝血瘀')) {
        recommendations.push('保持适度活动，促进血液循环');
        recommendations.push('饮食可适当增加活血化瘀的食材如桃仁、红枣等');
        recommendations.push('注意保暖，避免寒凉刺激');
      }
      
      if (concepts.includes('湿热') || concepts.includes('湿热内蕴') || concepts.includes('脾胃湿热')) {
        recommendations.push('饮食宜清淡，避免油腻、辛辣及甜腻食物');
        recommendations.push('保持规律作息，避免熬夜');
        recommendations.push('多食用冬瓜、绿豆、薏米等健脾利湿食物');
      }
      
      if (concepts.includes('阴虚') || concepts.includes('津液不足')) {
        recommendations.push('保持充足睡眠，避免过度劳累');
        recommendations.push('饮食宜滋阴润燥，可食用银耳、百合、梨等');
        recommendations.push('避免辛辣温燥食物，少饮酒');
      }
      
      // 通用健康建议
      if (recommendations.length === 0) {
        recommendations.push('保持规律作息，注意饮食平衡');
        recommendations.push('适度运动，保持心情舒畅');
      }
      
      this.logger.info('健康建议生成完成');
      return recommendations;
    } catch (error) {
      this.logger.error(`生成健康建议失败: ${error.message}`);
      throw new Error(`生成健康建议失败: ${error.message}`);
    }
  }
}