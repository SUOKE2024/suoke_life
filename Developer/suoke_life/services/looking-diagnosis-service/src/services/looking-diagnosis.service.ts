import { Service } from 'typedi';
import { 
  FaceAnalysisResult, 
  TongueAnalysisResult, 
  DiagnosticResult, 
  FaceAnalysisRequest, 
  TongueAnalysisRequest, 
  ComprehensiveAnalysisRequest,
  PaginationOptions,
  ConstitutionInfo,
  PaginatedResult,
  Recommendation,
  FiveElementsAnalysis,
  SpiritAnalysis,
  ThreeZonesAnalysis,
  TextureAnalysis,
  PhysiqueAnalysis,
  DynamicFeaturesAnalysis,
  FaceProportionAnalysis
} from '../interfaces/looking-diagnosis.interface';
import { logger } from '../utils/logger';
import { v4 as uuidv4 } from 'uuid';
import * as fs from 'fs';
import * as path from 'path';
import config from '../config';
import axios from 'axios';
import { Cache } from '../utils/cache';
import { FileStorage } from '../utils/file-storage';
import { ImageProcessor } from '../utils/image-processor';
import { KnowledgeGraphService } from './knowledge-graph.service';
import { lookingDiagnosisCounter, diagnosisSuccessCounter, diagnosisErrorCounter } from '../metrics/looking-diagnosis.metrics';

@Service()
export class LookingDiagnosisService {
  private modelCache: Cache;
  private resultCache: Cache;
  private fileStorage: FileStorage;
  private imageProcessor: ImageProcessor;
  private knowledgeGraphService: KnowledgeGraphService;
  
  constructor() {
    this.modelCache = new Cache('looking-diagnosis-models', config.cache.ttl);
    this.resultCache = new Cache('looking-diagnosis-results', config.cache.ttl * 3);
    this.fileStorage = new FileStorage();
    this.imageProcessor = new ImageProcessor();
    this.knowledgeGraphService = new KnowledgeGraphService();
    
    this.loadModels().catch(err => {
      logger.error('加载望诊模型失败', { error: err.message });
    });
  }
  
  /**
   * 加载所需的望诊模型
   */
  private async loadModels(): Promise<void> {
    logger.info('开始加载望诊分析模型...');
    
    try {
      // 加载面部分析模型
      await this.imageProcessor.loadModel('face-detection', path.join(config.modelPaths.faceDetection));
      await this.imageProcessor.loadModel('complexion-analysis', path.join(config.modelPaths.complexionAnalysis));
      
      // 加载舌象分析模型
      await this.imageProcessor.loadModel('tongue-detection', path.join(config.modelPaths.tongueDetection));
      await this.imageProcessor.loadModel('tongue-analysis', path.join(config.modelPaths.tongueAnalysis));
      
      // 加载多模态模型
      await this.imageProcessor.loadModel('multimodal-fusion', path.join(config.modelPaths.multimodalFusion));
      
      logger.info('望诊分析模型加载完成');
    } catch (error) {
      logger.error('加载望诊模型失败', { error: error.message, stack: error.stack });
      throw error;
    }
  }
  
  /**
   * 分析面部图像
   */
  public async analyzeFace(params: FaceAnalysisRequest): Promise<FaceAnalysisResult> {
    const startTime = Date.now();
    const { userId, imagePath, imageUrl, includeFeatures = true, includeTcmAnalysis = true } = params;
    
    try {
      let imageBuff: Buffer;
      let finalImagePath: string;
      
      // 处理图像来源
      if (imagePath) {
        imageBuff = await fs.promises.readFile(imagePath);
        finalImagePath = imagePath;
      } else if (imageUrl) {
        const response = await axios.get(imageUrl, { responseType: 'arraybuffer' });
        imageBuff = Buffer.from(response.data, 'binary');
        finalImagePath = path.join(config.tempDir, `face_${uuidv4()}.jpg`);
        await fs.promises.writeFile(finalImagePath, imageBuff);
      } else {
        throw new Error('必须提供imagePath或imageUrl');
      }
      
      // 检测人脸
      const faceDetectionResult = await this.imageProcessor.detectFace(finalImagePath);
      
      if (!faceDetectionResult.detected) {
        diagnosisErrorCounter.inc({ type: 'face', reason: 'no_face_detected' });
        return {
          id: uuidv4(),
          userId,
          timestamp: new Date(),
          faceDetected: false,
          confidence: 0,
          processingTime: Date.now() - startTime
        };
      }
      
      // 分析面色
      const complexionResult = await this.imageProcessor.analyzeComplexion(
        finalImagePath, 
        faceDetectionResult.boundingBox
      );
      
      // 构建基本结果
      const result: FaceAnalysisResult = {
        id: uuidv4(),
        userId,
        timestamp: new Date(),
        imageUrl: imageUrl || await this.fileStorage.saveAndGetUrl(imageBuff, `face/${userId}/${result.id}.jpg`),
        faceDetected: true,
        confidence: complexionResult.confidence,
        processingTime: Date.now() - startTime
      };
      
      // 如果需要特征分析
      if (includeFeatures) {
        result.faceFeatures = {
          complexion: {
            main: complexionResult.mainComplexion,
            secondary: complexionResult.secondaryComplexion,
            brightness: complexionResult.brightness,
            uniformity: complexionResult.uniformity,
            regions: complexionResult.regions
          },
          eyeFeatures: complexionResult.eyeFeatures,
          facialLandmarks: complexionResult.landmarks,
          facialExpression: complexionResult.expression
        };
      }
      
      // 如果需要中医分析
      if (includeTcmAnalysis) {
        result.tcmAnalysis = await this.analyzeTcmPatterns(complexionResult, 'face');
      }
      
      // 缓存结果
      this.resultCache.set(`face_${result.id}`, result);
      
      // 更新指标
      diagnosisSuccessCounter.inc({ type: 'face' });
      
      return result;
    } catch (error) {
      logger.error('面部望诊分析失败', { 
        error: error.message, 
        stack: error.stack,
        userId
      });
      diagnosisErrorCounter.inc({ type: 'face', reason: 'processing_error' });
      throw error;
    }
  }
  
  /**
   * 分析舌象图像
   */
  public async analyzeTongue(params: TongueAnalysisRequest): Promise<TongueAnalysisResult> {
    const startTime = Date.now();
    const { userId, imagePath, imageUrl, includeFeatures = true } = params;
    
    try {
      let imageBuff: Buffer;
      let finalImagePath: string;
      
      // 处理图像来源
      if (imagePath) {
        imageBuff = await fs.promises.readFile(imagePath);
        finalImagePath = imagePath;
      } else if (imageUrl) {
        const response = await axios.get(imageUrl, { responseType: 'arraybuffer' });
        imageBuff = Buffer.from(response.data, 'binary');
        finalImagePath = path.join(config.tempDir, `tongue_${uuidv4()}.jpg`);
        await fs.promises.writeFile(finalImagePath, imageBuff);
      } else {
        throw new Error('必须提供imagePath或imageUrl');
      }
      
      // 检测舌头
      const tongueDetectionResult = await this.imageProcessor.detectTongue(finalImagePath);
      
      if (!tongueDetectionResult.detected) {
        diagnosisErrorCounter.inc({ type: 'tongue', reason: 'no_tongue_detected' });
        return {
          id: uuidv4(),
          userId,
          timestamp: new Date(),
          tongueDetected: false,
          confidence: 0,
          processingTime: Date.now() - startTime
        };
      }
      
      // 分析舌象
      const tongueResult = await this.imageProcessor.analyzeTongue(
        finalImagePath, 
        tongueDetectionResult.boundingBox
      );
      
      // 构建基本结果
      const result: TongueAnalysisResult = {
        id: uuidv4(),
        userId,
        timestamp: new Date(),
        imageUrl: imageUrl || await this.fileStorage.saveAndGetUrl(imageBuff, `tongue/${userId}/${result.id}.jpg`),
        tongueDetected: true,
        confidence: tongueResult.confidence,
        processingTime: Date.now() - startTime
      };
      
      // 如果需要特征分析
      if (includeFeatures) {
        result.tongueFeatures = {
          tongueBody: {
            color: tongueResult.bodyColor,
            shape: tongueResult.shape,
            cracks: tongueResult.cracks,
            spots: tongueResult.spots,
            toothMarks: tongueResult.toothMarks,
            moisture: tongueResult.moisture
          },
          tongueCoating: {
            color: tongueResult.coatingColor,
            thickness: tongueResult.coatingThickness,
            distribution: tongueResult.coatingDistribution,
            rootAttachment: tongueResult.rootAttachment
          },
          tongueMovement: tongueResult.movement
        };
      }
      
      // 进行中医分析
      result.tcmAnalysis = await this.analyzeTcmPatterns(tongueResult, 'tongue');
      
      // 缓存结果
      this.resultCache.set(`tongue_${result.id}`, result);
      
      // 更新指标
      diagnosisSuccessCounter.inc({ type: 'tongue' });
      
      return result;
    } catch (error) {
      logger.error('舌象望诊分析失败', { 
        error: error.message, 
        stack: error.stack,
        userId
      });
      diagnosisErrorCounter.inc({ type: 'tongue', reason: 'processing_error' });
      throw error;
    }
  }
  
  /**
   * 综合分析
   */
  public async performComprehensiveAnalysis(params: ComprehensiveAnalysisRequest): Promise<DiagnosticResult> {
    const { 
      userId, 
      faceImageId, 
      tongueImageId, 
      eyeImageId, 
      postureMeasurements,
      userSymptoms,
      includeRecommendations = true,
      // 新增参数
      physiqueData,
      dynamicBehaviorData,
      advancedAnalysisOptions
    } = params;
    
    try {
      // 收集各项分析结果
      const analyses: any = {};
      
      // 获取面部分析结果
      if (faceImageId) {
        const faceResult = await this.getDiagnosticResult(faceImageId, userId) as FaceAnalysisResult;
        if (faceResult && faceResult.faceDetected) {
          analyses.face = faceResult;
        }
      }
      
      // 获取舌象分析结果
      if (tongueImageId) {
        const tongueResult = await this.getDiagnosticResult(tongueImageId, userId) as TongueAnalysisResult;
        if (tongueResult && tongueResult.tongueDetected) {
          analyses.tongue = tongueResult;
        }
      }
      
      // 其他分析结果处理（眼部、姿态等）
      // ...
      
      // 新增：处理形体气质数据
      if (physiqueData) {
        analyses.physique = await this.analyzePhysique(physiqueData, userId);
      }
      
      // 新增：处理动态行为数据
      if (dynamicBehaviorData) {
        analyses.dynamicBehavior = await this.analyzeDynamicBehavior(dynamicBehaviorData, userId);
      }
      
      // 进行多模态融合分析
      const fusionResult = await this.performMultimodalFusion(analyses, userSymptoms, advancedAnalysisOptions);
      
      // 构建诊断结果
      const diagnosticResult: DiagnosticResult = {
        id: uuidv4(),
        userId,
        timestamp: new Date(),
        sources: {
          face: faceImageId,
          tongue: tongueImageId,
          eye: eyeImageId,
          posture: !!postureMeasurements,
          userSymptoms: !!userSymptoms,
          physique: !!physiqueData,
          dynamicBehavior: !!dynamicBehaviorData
        },
        constitutionAnalysis: fusionResult.constitutionAnalysis,
        healthStatus: fusionResult.healthStatus,
        confidence: fusionResult.confidence
      };
      
      // 如果启用了高级分析，添加相应结果
      if (fusionResult.physiqueAnalysis) {
        diagnosticResult.physiqueAnalysis = fusionResult.physiqueAnalysis;
      }
      
      if (fusionResult.dynamicFeaturesAnalysis) {
        diagnosticResult.dynamicFeaturesAnalysis = fusionResult.dynamicFeaturesAnalysis;
      }
      
      // 如果需要包含建议
      if (includeRecommendations) {
        diagnosticResult.recommendations = await this.generateRecommendations(
          diagnosticResult.constitutionAnalysis,
          diagnosticResult.healthStatus,
          diagnosticResult.physiqueAnalysis,
          diagnosticResult.dynamicFeaturesAnalysis
        );
      }
      
      return diagnosticResult;
    } catch (error) {
      logger.error('综合望诊分析失败', { error: error.message, stack: error.stack, userId });
      throw error;
    }
  }
  
  /**
   * 基于中医理论分析证型
   */
  private async analyzeTcmPatterns(analysisResult: any, type: 'face' | 'tongue'): Promise<any> {
    try {
      // 基于不同类型的分析结果，应用中医知识进行证型辨识
      const primaryPatterns = await this.identifyPrimaryPatterns(analysisResult, type);
      const secondaryPatterns = await this.identifySecondaryPatterns(analysisResult, type);
      
      // 获取五行关系
      const fiveElements = this.calculateFiveElements(primaryPatterns, secondaryPatterns);
      
      // 获取脏腑关系
      const organImbalances = this.identifyOrganImbalances(primaryPatterns, secondaryPatterns);
      
      // 构建分析说明
      const explanation = await this.generateTcmExplanation(primaryPatterns, secondaryPatterns, type);
      
      return {
        mainPattern: primaryPatterns[0],
        secondaryPatterns: secondaryPatterns,
        fiveElements,
        organImbalances,
        explanation,
        confidence: this.calculateConfidence(analysisResult, type)
      };
    } catch (error) {
      logger.error('中医证型分析失败', { 
        error: error.message, 
        stack: error.stack,
        analysisType: type
      });
      return {
        mainPattern: '未知',
        explanation: '无法完成中医证型分析',
        confidence: 0
      };
    }
  }
  
  /**
   * 获取用户历史诊断结果
   */
  public async getUserDiagnosticHistory(userId: string, options: PaginationOptions): Promise<PaginatedResult<DiagnosticResult>> {
    // 实现从数据库获取用户历史诊断结果的逻辑
    // ...
    
    // 模拟返回数据
    return {
      items: [],
      total: 0,
      page: options.page,
      limit: options.limit,
      totalPages: 0
    };
  }
  
  /**
   * 获取诊断结果详情
   */
  public async getDiagnosticResult(resultId: string, userId: string): Promise<FaceAnalysisResult | TongueAnalysisResult | DiagnosticResult> {
    // 首先尝试从缓存获取
    const cachedResult = this.resultCache.get(`face_${resultId}`) || 
                         this.resultCache.get(`tongue_${resultId}`) || 
                         this.resultCache.get(`comprehensive_${resultId}`);
    
    if (cachedResult) {
      // 验证用户权限
      if (cachedResult.userId === userId) {
        return cachedResult;
      } else {
        throw new Error('无权访问该诊断结果');
      }
    }
    
    // 从数据库获取结果
    // ...
    
    throw new Error('找不到指定的诊断结果');
  }
  
  /**
   * 获取体质类型信息
   */
  public async getConstitutionInfo(constitutionType: string): Promise<ConstitutionInfo> {
    // 从知识图谱或配置获取体质信息
    try {
      const info = await this.knowledgeGraphService.getConstitutionInfo(constitutionType);
      return info;
    } catch (error) {
      logger.error('获取体质信息失败', { 
        error: error.message, 
        constitutionType
      });
      throw new Error(`无法获取体质信息: ${constitutionType}`);
    }
  }
  
  /**
   * 获取个性化健康建议
   */
  public async getPersonalizedRecommendations(
    resultId: string, 
    userId: string, 
    includeTypes?: string[]
  ): Promise<Recommendation[]> {
    try {
      // 获取诊断结果
      const diagnosticResult = await this.getDiagnosticResult(resultId, userId) as DiagnosticResult;
      
      if (!diagnosticResult) {
        throw new Error('找不到指定的诊断结果');
      }
      
      // 如果结果已有建议且不需要特定类型的建议，直接返回
      if (diagnosticResult.recommendations && !includeTypes) {
        return diagnosticResult.recommendations;
      }
      
      // 生成建议
      let recommendations = await this.generateRecommendations(
        diagnosticResult.constitutionAnalysis,
        diagnosticResult.healthStatus
      );
      
      // 如果需要筛选特定类型
      if (includeTypes && includeTypes.length > 0) {
        recommendations = recommendations.filter(rec => includeTypes.includes(rec.type));
      }
      
      return recommendations;
    } catch (error) {
      logger.error('获取个性化建议失败', { 
        error: error.message, 
        resultId,
        userId
      });
      throw error;
    }
  }
  
  /**
   * 生成健康建议
   */
  private async generateRecommendations(
    constitutionAnalysis: any, 
    healthStatus: any
  ): Promise<Recommendation[]> {
    // 根据体质分析和健康状态生成个性化建议
    // ...
    
    // 模拟返回数据
    return [
      {
        type: 'diet',
        title: '膳食调理建议',
        description: '根据您的体质特点，建议饮食调整方案',
        priority: 1,
        items: [
          {
            name: '温性食物',
            description: '如生姜、韭菜等温性食物有助于调节阳虚体质',
            frequency: '每周3-4次'
          }
        ]
      }
    ];
  }
  
  /**
   * 执行多模态融合分析
   */
  private async performMultimodalFusion(
    analyses: any, 
    userSymptoms?: any,
    advancedOptions?: any
  ): Promise<any> {
    // 构建融合输入
    const fusionInput: any = {};
    
    // 添加面部分析数据
    if (analyses.face) {
      fusionInput.face = {
        features: analyses.face.faceFeatures,
        tcmAnalysis: analyses.face.tcmAnalysis
      };
      
      // 新增：添加高级面部分析结果
      if (analyses.face.fiveElementsAnalysis) {
        fusionInput.face.fiveElements = analyses.face.fiveElementsAnalysis;
      }
      
      if (analyses.face.spiritAnalysis) {
        fusionInput.face.spirit = analyses.face.spiritAnalysis;
      }
      
      if (analyses.face.threeZonesAnalysis) {
        fusionInput.face.threeZones = analyses.face.threeZonesAnalysis;
      }
      
      if (analyses.face.textureAnalysis) {
        fusionInput.face.texture = analyses.face.textureAnalysis;
      }
      
      if (analyses.face.faceProportionAnalysis) {
        fusionInput.face.proportion = analyses.face.faceProportionAnalysis;
      }
    }
    
    // 添加舌象分析数据
    if (analyses.tongue) {
      fusionInput.tongue = {
        features: analyses.tongue.tongueFeatures,
        tcmAnalysis: analyses.tongue.tcmAnalysis
      };
    }
    
    // 添加其他数据源
    // ...
    
    // 新增：添加形体分析数据
    if (analyses.physique) {
      fusionInput.physique = analyses.physique;
    }
    
    // 新增：添加动态行为分析数据
    if (analyses.dynamicBehavior) {
      fusionInput.dynamicBehavior = analyses.dynamicBehavior;
    }
    
    // 添加用户自述症状
    if (userSymptoms) {
      fusionInput.userSymptoms = userSymptoms;
    }
    
    // 添加分析选项
    if (advancedOptions) {
      fusionInput.options = advancedOptions;
    }
    
    // 调用望诊服务进行多模态融合
    try {
      const response = await axios.post(`${config.services.lookingDiagnosis}/multimodal-fusion`, fusionInput);
      return response.data;
    } catch (error) {
      logger.error('多模态融合分析失败', { error: error.message });
      throw error;
    }
  }
  
  /**
   * 保存综合诊断结果
   */
  private async saveComprehensiveDiagnosisResult(result: DiagnosticResult): Promise<void> {
    // 将结果保存到缓存
    this.resultCache.set(`comprehensive_${result.id}`, result);
    
    // 将结果保存到数据库
    // ...
  }
  
  /**
   * 计算分析置信度
   */
  private calculateConfidence(analysisResult: any, type: string): number {
    // 根据分析结果计算置信度
    // ...
    return 0.85;
  }
  
  /**
   * 识别主要证型
   */
  private async identifyPrimaryPatterns(analysisResult: any, type: string): Promise<string[]> {
    // 根据分析结果识别主要证型
    // ...
    return ['阳虚证'];
  }
  
  /**
   * 识别次要证型
   */
  private async identifySecondaryPatterns(analysisResult: any, type: string): Promise<string[]> {
    // 根据分析结果识别次要证型
    // ...
    return ['气虚证', '血虚证'];
  }
  
  /**
   * 计算五行关系
   */
  private calculateFiveElements(primaryPatterns: string[], secondaryPatterns: string[]): any {
    // 根据证型计算五行关系
    // ...
    return {
      wood: 30,
      fire: 40,
      earth: 60,
      metal: 75,
      water: 55
    };
  }
  
  /**
   * 识别脏腑失调
   */
  private identifyOrganImbalances(primaryPatterns: string[], secondaryPatterns: string[]): string[] {
    // 根据证型识别脏腑失调
    // ...
    return ['脾虚', '肾阳不足'];
  }
  
  /**
   * 生成中医理论解释
   */
  private async generateTcmExplanation(
    primaryPatterns: string[], 
    secondaryPatterns: string[], 
    type: string
  ): Promise<string> {
    // 根据证型生成中医理论解释
    // ...
    return '您的面色偏白，舌淡苔白，为阳虚证的表现。阳虚主要是由于阳气不足，温煦功能减弱所致，常见怕冷、手脚发凉、精神不振等症状。';
  }
  
  // 新增：处理面部五行分析
  public async analyzeFaceFiveElements(imageId: string, userId: string): Promise<FiveElementsAnalysis> {
    try {
      // 检查是否启用了这项分析
      if (!config.lookingDiagnosis.advancedAnalysis.enableFiveElements) {
        throw new Error('面部五行分析功能未启用');
      }
      
      // 获取面部分析结果作为基础
      const faceResult = await this.getDiagnosticResult(imageId, userId) as FaceAnalysisResult;
      if (!faceResult || !faceResult.faceDetected) {
        throw new Error('无法检测到面部，请重新上传清晰的正面照片');
      }
      
      // 调用望诊服务API进行五行分析
      const response = await axios.post(`${config.services.lookingDiagnosis}/face-five-elements`, {
        imageId,
        userId,
        faceFeatures: faceResult.faceFeatures
      });
      
      return response.data;
    } catch (error) {
      logger.error('面部五行分析失败', { error: error.message, userId, imageId });
      throw error;
    }
  }
  
  // 新增：处理神气分析
  public async analyzeFaceSpirit(imageId: string, userId: string): Promise<SpiritAnalysis> {
    try {
      // 检查是否启用了这项分析
      if (!config.lookingDiagnosis.advancedAnalysis.enableSpiritAnalysis) {
        throw new Error('神气分析功能未启用');
      }
      
      // 获取面部分析结果作为基础
      const faceResult = await this.getDiagnosticResult(imageId, userId) as FaceAnalysisResult;
      if (!faceResult || !faceResult.faceDetected) {
        throw new Error('无法检测到面部，请重新上传清晰的正面照片');
      }
      
      // 调用望诊服务API进行神气分析
      const response = await axios.post(`${config.services.lookingDiagnosis}/face-spirit`, {
        imageId,
        userId,
        faceFeatures: faceResult.faceFeatures
      });
      
      return response.data;
    } catch (error) {
      logger.error('神气分析失败', { error: error.message, userId, imageId });
      throw error;
    }
  }
  
  // 新增：处理三停五骨分析
  public async analyzeThreeZones(imageId: string, userId: string): Promise<ThreeZonesAnalysis> {
    try {
      // 检查是否启用了这项分析
      if (!config.lookingDiagnosis.advancedAnalysis.enableThreeZones) {
        throw new Error('三停分析功能未启用');
      }
      
      // 获取面部分析结果作为基础
      const faceResult = await this.getDiagnosticResult(imageId, userId) as FaceAnalysisResult;
      if (!faceResult || !faceResult.faceDetected) {
        throw new Error('无法检测到面部，请重新上传清晰的正面照片');
      }
      
      // 调用望诊服务API进行三停分析
      const response = await axios.post(`${config.services.lookingDiagnosis}/face-three-zones`, {
        imageId,
        userId,
        faceFeatures: faceResult.faceFeatures
      });
      
      return response.data;
    } catch (error) {
      logger.error('三停分析失败', { error: error.message, userId, imageId });
      throw error;
    }
  }
  
  // 新增：处理面部纹理分析
  public async analyzeTexture(imageId: string, userId: string): Promise<TextureAnalysis> {
    try {
      // 检查是否启用了这项分析
      if (!config.lookingDiagnosis.advancedAnalysis.enableTextureAnalysis) {
        throw new Error('面部纹理分析功能未启用');
      }
      
      // 获取面部分析结果作为基础
      const faceResult = await this.getDiagnosticResult(imageId, userId) as FaceAnalysisResult;
      if (!faceResult || !faceResult.faceDetected) {
        throw new Error('无法检测到面部，请重新上传清晰的正面照片');
      }
      
      // 调用望诊服务API进行纹理分析
      const response = await axios.post(`${config.services.lookingDiagnosis}/face-texture`, {
        imageId,
        userId,
        faceFeatures: faceResult.faceFeatures
      });
      
      return response.data;
    } catch (error) {
      logger.error('面部纹理分析失败', { error: error.message, userId, imageId });
      throw error;
    }
  }
  
  // 新增：处理形体气质分析
  public async analyzePhysique(physiqueData: any, userId: string): Promise<PhysiqueAnalysis> {
    try {
      // 检查是否启用了这项分析
      if (!config.lookingDiagnosis.advancedAnalysis.enablePhysiqueAnalysis) {
        throw new Error('形体气质分析功能未启用');
      }
      
      // 调用望诊服务API进行形体气质分析
      const response = await axios.post(`${config.services.lookingDiagnosis}/physique-analysis`, {
        userId,
        physiqueData
      });
      
      return response.data;
    } catch (error) {
      logger.error('形体气质分析失败', { error: error.message, userId });
      throw error;
    }
  }
  
  // 新增：处理动态行为分析
  public async analyzeDynamicBehavior(dynamicData: any, userId: string): Promise<DynamicFeaturesAnalysis> {
    try {
      // 检查是否启用了这项分析
      if (!config.lookingDiagnosis.advancedAnalysis.enableDynamicFeatures) {
        throw new Error('动态行为分析功能未启用');
      }
      
      // 调用望诊服务API进行动态行为分析
      const response = await axios.post(`${config.services.lookingDiagnosis}/dynamic-features`, {
        userId,
        dynamicData
      });
      
      return response.data;
    } catch (error) {
      logger.error('动态行为分析失败', { error: error.message, userId });
      throw error;
    }
  }
  
  // 新增：处理面部比例分析
  public async analyzeFaceProportion(imageId: string, userId: string): Promise<FaceProportionAnalysis> {
    try {
      // 检查是否启用了这项分析
      if (!config.lookingDiagnosis.advancedAnalysis.enableFaceProportion) {
        throw new Error('面部比例分析功能未启用');
      }
      
      // 获取面部分析结果作为基础
      const faceResult = await this.getDiagnosticResult(imageId, userId) as FaceAnalysisResult;
      if (!faceResult || !faceResult.faceDetected) {
        throw new Error('无法检测到面部，请重新上传清晰的正面照片');
      }
      
      // 调用望诊服务API进行面部比例分析
      const response = await axios.post(`${config.services.lookingDiagnosis}/face-proportion`, {
        imageId,
        userId,
        faceFeatures: faceResult.faceFeatures
      });
      
      return response.data;
    } catch (error) {
      logger.error('面部比例分析失败', { error: error.message, userId, imageId });
      throw error;
    }
  }
  
  // 修改现有的面部分析方法，以支持新的分析功能
  public async performFaceAnalysis(params: FaceAnalysisRequest): Promise<FaceAnalysisResult> {
    const { 
      userId, 
      imagePath, 
      imageUrl, 
      includeFeatures = true, 
      includeTcmAnalysis = true,
      // 新增参数
      includeFiveElements = false,
      includeSpiritAnalysis = false,
      includeThreeZones = false,
      includeTextureAnalysis = false,
      includeFaceProportion = false
    } = params;
    
    // 原有的面部分析代码
    // ...
    
    // 构造结果对象
    const result: FaceAnalysisResult = {
      id: uuidv4(),
      userId,
      timestamp: new Date(),
      imageUrl: publicUrl,
      imagePath: savedImagePath,
      faceDetected: true,
      confidence: confidence,
      processingTime: Date.now() - startTime
    };
    
    // 如果需要包含面部特征
    if (includeFeatures) {
      result.faceFeatures = await this.extractFaceFeatures(savedImagePath);
    }
    
    // 如果需要包含中医分析
    if (includeTcmAnalysis) {
      result.tcmAnalysis = await this.performTcmAnalysis(savedImagePath, result.faceFeatures);
    }
    
    // 新增：如果需要包含五行分析
    if (includeFiveElements && config.lookingDiagnosis.advancedAnalysis.enableFiveElements) {
      try {
        result.fiveElementsAnalysis = await this.analyzeFaceFiveElements(result.id, userId);
      } catch (err) {
        logger.warn('五行分析失败，继续其他分析', { userId, error: err.message });
      }
    }
    
    // 新增：如果需要包含神气分析
    if (includeSpiritAnalysis && config.lookingDiagnosis.advancedAnalysis.enableSpiritAnalysis) {
      try {
        result.spiritAnalysis = await this.analyzeFaceSpirit(result.id, userId);
      } catch (err) {
        logger.warn('神气分析失败，继续其他分析', { userId, error: err.message });
      }
    }
    
    // 新增：如果需要包含三停分析
    if (includeThreeZones && config.lookingDiagnosis.advancedAnalysis.enableThreeZones) {
      try {
        result.threeZonesAnalysis = await this.analyzeThreeZones(result.id, userId);
      } catch (err) {
        logger.warn('三停分析失败，继续其他分析', { userId, error: err.message });
      }
    }
    
    // 新增：如果需要包含面部纹理分析
    if (includeTextureAnalysis && config.lookingDiagnosis.advancedAnalysis.enableTextureAnalysis) {
      try {
        result.textureAnalysis = await this.analyzeTexture(result.id, userId);
      } catch (err) {
        logger.warn('面部纹理分析失败，继续其他分析', { userId, error: err.message });
      }
    }
    
    // 新增：如果需要包含面部比例分析
    if (includeFaceProportion && config.lookingDiagnosis.advancedAnalysis.enableFaceProportion) {
      try {
        result.faceProportionAnalysis = await this.analyzeFaceProportion(result.id, userId);
      } catch (err) {
        logger.warn('面部比例分析失败，继续其他分析', { userId, error: err.message });
      }
    }
    
    // 缓存结果并返回
    this.resultCache.set(result.id, result);
    return result;
  }
  
  // 扩展建议生成方法，以考虑新的分析结果
  private async generateRecommendations(
    constitutionAnalysis: any,
    healthStatus: any,
    physiqueAnalysis?: any,
    dynamicFeaturesAnalysis?: any
  ): Promise<Recommendation[]> {
    try {
      // 构建请求数据
      const requestData: any = {
        constitutionAnalysis,
        healthStatus
      };
      
      // 添加形体分析数据（如果有）
      if (physiqueAnalysis) {
        requestData.physiqueAnalysis = physiqueAnalysis;
      }
      
      // 添加动态特征分析数据（如果有）
      if (dynamicFeaturesAnalysis) {
        requestData.dynamicFeaturesAnalysis = dynamicFeaturesAnalysis;
      }
      
      // 调用知识图谱服务生成建议
      const response = await this.knowledgeGraphService.generateRecommendations(requestData);
      return response.recommendations;
    } catch (error) {
      logger.error('生成建议失败', { error: error.message });
      return [];
    }
  }

  /**
   * 增强面色与五行分析关联
   */
  private async analyzeColorFiveElements(faceColor: string): Promise<{
    dominantElement: FiveElements;
    elementDistribution: Record<FiveElements, number>;
    description: string;
  }> {
    const colorMap = {
      '青': FiveElements.WOOD,   // 青色对应木
      '红': FiveElements.FIRE,   // 红色对应火
      '黄': FiveElements.EARTH,  // 黄色对应土
      '白': FiveElements.METAL,  // 白色对应金
      '黑': FiveElements.WATER,  // 黑色对应水
      '苍白': FiveElements.METAL,
      '淡白': FiveElements.METAL,
      '灰白': FiveElements.METAL,
      '萎黄': FiveElements.EARTH,
      '橘黄': FiveElements.EARTH,
      '青紫': FiveElements.WOOD,
      '暗红': FiveElements.FIRE,
      '淡红': FiveElements.FIRE,
      '暗黑': FiveElements.WATER
    };

    // 色泽深浅的修正系数
    const intensityAdjustment = {
      '暗': 0.8,  // 暗色降低对应五行强度
      '淡': 0.7,  // 淡色降低对应五行强度
      '鲜': 1.2,  // 鲜色增加对应五行强度
      '明': 1.1   // 明亮色增加对应五行强度
    };

    // 初始化五行分布
    const elementDistribution = {
      [FiveElements.WOOD]: 0,
      [FiveElements.FIRE]: 0,
      [FiveElements.EARTH]: 0,
      [FiveElements.METAL]: 0,
      [FiveElements.WATER]: 0
    };

    // 获取主要色彩
    let dominantElement = FiveElements.EARTH; // 默认土
    let maxScore = 0;

    // 分析主色与修饰词
    Object.keys(colorMap).forEach(colorKey => {
      if (faceColor.includes(colorKey)) {
        const element = colorMap[colorKey];
        let score = 1.0;
        
        // 应用修正系数
        Object.keys(intensityAdjustment).forEach(intensity => {
          if (faceColor.includes(intensity)) {
            score *= intensityAdjustment[intensity];
          }
        });
        
        elementDistribution[element] += score;
        
        if (elementDistribution[element] > maxScore) {
          maxScore = elementDistribution[element];
          dominantElement = element;
        }
      }
    });

    // 确保总分为1，转换为百分比
    const total = Object.values(elementDistribution).reduce((sum, value) => sum + value, 0) || 1;
    Object.keys(elementDistribution).forEach(key => {
      elementDistribution[key] = (elementDistribution[key] / total) * 100;
    });

    // 生成描述
    const elementNames = {
      [FiveElements.WOOD]: '木',
      [FiveElements.FIRE]: '火',
      [FiveElements.EARTH]: '土',
      [FiveElements.METAL]: '金',
      [FiveElements.WATER]: '水'
    };

    const description = `面色以${elementNames[dominantElement]}的特性为主，显示${elementNames[dominantElement]}属性占比${Math.round(elementDistribution[dominantElement])}%。`;

    return {
      dominantElement,
      elementDistribution,
      description
    };
  }

  /**
   * 增强舌象区域分析
   */
  private async analyzeTongueRegions(tongueImage: Buffer): Promise<TongueFeatures['regionalAnalysis']> {
    try {
      // 调用图像处理服务进行舌象区域分割
      const response = await this.imageProcessorService.segmentTongueRegions(tongueImage);
      
      // 分析舌尖（心）
      const tipAnalysis = {
        color: response.regions.tip.color,
        features: response.regions.tip.features,
        organRelation: '心'
      };
      
      // 分析舌中（脾胃）
      const centerAnalysis = {
        color: response.regions.center.color,
        features: response.regions.center.features,
        organRelation: '脾胃'
      };
      
      // 分析舌边（肝胆）
      const sidesAnalysis = {
        color: response.regions.sides.color,
        features: response.regions.sides.features,
        organRelation: '肝胆'
      };
      
      // 分析舌根（肾）
      const rootAnalysis = {
        color: response.regions.root.color,
        features: response.regions.root.features,
        organRelation: '肾'
      };
      
      return {
        tip: tipAnalysis,
        center: centerAnalysis,
        sides: sidesAnalysis,
        root: rootAnalysis
      };
    } catch (error) {
      console.error('舌象区域分析错误:', error);
      return null;
    }
  }

  /**
   * 分析舌象微循环状态
   */
  private async analyzeTongueMicrocirculation(tongueImage: Buffer): Promise<TongueFeatures['microcirculation']> {
    try {
      // 获取舌象血管特征和微循环指标
      const microcirculationData = await this.imageProcessorService.extractMicrocirculationFeatures(tongueImage);
      
      // 分析微循环状态
      let status: 'normal' | 'impaired' | 'severely_impaired';
      const features = [];
      
      if (microcirculationData.vesselDensity < 0.3) {
        status = 'severely_impaired';
        features.push('血管密度显著减少');
      } else if (microcirculationData.vesselDensity < 0.6) {
        status = 'impaired';
        features.push('血管密度减少');
      } else {
        status = 'normal';
        features.push('血管密度正常');
      }
      
      if (microcirculationData.tortuosity > 1.5) {
        features.push('血管弯曲度增加');
        status = status === 'normal' ? 'impaired' : status;
      }
      
      if (microcirculationData.branchingPattern === 'irregular') {
        features.push('血管分支模式不规则');
        status = status === 'normal' ? 'impaired' : status;
      }
      
      return {
        status,
        features,
        confidence: microcirculationData.confidence
      };
    } catch (error) {
      console.error('舌象微循环分析错误:', error);
      return null;
    }
  }

  /**
   * 分析舌象病机
   */
  private async analyzeTonguePathogenicMechanism(tongueFeatures: TongueFeatures): Promise<TongueFeatures['pathogenicMechanism']> {
    const externalPathogens = [];
    const internalImbalance = [];
    let confidence = 0.7;
    
    // 分析外感病邪
    if (tongueFeatures.tongueBody.color.includes('红')) {
      externalPathogens.push('热邪');
      confidence += 0.05;
    }
    
    if (tongueFeatures.tongueCoating.color.includes('白') && 
        tongueFeatures.tongueCoating.thickness > 0.5) {
      externalPathogens.push('寒邪');
      confidence += 0.05;
    }
    
    if (tongueFeatures.tongueCoating.color.includes('黄')) {
      externalPathogens.push('湿热');
      confidence += 0.05;
    }
    
    // 分析内伤病机
    if (tongueFeatures.tongueBody.color.includes('淡') || 
        tongueFeatures.tongueBody.color.includes('白')) {
      internalImbalance.push('气血亏虚');
      confidence += 0.05;
    }
    
    if (tongueFeatures.tongueBody.color.includes('紫') || 
        tongueFeatures.tongueBody.spots && 
        tongueFeatures.tongueBody.spots.length > 0) {
      internalImbalance.push('血瘀');
      confidence += 0.05;
    }
    
    if (tongueFeatures.tongueBody.cracks && 
        tongueFeatures.tongueBody.cracks.length > 0) {
      internalImbalance.push('阴虚');
      confidence += 0.05;
    }
    
    if (tongueFeatures.tongueBody.toothMarks) {
      internalImbalance.push('脾虚');
      confidence += 0.05;
    }
    
    // 确保置信度不超过1.0
    confidence = Math.min(confidence, 1.0);
    
    return {
      externalPathogens,
      internalImbalance,
      confidence
    };
  }

  /**
   * 分析舌象色彩与五脏的联系
   */
  private async analyzeTongueColorOrganRelation(tongueColor: string): Promise<any> {
    const colorOrganMap = {
      'pale': { organ: '脾肺', description: '脾肺气虚，气血不足', confidence: 0.85 },
      'pink': { organ: '脾胃', description: '脾胃功能正常', confidence: 0.9 },
      'red': { organ: '心', description: '心火旺盛，阴虚火旺', confidence: 0.85 },
      'scarlet': { organ: '心肝', description: '心肝火盛，热毒内盛', confidence: 0.8 },
      'purple': { organ: '肝', description: '肝郁血瘀，气滞血瘀', confidence: 0.85 },
      'bluish': { organ: '肾', description: '肾阳不足，寒凝血瘀', confidence: 0.8 },
      'yellow': { organ: '脾胃', description: '脾胃湿热，消化不良', confidence: 0.85 }
    };

    // 若是复合色，需要分析各组成部分
    const colors = tongueColor.split('-');
    if (colors.length === 1 && colorOrganMap[tongueColor]) {
      return colorOrganMap[tongueColor];
    }

    // 处理复合色
    const results = colors
      .filter(color => colorOrganMap[color])
      .map(color => colorOrganMap[color]);

    if (results.length === 0) {
      return { organ: '未知', description: '无法确定舌色与脏腑的关系', confidence: 0.5 };
    }

    // 取置信度最高的结果
    return results.sort((a, b) => b.confidence - a.confidence)[0];
  }

  /**
   * 分析舌象苔与六腑的联系
   */
  private async analyzeTongueCoatingOrganRelation(coating: string): Promise<any> {
    const coatingOrganMap = {
      'thin': { organ: '正常', description: '体内津液正常', confidence: 0.9 },
      'thick': { organ: '胃肠', description: '胃肠湿浊较重', confidence: 0.85 },
      'white': { organ: '肺胃', description: '外感风寒或胃寒', confidence: 0.85 },
      'yellow': { organ: '胆胃', description: '胃热或肠胃湿热', confidence: 0.85 },
      'gray': { organ: '肠', description: '湿热较甚或瘀滞', confidence: 0.8 },
      'black': { organ: '肾', description: '内寒重或热极生寒', confidence: 0.8 },
      'greasy': { organ: '脾胃', description: '痰湿内蕴', confidence: 0.85 },
      'dry': { organ: '胃', description: '胃阴不足或热盛伤津', confidence: 0.85 }
    };

    // 解析复合苔象
    const coatings = coating.split('-');
    if (coatings.length === 1 && coatingOrganMap[coating]) {
      return coatingOrganMap[coating];
    }

    // 处理复合苔象
    const results = coatings
      .filter(c => coatingOrganMap[c])
      .map(c => coatingOrganMap[c]);

    if (results.length === 0) {
      return { organ: '未知', description: '无法确定舌苔与腑脏的关系', confidence: 0.5 };
    }

    // 取置信度最高的结果
    return results.sort((a, b) => b.confidence - a.confidence)[0];
  }

  /**
   * 分析面部颜色与五脏的精细联系
   */
  public async analyzeFaceColorOrganRelation(
    faceAnalysisResult: FaceAnalysisResult
  ): Promise<{
    mainOrgan: string;
    secondaryOrgans: string[];
    description: string;
    confidence: number;
  }> {
    if (!faceAnalysisResult.faceFeatures || !faceAnalysisResult.faceFeatures.complexion) {
      return {
        mainOrgan: '未知',
        secondaryOrgans: [],
        description: '无法分析面色与脏腑关系',
        confidence: 0
      };
    }
    
    const { complexion, facialLandmarks } = faceAnalysisResult.faceFeatures;
    const mainColor = complexion.main;
    
    // 面色与脏腑对应关系
    const colorOrganMap = {
      'red': { organ: '心', description: '心火旺盛或热证', confidence: 0.85 },
      'yellow': { organ: '脾', description: '脾虚湿盛或湿热证', confidence: 0.85 },
      'white': { organ: '肺', description: '肺气虚弱或气血不足', confidence: 0.85 },
      'dark': { organ: '肾', description: '肾精不足或寒证', confidence: 0.85 },
      'greenish': { organ: '肝', description: '肝气郁结或寒凝', confidence: 0.85 },
      'purple': { organ: '血', description: '血瘀或寒凝血瘀', confidence: 0.8 }
    };
    
    // 区域精细化分析
    const regionAnalysis = complexion.regions || {};
    const fiveRegions = {
      forehead: regionAnalysis.forehead || complexion.main, // 额部对应膀胱、小肠
      eyes: regionAnalysis.eyes || complexion.main,        // 眼部对应肝
      cheeks: regionAnalysis.cheeks || complexion.main,    // 颧部对应肺
      nose: regionAnalysis.nose || complexion.main,        // 鼻部对应脾胃
      chin: regionAnalysis.chin || complexion.main         // 颏部对应肾
    };
    
    // 计算主要脏腑
    let organScores = {
      '心': 0,
      '肝': 0,
      '脾': 0,
      '肺': 0,
      '肾': 0,
      '血': 0
    };
    
    // 添加主色分析
    if (colorOrganMap[mainColor]) {
      const mainOrgan = colorOrganMap[mainColor].organ;
      organScores[mainOrgan] += 5;
    }
    
    // 区域分析权重
    if (colorOrganMap[fiveRegions.forehead]) {
      organScores['膀胱'] = (organScores['膀胱'] || 0) + 2;
      organScores['小肠'] = (organScores['小肠'] || 0) + 2;
    }
    
    if (colorOrganMap[fiveRegions.eyes]) {
      organScores['肝'] += 3;
    }
    
    if (colorOrganMap[fiveRegions.cheeks]) {
      organScores['肺'] += 3;
    }
    
    if (colorOrganMap[fiveRegions.nose]) {
      organScores['脾'] += 2;
      organScores['胃'] = (organScores['胃'] || 0) + 2;
    }
    
    if (colorOrganMap[fiveRegions.chin]) {
      organScores['肾'] += 3;
    }
    
    // 排序获得主要和次要脏腑
    const sortedOrgans = Object.entries(organScores)
      .filter(([_, score]) => score > 0)
      .sort((a, b) => b[1] - a[1]);
    
    if (sortedOrgans.length === 0) {
      return {
        mainOrgan: '未知',
        secondaryOrgans: [],
        description: '无法确定面色与脏腑关系',
        confidence: 0.5
      };
    }
    
    const mainOrgan = sortedOrgans[0][0];
    const secondaryOrgans = sortedOrgans.slice(1, 4).map(item => item[0]);
    
    // 生成描述
    let description = `面色主要反映${mainOrgan}的状态`;
    if (secondaryOrgans.length > 0) {
      description += `，同时与${secondaryOrgans.join('、')}有关联`;
    }
    
    if (colorOrganMap[mainColor]) {
      description += `。整体面色表现为${colorOrganMap[mainColor].description}`;
    }
    
    return {
      mainOrgan,
      secondaryOrgans,
      description,
      confidence: sortedOrgans[0][1] / 10 // 归一化置信度
    };
  }

  /**
   * 整合五行理论分析面部特征
   */
  public async performIntegratedFiveElementsAnalysis(
    faceAnalysisResult: FaceAnalysisResult
  ): Promise<{
    dominantElement: FiveElements;
    elementDistribution: Record<FiveElements, number>;
    organImbalances: string[];
    recommendations: string[];
  }> {
    // 已有的面色五行分析
    const colorAnalysis = await this.analyzeColorFiveElements(
      faceAnalysisResult.faceFeatures?.complexion?.main || 'neutral'
    );
    
    // 获取面部分区分析
    const faceZones = await this.analyzeThreeZones(
      faceAnalysisResult.id,
      faceAnalysisResult.userId
    );
    
    // 获取精神分析
    const spiritAnalysis = await this.analyzeFaceSpirit(
      faceAnalysisResult.id,
      faceAnalysisResult.userId
    );
    
    // 综合五行得分
    const elementScores = {
      [FiveElements.WOOD]: 0, // 木
      [FiveElements.FIRE]: 0, // 火
      [FiveElements.EARTH]: 0, // 土
      [FiveElements.METAL]: 0, // 金
      [FiveElements.WATER]: 0  // 水
    };
    
    // 整合面色分析结果
    if (colorAnalysis.elementDistribution) {
      Object.entries(colorAnalysis.elementDistribution).forEach(([element, score]) => {
        elementScores[element] += score * 3; // 面色加权
      });
    }
    
    // 整合三区分析
    if (faceZones && faceZones.zoneAnalysis) {
      // 上区主火，中区主土，下区主水
      if (faceZones.zoneAnalysis.upperZone && faceZones.zoneAnalysis.upperZone.condition === 'excess') {
        elementScores[FiveElements.FIRE] += 2;
      } else if (faceZones.zoneAnalysis.upperZone && faceZones.zoneAnalysis.upperZone.condition === 'deficiency') {
        elementScores[FiveElements.FIRE] -= 2;
      }
      
      if (faceZones.zoneAnalysis.middleZone && faceZones.zoneAnalysis.middleZone.condition === 'excess') {
        elementScores[FiveElements.EARTH] += 2;
      } else if (faceZones.zoneAnalysis.middleZone && faceZones.zoneAnalysis.middleZone.condition === 'deficiency') {
        elementScores[FiveElements.EARTH] -= 2;
      }
      
      if (faceZones.zoneAnalysis.lowerZone && faceZones.zoneAnalysis.lowerZone.condition === 'excess') {
        elementScores[FiveElements.WATER] += 2;
      } else if (faceZones.zoneAnalysis.lowerZone && faceZones.zoneAnalysis.lowerZone.condition === 'deficiency') {
        elementScores[FiveElements.WATER] -= 2;
      }
    }
    
    // 整合精神分析
    if (spiritAnalysis && spiritAnalysis.spiritLevel) {
      // 精神充沛-火旺，精神萎靡-水弱
      const spiritScoreMap = {
        'excellent': { element: FiveElements.FIRE, score: 3 },
        'good': { element: FiveElements.FIRE, score: 2 },
        'average': { element: FiveElements.EARTH, score: 1 },
        'poor': { element: FiveElements.WATER, score: -2 },
        'very_poor': { element: FiveElements.WATER, score: -3 }
      };
      
      const spiritMapping = spiritScoreMap[spiritAnalysis.spiritLevel];
      if (spiritMapping) {
        elementScores[spiritMapping.element] += spiritMapping.score;
      }
    }
    
    // 归一化各元素分数到0-10
    const normalizedScores = {};
    const maxAbsScore = Math.max(...Object.values(elementScores).map(Math.abs));
    Object.entries(elementScores).forEach(([element, score]) => {
      normalizedScores[element] = 5 + (score / (maxAbsScore || 1)) * 5;
      normalizedScores[element] = Math.max(0, Math.min(10, normalizedScores[element]));
    });
    
    // 确定主导五行
    const dominantElement = Object.entries(normalizedScores)
      .sort((a, b) => b[1] - a[1])[0][0] as FiveElements;
    
    // 分析五行失衡导致的脏腑问题
    const organImbalances = this.analyzeOrganImbalancesFromElements(normalizedScores);
    
    // 根据五行分析生成调理建议
    const recommendations = await this.generateFiveElementsRecommendations(
      dominantElement,
      normalizedScores,
      organImbalances
    );
    
    return {
      dominantElement,
      elementDistribution: normalizedScores as Record<FiveElements, number>,
      organImbalances,
      recommendations
    };
  }

  /**
   * 根据五行分析脏腑失衡
   */
  private analyzeOrganImbalancesFromElements(
    elementScores: Record<string, number>
  ): string[] {
    const imbalances = [];
    const threshold = 3; // 阈值：高于7或低于3视为失衡
    
    // 五行与脏腑对应关系
    const elementOrganMap = {
      [FiveElements.WOOD]: { organ: '肝胆', excess: '肝火旺', deficiency: '肝血虚' },
      [FiveElements.FIRE]: { organ: '心小肠', excess: '心火亢', deficiency: '心阳虚' },
      [FiveElements.EARTH]: { organ: '脾胃', excess: '脾湿重', deficiency: '脾气虚' },
      [FiveElements.METAL]: { organ: '肺大肠', excess: '肺热盛', deficiency: '肺气虚' },
      [FiveElements.WATER]: { organ: '肾膀胱', excess: '肾阳亢', deficiency: '肾阴虚' }
    };
    
    // 检查各元素是否失衡
    Object.entries(elementScores).forEach(([element, score]) => {
      const mapping = elementOrganMap[element];
      if (!mapping) return;
      
      if (score > 7) {
        imbalances.push(`${mapping.excess}：${mapping.organ}功能亢进`);
      } else if (score < threshold) {
        imbalances.push(`${mapping.deficiency}：${mapping.organ}功能不足`);
      }
    });
    
    // 检查五行相克关系失衡
    const overactingRelations = [
      { controller: FiveElements.WOOD, controlled: FiveElements.EARTH, description: '肝木过旺克脾土' },
      { controller: FiveElements.FIRE, controlled: FiveElements.METAL, description: '心火过旺克肺金' },
      { controller: FiveElements.EARTH, controlled: FiveElements.WATER, description: '脾土过旺克肾水' },
      { controller: FiveElements.METAL, controlled: FiveElements.WOOD, description: '肺金过旺克肝木' },
      { controller: FiveElements.WATER, controlled: FiveElements.FIRE, description: '肾水过旺克心火' }
    ];
    
    overactingRelations.forEach(relation => {
      const controllerScore = elementScores[relation.controller];
      const controlledScore = elementScores[relation.controlled];
      
      if (controllerScore > 7 && controlledScore < threshold) {
        imbalances.push(`${relation.description}：五行相克关系失衡`);
      }
    });
    
    return imbalances;
  }

  /**
   * 生成基于五行理论的调理建议
   */
  private async generateFiveElementsRecommendations(
    dominantElement: FiveElements,
    elementScores: Record<string, number>,
    organImbalances: string[]
  ): Promise<string[]> {
    const recommendations = [];
    
    // 基于主导五行的一般建议
    const elementRecommendations = {
      [FiveElements.WOOD]: [
        '调畅情志，保持心情舒畅',
        '适当进行舒缓运动如太极、瑜伽',
        '饮食宜清淡，忌辛辣刺激'
      ],
      [FiveElements.FIRE]: [
        '保持心情平和，避免情绪激动',
        '作息规律，保证充足睡眠',
        '饮食宜清凉，可适量食用苦味食物'
      ],
      [FiveElements.EARTH]: [
        '饮食规律，避免过度思虑',
        '适当食用健脾养胃的食物',
        '保持乐观心态，增强中气'
      ],
      [FiveElements.METAL]: [
        '注意呼吸健康，避免污浊环境',
        '保持情绪稳定，预防肺气失宣',
        '饮食宜温润，可适量食用辛味食物'
      ],
      [FiveElements.WATER]: [
        '注意保暖，预防寒邪侵袭',
        '适当进行温和运动如散步、游泳',
        '合理作息，避免过度劳累'
      ]
    };
    
    // 添加主导五行的一般建议
    recommendations.push(...(elementRecommendations[dominantElement] || []));
    
    // 基于脏腑失衡的特定建议
    const imbalancePatterns = {
      '肝火旺': [
        '饮食宜清淡，避免辛辣刺激',
        '保持情绪平和，避免暴怒',
        '可适量食用菊花、枸杞等清肝明目的食物'
      ],
      '肝血虚': [
        '注意休息，避免过度用眼',
        '可适量食用桑葚、黑芝麻等补肝血的食物',
        '保持规律作息，早睡早起'
      ],
      '心火亢': [
        '保持心情平静，避免过度兴奋',
        '适当进行冥想或深呼吸放松练习',
        '可适量食用莲子、百合等清心安神的食物'
      ],
      '心阳虚': [
        '注意保暖，避免受寒',
        '可适量食用桂圆、红枣等温补心阳的食物',
        '保持积极乐观的心态'
      ],
      '脾湿重': [
        '饮食宜清淡，避免过度油腻',
        '适当运动，促进水湿代谢',
        '可适量食用薏米、赤小豆等健脾利湿的食物'
      ],
      '脾气虚': [
        '饮食规律，少食多餐',
        '避免过度思虑和劳累',
        '可适量食用山药、大枣等补脾益气的食物'
      ],
      '肺热盛': [
        '保持室内空气流通',
        '避免接触烟尘等刺激物',
        '可适量食用梨、杏等清肺润燥的食物'
      ],
      '肺气虚': [
        '注意保暖，预防感冒',
        '适当进行呼吸训练和胸式呼吸',
        '可适量食用百合、蜂蜜等补肺益气的食物'
      ],
      '肾阳亢': [
        '保持情绪稳定，避免过度劳累',
        '避免久坐和熬夜',
        '可适量食用菊花、甘蔗等滋阴清热的食物'
      ],
      '肾阴虚': [
        '保持充足睡眠，避免过度劳累',
        '减少辛辣刺激性食物',
        '可适量食用黑芝麻、枸杞等滋补肾阴的食物'
      ]
    };
    
    // 根据失衡添加特定建议
    organImbalances.forEach(imbalance => {
      const pattern = Object.keys(imbalancePatterns).find(pattern => imbalance.includes(pattern));
      if (pattern && imbalancePatterns[pattern]) {
        recommendations.push(...imbalancePatterns[pattern]);
      }
    });
    
    // 去重
    return [...new Set(recommendations)];
  }

  /**
   * 整合四诊合参分析
   */
  public async integrateWithOtherDiagnosticMethods(
    lookingResults: DiagnosticResult,
    inquiryResults?: any,
    listeningResults?: any,
    touchingResults?: any
  ): Promise<{
    integratedDiagnosis: string;
    confidenceScore: number;
    constitutionTypes: string[];
    recommendations: string[];
    warningSigns: string[];
  }> {
    // 初始化权重和得分记录
    const patternScores = {};
    const constitutionScores = {};
    
    // 整合望诊结果
    if (lookingResults && lookingResults.tcmPatterns) {
      lookingResults.tcmPatterns.forEach(pattern => {
        patternScores[pattern.name] = (patternScores[pattern.name] || 0) + (pattern.confidence * 3);
      });
      
      if (lookingResults.constitutionTypes) {
        lookingResults.constitutionTypes.forEach(type => {
          constitutionScores[type.name] = (constitutionScores[type.name] || 0) + (type.confidence * 3);
        });
      }
    }
    
    // 整合问诊结果（权重高）
    if (inquiryResults && inquiryResults.tcmPatterns) {
      inquiryResults.tcmPatterns.forEach(pattern => {
        patternScores[pattern.name] = (patternScores[pattern.name] || 0) + (pattern.confidence * 4);
      });
      
      if (inquiryResults.constitutionTypes) {
        inquiryResults.constitutionTypes.forEach(type => {
          constitutionScores[type.name] = (constitutionScores[type.name] || 0) + (type.confidence * 4);
        });
      }
    }
    
    // 整合闻诊结果
    if (listeningResults && listeningResults.tcmPatterns) {
      listeningResults.tcmPatterns.forEach(pattern => {
        patternScores[pattern.name] = (patternScores[pattern.name] || 0) + (pattern.confidence * 2.5);
      });
      
      if (listeningResults.constitutionTypes) {
        listeningResults.constitutionTypes.forEach(type => {
          constitutionScores[type.name] = (constitutionScores[type.name] || 0) + (type.confidence * 2.5);
        });
      }
    }
    
    // 整合切诊结果
    if (touchingResults && touchingResults.tcmPatterns) {
      touchingResults.tcmPatterns.forEach(pattern => {
        patternScores[pattern.name] = (patternScores[pattern.name] || 0) + (pattern.confidence * 3.5);
      });
      
      if (touchingResults.constitutionTypes) {
        touchingResults.constitutionTypes.forEach(type => {
          constitutionScores[type.name] = (constitutionScores[type.name] || 0) + (type.confidence * 3.5);
        });
      }
    }
    
    // 排序获取主要证型和体质类型
    const sortedPatterns = Object.entries(patternScores)
      .sort((a, b) => b[1] - a[1]);
    
    const sortedConstitutions = Object.entries(constitutionScores)
      .sort((a, b) => b[1] - a[1]);
    
    // 确定主要诊断结果
    const mainPattern = sortedPatterns.length > 0 ? sortedPatterns[0][0] : '未能确定证型';
    const secondaryPatterns = sortedPatterns.slice(1, 3).map(p => p[0]);
    
    const integratedDiagnosis = mainPattern + 
      (secondaryPatterns.length > 0 ? `，兼有${secondaryPatterns.join('、')}` : '');
    
    // 提取主要体质类型
    const constitutionTypes = sortedConstitutions
      .filter(c => c[1] > 5) // 只选择得分高于阈值的体质
      .map(c => c[0]);
    
    // 计算整体置信度
    const confidenceScore = sortedPatterns.length > 0 ? 
      Math.min(sortedPatterns[0][1] / 13, 0.95) : 0.3; // 归一化到0-1范围
    
    // 综合调理建议
    const recommendations = await this.generateIntegratedRecommendations(
      mainPattern,
      secondaryPatterns,
      constitutionTypes
    );
    
    // 分析可能的警示信号
    const warningSignals = this.identifyWarningSignals(
      lookingResults, 
      inquiryResults, 
      listeningResults, 
      touchingResults
    );
    
    return {
      integratedDiagnosis,
      confidenceScore,
      constitutionTypes,
      recommendations,
      warningSigns: warningSignals
    };
  }

  /**
   * 生成整合的调理建议
   */
  private async generateIntegratedRecommendations(
    mainPattern: string,
    secondaryPatterns: string[],
    constitutionTypes: string[]
  ): Promise<string[]> {
    // 从知识图谱获取相关建议
    const knowledgeRecommendations = await this.knowledgeGraphService.getRecommendationsForPattern(mainPattern);

    // 补充针对次要证型的建议
    const secondaryRecommendations = await Promise.all(
      secondaryPatterns.map(pattern => 
        this.knowledgeGraphService.getRecommendationsForPattern(pattern)
      )
    );
    
    // 整合所有建议
    const allRecommendations = [
      ...(knowledgeRecommendations || []),
      ...(secondaryRecommendations.flat() || [])
    ];
    
    // 体质相关建议
    const constitutionRecommendations = await Promise.all(
      constitutionTypes.map(type => 
        this.knowledgeGraphService.getRecommendationsForConstitution(type)
      )
    );
    
    // 合并去重
    return [...new Set([
      ...allRecommendations,
      ...(constitutionRecommendations.flat() || [])
    ])];
  }

  /**
   * 识别可能的警示信号
   */
  private identifyWarningSignals(
    lookingResults: any,
    inquiryResults?: any,
    listeningResults?: any,
    touchingResults?: any
  ): string[] {
    const warningSignals = [];
    
    // 面色异常警示
    if (lookingResults?.faceFeatures?.complexion?.main === 'dark' || 
        lookingResults?.faceFeatures?.complexion?.main === 'purple') {
      warningSignals.push('面色晦暗或紫暗，可能提示气血运行不畅或内有瘀滞');
    }
    
    // 舌象异常警示
    if (lookingResults?.tongueFeatures?.tongueBody?.color === 'purple' ||
        lookingResults?.tongueFeatures?.tongueBody?.color === 'bluish') {
      warningSignals.push('舌质紫暗，提示内有瘀血或寒凝血瘀');
    }
    
    if (lookingResults?.tongueFeatures?.tongueBody?.cracks && 
        lookingResults?.tongueFeatures?.tongueBody?.cracks.length > 3) {
      warningSignals.push('舌体有明显裂纹，提示阴液亏虚或热盛伤阴');
    }
    
    // 问诊警示
    if (inquiryResults?.symptoms?.some(s => s.severity === 'severe' && s.duration > 14)) {
      warningSignals.push('严重症状持续时间超过两周，建议及时就医');
    }
    
    // 闻诊警示
    if (listeningResults?.anomalyDetection?.anomalyDetected) {
      warningSignals.push(listeningResults.anomalyDetection.description || 
        '声音或气味异常，建议进一步检查');
    }
    
    // 切诊警示
    if (touchingResults?.pulseAnalysis?.features?.some(f => 
        f.name === 'scattered' || f.name === 'intermittent')) {
      warningSignals.push('脉象散乱或间代，提示气血亏虚严重或内有危重病机');
    }
    
    return warningSignals;
  }
} 