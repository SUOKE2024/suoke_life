import { Service } from 'typedi';
import { v4 as uuidv4 } from 'uuid';
import sharp from 'sharp';
import path from 'path';
import fs from 'fs';
import { Logger } from '../../utils/logger';
import { PostureAnalysisRepository } from '../../repositories/posture-analysis.repository';
import { PostureDiagnosis, PostureFeatures, TCMImplication } from '../../models/diagnosis/posture.model';

/**
 * 体态分析服务类
 * 负责分析体态图像并生成诊断结果
 */
@Service()
export class PostureAnalysisService {
  private logger = new Logger('PostureAnalysisService');
  private readonly imageStoragePath: string;
  
  constructor(private postureAnalysisRepository: PostureAnalysisRepository) {
    // 设置图像存储路径
    this.imageStoragePath = process.env.IMAGE_STORAGE_PATH || path.join(process.cwd(), 'data', 'images', 'posture');
    
    // 确保目录存在
    if (!fs.existsSync(this.imageStoragePath)) {
      fs.mkdirSync(this.imageStoragePath, { recursive: true });
    }
  }
  
  /**
   * 分析体态
   * @param imageBase64 Base64编码的图像
   * @param sessionId 会话ID
   * @param userId 用户ID (可选)
   * @param metadata 元数据
   * @returns 体态分析结果
   */
  async analyzePosture(
    imageBase64: string,
    sessionId: string,
    userId?: string,
    metadata: Record<string, any> = {}
  ): Promise<PostureDiagnosis> {
    try {
      this.logger.info(`开始体态分析， 会话ID: ${sessionId}`);
      
      // 解码Base64图像
      const imageBuffer = Buffer.from(imageBase64.replace(/^data:image\/\w+;base64,/, ''), 'base64');
      
      // 保存图像
      const imageName = `posture_${Date.now()}_${uuidv4().substring(0, 8)}.png`;
      const imagePath = path.join(this.imageStoragePath, imageName);
      
      await sharp(imageBuffer)
        .resize(800, 800, { fit: 'inside', withoutEnlargement: true })
        .toFile(imagePath);
      
      this.logger.info(`图像已保存: ${imagePath}`);
      
      // 处理图像并提取特征
      const features = await this.extractPostureFeatures(imageBuffer);
      
      // 生成中医体质关联
      const tcmImplications = this.generateTCMImplications(features);
      
      // 生成健康建议
      const recommendations = this.generateRecommendations(features, tcmImplications);
      
      // 创建诊断结果
      const diagnosisId = `ld-posture-${Date.now()}-${uuidv4().substring(0, 8)}`;
      
      const postureDiagnosis: Partial<PostureDiagnosis> = {
        diagnosisId,
        sessionId,
        userId,
        timestamp: new Date(),
        imagePath,
        features,
        tcmImplications,
        recommendations,
        metadata: {
          ...metadata,
          processingSteps: [
            '图像预处理',
            '体态特征提取',
            'TCM辨证分析',
            '建议生成'
          ],
          dataVersion: '1.0'
        }
      };
      
      // 保存到数据库
      const savedDiagnosis = await this.postureAnalysisRepository.savePostureDiagnosis(postureDiagnosis);
      
      this.logger.info(`体态分析完成, 诊断ID: ${diagnosisId}`);
      return savedDiagnosis;
    } catch (error) {
      this.logger.error(`体态分析失败: ${error.message}`);
      throw new Error(`体态分析失败: ${error.message}`);
    }
  }
  
  /**
   * 通过ID获取体态分析结果
   * @param diagnosisId 诊断ID
   * @returns 体态分析结果
   */
  async getPostureDiagnosisById(diagnosisId: string): Promise<PostureDiagnosis | null> {
    try {
      return await this.postureAnalysisRepository.getPostureDiagnosisById(diagnosisId);
    } catch (error) {
      this.logger.error(`获取体态分析结果失败: ${error.message}`);
      throw new Error(`获取体态分析结果失败: ${error.message}`);
    }
  }
  
  /**
   * 获取用户的体态分析历史记录
   * @param userId 用户ID
   * @param limit 记录限制数
   * @param offset 偏移量
   * @returns 体态分析历史记录
   */
  async getPostureDiagnosisByUserId(userId: string, limit: number = 10, offset: number = 0): Promise<PostureDiagnosis[]> {
    try {
      return await this.postureAnalysisRepository.getPostureDiagnosisByUserId(userId, limit, offset);
    } catch (error) {
      this.logger.error(`获取用户体态分析历史记录失败: ${error.message}`);
      throw new Error(`获取用户体态分析历史记录失败: ${error.message}`);
    }
  }
  
  /**
   * 获取会话的体态分析历史记录
   * @param sessionId 会话ID
   * @param limit 记录限制数
   * @param offset 偏移量
   * @returns 体态分析历史记录
   */
  async getPostureDiagnosisBySessionId(sessionId: string, limit: number = 10, offset: number = 0): Promise<PostureDiagnosis[]> {
    try {
      return await this.postureAnalysisRepository.getPostureDiagnosisBySessionId(sessionId, limit, offset);
    } catch (error) {
      this.logger.error(`获取会话体态分析历史记录失败: ${error.message}`);
      throw new Error(`获取会话体态分析历史记录失败: ${error.message}`);
    }
  }
  
  /**
   * 从图像中提取体态特征
   * 注意：这里是mock实现，实际项目中应该集成姿态估计模型
   * @param imageBuffer 图像缓冲区
   * @returns 体态特征
   */
  private async extractPostureFeatures(imageBuffer: Buffer): Promise<PostureFeatures> {
    // 模拟体态特征提取（实际项目中应该使用专业的姿态估计模型）
    // 如: tensorflow的posenet或mediapipe的姿态估计模型
    
    // 随机模拟一些体态特征作为示例
    const posturalProblems = [
      { name: 'hasForwardHeadPosture', probability: Math.random() },
      { name: 'hasRoundedShoulders', probability: Math.random() },
      { name: 'hasSwaybBack', probability: Math.random() },
      { name: 'hasFlatBack', probability: Math.random() }
    ];
    
    const postureAlignments = [
      '正常', '略前倾', '显著前倾', '后仰', '偏左', '偏右'
    ];
    
    const shoulderAlignments = [
      '对称', '左高', '右高', '双侧前倾', '左侧前倾', '右侧前倾'
    ];
    
    const spineAlignments = [
      '正常', '过度弯曲', '左侧弯曲', '右侧弯曲', '平直', 'S型弯曲'
    ];
    
    const hipAlignments = [
      '对称', '左高', '右高', '前倾', '后倾'
    ];
    
    // 生成模拟的体态特征
    return {
      overallPosture: postureAlignments[Math.floor(Math.random() * postureAlignments.length)],
      shoulderAlignment: shoulderAlignments[Math.floor(Math.random() * shoulderAlignments.length)],
      spineAlignment: spineAlignments[Math.floor(Math.random() * spineAlignments.length)],
      hipAlignment: hipAlignments[Math.floor(Math.random() * hipAlignments.length)],
      
      hasForwardHeadPosture: posturalProblems[0].probability > 0.5,
      hasRoundedShoulders: posturalProblems[1].probability > 0.5,
      hasSwaybBack: posturalProblems[2].probability > 0.5,
      hasFlatBack: posturalProblems[3].probability > 0.5,
      
      posturalDeviation: Math.floor(Math.random() * 8) + 1, // 1-8 分
      comments: '这是一个基于模拟数据的体态分析评估，实际应用中应替换为真实的姿态估计分析结果。'
    };
  }
  
  /**
   * 生成中医体质关联
   * @param features 体态特征
   * @returns 中医体质关联
   */
  private generateTCMImplications(features: PostureFeatures): TCMImplication[] {
    const tcmImplications: TCMImplication[] = [];
    
    // 根据体态特征生成中医体质关联
    // 例如：肩部前倾往往与气虚相关
    if (features.hasRoundedShoulders) {
      tcmImplications.push({
        concept: '气虚体质',
        confidence: 0.7 + Math.random() * 0.3,
        explanation: '肩部前倾(圆肩)往往与气虚体质相关，表现为精神不振、易疲劳。'
      });
    }
    
    // 脊柱弯曲异常与肝肾不足相关
    if (features.hasSwaybBack || features.spineAlignment !== '正常') {
      tcmImplications.push({
        concept: '肝肾不足',
        confidence: 0.6 + Math.random() * 0.3,
        explanation: '脊柱弯曲异常往往与肝肾不足相关，可能表现为腰膝酸软。'
      });
    }
    
    // 头部前倾与颈肩不适相关
    if (features.hasForwardHeadPosture) {
      tcmImplications.push({
        concept: '肝郁气滞',
        confidence: 0.5 + Math.random() * 0.4,
        explanation: '头部前倾姿势可能与肝郁气滞相关，常见颈肩部紧张不适。'
      });
    }
    
    // 骨盆不平衡与脾虚湿阻相关
    if (features.hipAlignment !== '对称') {
      tcmImplications.push({
        concept: '脾虚湿阻',
        confidence: 0.5 + Math.random() * 0.3,
        explanation: '骨盆不平衡可能与脾虚湿阻相关，表现为下肢沉重感、消化不良等。'
      });
    }
    
    // 若没有明显异常，则为平和体质
    if (tcmImplications.length === 0 || (
      features.overallPosture === '正常' &&
      features.shoulderAlignment === '对称' &&
      features.spineAlignment === '正常' &&
      features.hipAlignment === '对称'
    )) {
      tcmImplications.push({
        concept: '平和体质',
        confidence: 0.8,
        explanation: '体态表现整体较为平衡，符合平和体质特征。'
      });
    }
    
    return tcmImplications;
  }
  
  /**
   * 生成健康建议
   * @param features 体态特征
   * @param tcmImplications 中医体质关联
   * @returns 健康建议
   */
  private generateRecommendations(features: PostureFeatures, tcmImplications: TCMImplication[]): string[] {
    const recommendations: string[] = [];
    
    // 通用建议
    recommendations.push('保持良好姿势，注意站立和坐姿的正确性。');
    recommendations.push('定期进行体态评估，跟踪姿势变化。');
    
    // 根据体态特征生成特定建议
    if (features.hasForwardHeadPosture) {
      recommendations.push('注意头部姿势，避免长时间低头看手机或电脑，建议每工作一小时休息5-10分钟。');
      recommendations.push('可以尝试颈部后伸运动，每天3-5次，每次保持10秒。');
    }
    
    if (features.hasRoundedShoulders) {
      recommendations.push('加强背部肌肉锻炼，如划船运动、俯卧撑等。');
      recommendations.push('注意工作环境的人体工程学设计，调整座椅和桌面高度。');
    }
    
    if (features.hasSwaybBack) {
      recommendations.push('加强核心肌群训练，如平板支撑、仰卧起坐等。');
      recommendations.push('注意站立时避免腰部过度前凸，保持骨盆中立位置。');
    }
    
    if (features.spineAlignment !== '正常') {
      recommendations.push('建议咨询物理治疗师，获取个性化的脊柱矫正方案。');
      recommendations.push('日常注意姿势，避免习惯性偏侧负重。');
    }
    
    // 根据TCM体质关联添加中医调理建议
    for (const implication of tcmImplications) {
      if (implication.concept === '气虚体质') {
        recommendations.push('建议适量参加有氧运动，如太极、慢跑等，增强体质。');
        recommendations.push('饮食宜清淡而富有营养，可适当食用黄芪炖鸡、山药等补气食物。');
      }
      
      if (implication.concept === '肝肾不足') {
        recommendations.push('避免过度劳累，保证充足睡眠，尤其是23:00前就寝。');
        recommendations.push('可适当食用枸杞、核桃等滋补肝肾的食物。');
      }
      
      if (implication.concept === '肝郁气滞') {
        recommendations.push('保持心情舒畅，避免情绪激动，可尝试冥想、深呼吸等放松技巧。');
        recommendations.push('饮食宜疏肝理气，如薄荷、柑橘类水果等。');
      }
      
      if (implication.concept === '脾虚湿阻') {
        recommendations.push('饮食宜清淡，避免过食生冷、油腻食物。');
        recommendations.push('建议适当食用山药、薏米、莲子等健脾祛湿的食物。');
      }
      
      if (implication.concept === '平和体质') {
        recommendations.push('继续保持当前的良好生活习惯。');
        recommendations.push('均衡饮食，适量运动，保持规律作息。');
      }
    }
    
    return recommendations;
  }
} 