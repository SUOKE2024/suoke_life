import { Logger } from '../utils/logger';
import { AppError } from '../middlewares/error.middleware';
import { 
  LookingDiagnosisClient, 
  SmellDiagnosisClient, 
  InquiryDiagnosisClient, 
  TouchDiagnosisClient 
} from './diagnosis-services-client';
import NodeCache from 'node-cache';
import { v4 as uuidv4 } from 'uuid';
import * as _ from 'lodash';
import database from '../utils/database';
import { FourDiagnosisRepository } from './four-diagnosis-repository';
import analysisEngine from './analysis-engine';
import healthSuggestions from './health-suggestions';
import { DiagnosisType } from '../interfaces/four-diagnosis.interface';
import { AnalysisEngine } from './analysis-engine';
import { Diagnosis } from '../models/diagnosis.model';
import { ConstitutionType, FourDiagnosisCoordinatorRequest } from '../interfaces/four-diagnosis.interface';
import { LookingService } from './looking.service';
import { SmellService } from './smell.service';
import { InquiryService } from './inquiry.service';
import { TouchService } from './touch.service';
import { HealthRecommendationService } from './health-recommendation.service';
import { ErrorType } from '../middlewares/error.middleware';

const logger = new Logger('FourDiagnosisCoordinatorService');

// 缓存，用于存储诊断结果
const diagnosisCache = new NodeCache({
  stdTTL: parseInt(process.env.CACHE_TTL || '3600', 10),
  checkperiod: 600,
  maxKeys: parseInt(process.env.DIAGNOSIS_CACHE_SIZE || '1000', 10)
});

/**
 * 四诊协调服务
 * 负责整合四诊数据，提供综合分析
 */
export class FourDiagnosisCoordinatorService {
  private lookingClient: LookingDiagnosisClient;
  private smellClient: SmellDiagnosisClient;
  private inquiryClient: InquiryDiagnosisClient;
  private touchClient: TouchDiagnosisClient;
  private repository: FourDiagnosisRepository;
  private analysisEngine = new AnalysisEngine();
  private lookingService = new LookingService();
  private smellService = new SmellService();
  private inquiryService = new InquiryService();
  private touchService = new TouchService();
  private healthRecommendationService = new HealthRecommendationService();
  
  constructor() {
    this.lookingClient = new LookingDiagnosisClient();
    this.smellClient = new SmellDiagnosisClient();
    this.inquiryClient = new InquiryDiagnosisClient();
    this.touchClient = new TouchDiagnosisClient();
    this.repository = new FourDiagnosisRepository();
    
    // 启动时连接数据库
    this.initializeDatabase();
    
    logger.info('四诊协调服务初始化完成');
  }
  
  /**
   * 初始化数据库连接
   */
  private async initializeDatabase(): Promise<void> {
    try {
      await database.connect();
      logger.info('数据库连接初始化成功');
    } catch (error) {
      logger.error('数据库连接初始化失败', { error });
    }
  }
  
  /**
   * 获取患者四诊数据
   */
  async getPatientFourDiagnosisData(patientId: string): Promise<any> {
    logger.info(`获取患者四诊数据: ${patientId}`);
    
    // 检查缓存
    const cacheKey = `patient:${patientId}:fourDiagnosis`;
    const cachedData = diagnosisCache.get(cacheKey);
    
    if (cachedData) {
      logger.debug(`使用缓存的四诊数据: ${patientId}`);
      return cachedData;
    }
    
    // 首先尝试从数据库中获取最新记录
    try {
      const latestData = await this.repository.getLatestFourDiagnosisData(patientId);
      
      if (latestData) {
        logger.debug(`从数据库获取四诊数据: ${patientId}`);
        
        // 更新缓存
        diagnosisCache.set(cacheKey, latestData);
        
        return latestData;
      }
    } catch (error) {
      logger.warn(`从数据库获取四诊数据失败: ${patientId}`, { error });
      // 继续从各诊断服务获取数据
    }
    
    // 并行获取四诊数据
    try {
      const [lookingData, smellData, inquiryData, touchData] = await Promise.all([
        this.lookingClient.getPatientData(patientId).catch(err => {
          logger.warn(`获取望诊数据失败: ${patientId}`, { error: err.message });
          return null;
        }),
        this.smellClient.getPatientData(patientId).catch(err => {
          logger.warn(`获取闻诊数据失败: ${patientId}`, { error: err.message });
          return null;
        }),
        this.inquiryClient.getPatientData(patientId).catch(err => {
          logger.warn(`获取问诊数据失败: ${patientId}`, { error: err.message });
          return null;
        }),
        this.touchClient.getPatientData(patientId).catch(err => {
          logger.warn(`获取切诊数据失败: ${patientId}`, { error: err.message });
          return null;
        })
      ]);
      
      // 整合四诊数据
      const fourDiagnosisData = {
        patientId,
        timestamp: new Date(),
        looking: lookingData?.data,
        smell: smellData?.data,
        inquiry: inquiryData?.data,
        touch: touchData?.data,
        integratedAssessment: null, // 尚未进行综合分析
        diagnosisId: uuidv4()
      };
      
      // 缓存数据
      diagnosisCache.set(cacheKey, fourDiagnosisData);
      
      return fourDiagnosisData;
    } catch (error) {
      logger.error(`获取四诊数据失败: ${patientId}`, { error });
      throw new AppError('获取四诊数据失败', 500);
    }
  }
  
  /**
   * 分析患者四诊数据，提供综合诊断
   */
  async analyzeFourDiagnosis(patientId: string): Promise<any> {
    logger.info(`分析患者四诊数据: ${patientId}`);
    
    try {
      // 首先获取最新的四诊数据
      const fourDiagnosisData = await this.getPatientFourDiagnosisData(patientId);
      
      // 请求各诊断服务进行分析
      const analysisPromises = [];
      
      if (!fourDiagnosisData.looking?.overallAssessment) {
        analysisPromises.push(
          this.lookingClient.requestAnalysis(patientId).catch(err => {
            logger.warn(`望诊分析失败: ${patientId}`, { error: err.message });
            return null;
          })
        );
      }
      
      if (!fourDiagnosisData.smell?.overallAssessment) {
        analysisPromises.push(
          this.smellClient.requestAnalysis(patientId).catch(err => {
            logger.warn(`闻诊分析失败: ${patientId}`, { error: err.message });
            return null;
          })
        );
      }
      
      if (!fourDiagnosisData.inquiry?.overallAssessment) {
        analysisPromises.push(
          this.inquiryClient.requestAnalysis(patientId).catch(err => {
            logger.warn(`问诊分析失败: ${patientId}`, { error: err.message });
            return null;
          })
        );
      }
      
      if (!fourDiagnosisData.touch?.overallAssessment) {
        analysisPromises.push(
          this.touchClient.requestAnalysis(patientId).catch(err => {
            logger.warn(`切诊分析失败: ${patientId}`, { error: err.message });
            return null;
          })
        );
      }
      
      // 等待所有分析完成
      if (analysisPromises.length > 0) {
        await Promise.all(analysisPromises);
      }
      
      // 再次获取最新的四诊数据（包含各自的分析结果）
      const updatedFourDiagnosisData = await this.getPatientFourDiagnosisData(patientId);
      
      // 执行四诊合参分析
      const integratedAssessment = analysisEngine.performIntegratedAnalysis(updatedFourDiagnosisData);
      
      // 生成健康建议
      integratedAssessment.healthSuggestions = healthSuggestions.generateComprehensiveSuggestions({
        ...updatedFourDiagnosisData,
        integratedAssessment
      });
      
      // 更新综合分析结果
      updatedFourDiagnosisData.integratedAssessment = integratedAssessment;
      
      // 更新缓存
      const cacheKey = `patient:${patientId}:fourDiagnosis`;
      diagnosisCache.set(cacheKey, updatedFourDiagnosisData);
      
      // 持久化分析结果
      await this.saveDiagnosisResult(updatedFourDiagnosisData);
      
      return updatedFourDiagnosisData;
    } catch (error) {
      logger.error(`四诊合参分析失败: ${patientId}`, { error });
      throw new AppError('四诊合参分析失败', 500);
    }
  }
  
  /**
   * 持久化诊断结果
   */
  private async saveDiagnosisResult(diagnosisData: any): Promise<void> {
    logger.info(`持久化诊断结果: ${diagnosisData.patientId}`);
    
    try {
      // 保存各个诊断分析结果
      const savedAnalysis = {
        looking: null,
        smell: null,
        inquiry: null,
        touch: null,
      };
      
      if (diagnosisData.looking) {
        savedAnalysis.looking = await this.repository.saveDiagnosisAnalysis({
          diagnosisType: DiagnosisType.LOOKING,
          timestamp: diagnosisData.timestamp,
          findings: diagnosisData.looking.findings || [],
          overallAssessment: diagnosisData.looking.overallAssessment || '',
          confidence: diagnosisData.looking.confidence || 0,
          rawData: diagnosisData.looking
        });
      }
      
      if (diagnosisData.smell) {
        savedAnalysis.smell = await this.repository.saveDiagnosisAnalysis({
          diagnosisType: DiagnosisType.SMELL,
          timestamp: diagnosisData.timestamp,
          findings: diagnosisData.smell.findings || [],
          overallAssessment: diagnosisData.smell.overallAssessment || '',
          confidence: diagnosisData.smell.confidence || 0,
          rawData: diagnosisData.smell
        });
      }
      
      if (diagnosisData.inquiry) {
        savedAnalysis.inquiry = await this.repository.saveDiagnosisAnalysis({
          diagnosisType: DiagnosisType.INQUIRY,
          timestamp: diagnosisData.timestamp,
          findings: diagnosisData.inquiry.findings || [],
          overallAssessment: diagnosisData.inquiry.overallAssessment || '',
          confidence: diagnosisData.inquiry.confidence || 0,
          rawData: diagnosisData.inquiry
        });
      }
      
      if (diagnosisData.touch) {
        savedAnalysis.touch = await this.repository.saveDiagnosisAnalysis({
          diagnosisType: DiagnosisType.TOUCH,
          timestamp: diagnosisData.timestamp,
          findings: diagnosisData.touch.findings || [],
          overallAssessment: diagnosisData.touch.overallAssessment || '',
          confidence: diagnosisData.touch.confidence || 0,
          rawData: diagnosisData.touch
        });
      }
      
      // 保存综合分析结果
      let savedIntegratedAssessment = null;
      if (diagnosisData.integratedAssessment) {
        // 保存阴阳平衡分析
        const yinYangAnalysis = await this.repository.saveYinYangAnalysis({
          yin: diagnosisData.integratedAssessment.bodyCondition.balance.yinYang.yin,
          yang: diagnosisData.integratedAssessment.bodyCondition.balance.yinYang.yang,
          balance: diagnosisData.integratedAssessment.bodyCondition.balance.yinYang.balance
        });
        
        // 保存五行分析
        const fiveElementsAnalysis = await this.repository.saveFiveElementsAnalysis({
          wood: diagnosisData.integratedAssessment.bodyCondition.balance.fiveElements.wood,
          fire: diagnosisData.integratedAssessment.bodyCondition.balance.fiveElements.fire,
          earth: diagnosisData.integratedAssessment.bodyCondition.balance.fiveElements.earth,
          metal: diagnosisData.integratedAssessment.bodyCondition.balance.fiveElements.metal,
          water: diagnosisData.integratedAssessment.bodyCondition.balance.fiveElements.water,
          dominantElement: diagnosisData.integratedAssessment.bodyCondition.balance.fiveElements.dominantElement,
          deficientElement: diagnosisData.integratedAssessment.bodyCondition.balance.fiveElements.deficientElement
        });
        
        // 保存脏腑分析
        const organAnalysis = await this.repository.saveOrganAnalysis({
          heart: diagnosisData.integratedAssessment.bodyCondition.balance.organs.heart,
          liver: diagnosisData.integratedAssessment.bodyCondition.balance.organs.liver,
          spleen: diagnosisData.integratedAssessment.bodyCondition.balance.organs.spleen,
          lung: diagnosisData.integratedAssessment.bodyCondition.balance.organs.lung,
          kidney: diagnosisData.integratedAssessment.bodyCondition.balance.organs.kidney,
          stomach: diagnosisData.integratedAssessment.bodyCondition.balance.organs.stomach,
          gallbladder: diagnosisData.integratedAssessment.bodyCondition.balance.organs.gallbladder,
          anomalies: diagnosisData.integratedAssessment.bodyCondition.balance.organs.anomalies || []
        });
        
        // 保存身体状况分析
        const bodyCondition = await this.repository.saveBodyConditionAnalysis({
          yinYang: yinYangAnalysis._id,
          fiveElements: fiveElementsAnalysis._id,
          organs: organAnalysis._id,
          energyLevel: diagnosisData.integratedAssessment.bodyCondition.energyLevel,
          constitutionType: diagnosisData.integratedAssessment.bodyCondition.constitutionType
        });
        
        // 保存综合分析
        savedIntegratedAssessment = await this.repository.saveIntegratedAssessment({
          timestamp: diagnosisData.integratedAssessment.timestamp,
          summary: diagnosisData.integratedAssessment.summary,
          bodyCondition: bodyCondition._id,
          healthSuggestions: diagnosisData.integratedAssessment.healthSuggestions || [],
          diagnosticConfidence: diagnosisData.integratedAssessment.diagnosticConfidence
        });
      }
      
      // 保存四诊合参数据
      await this.repository.saveFourDiagnosisData({
        patientId: diagnosisData.patientId,
        diagnosisId: diagnosisData.diagnosisId,
        timestamp: diagnosisData.timestamp,
        looking: savedAnalysis.looking?._id,
        smell: savedAnalysis.smell?._id,
        inquiry: savedAnalysis.inquiry?._id,
        touch: savedAnalysis.touch?._id,
        integratedAssessment: savedIntegratedAssessment?._id
      });
      
      logger.info(`诊断结果保存成功: ${diagnosisData.patientId}`);
    } catch (error) {
      logger.error(`保存诊断结果失败: ${diagnosisData.patientId}`, { error });
      throw new AppError('保存诊断结果失败', 500);
    }
  }
  
  /**
   * 获取患者诊断历史记录
   */
  async getPatientDiagnosisHistory(
    patientId: string,
    startDate?: string,
    endDate?: string,
    limit: number = 10,
    offset: number = 0
  ): Promise<any> {
    logger.info(`获取患者诊断历史记录: ${patientId}`, { startDate, endDate, limit, offset });
    
    try {
      // 从数据库获取历史数据
      const historyData = await this.repository.getPatientDiagnosisHistory(
        patientId,
        startDate,
        endDate,
        limit,
        offset
      );
      
      return historyData;
    } catch (error) {
      logger.error(`获取患者诊断历史记录失败: ${patientId}`, { error });
      throw new AppError('获取患者诊断历史记录失败', 500);
    }
  }
  
  /**
   * 根据ID获取四诊合参数据
   */
  async getFourDiagnosisById(diagnosisId: string): Promise<any> {
    logger.info(`根据ID获取四诊合参数据: ${diagnosisId}`);
    
    try {
      // 从数据库获取数据
      const diagnosisData = await this.repository.getFourDiagnosisById(diagnosisId);
      
      if (!diagnosisData) {
        throw new AppError('未找到指定的诊断记录', 404);
      }
      
      return diagnosisData;
    } catch (error) {
      logger.error(`根据ID获取四诊合参数据失败: ${diagnosisId}`, { error });
      if (error instanceof AppError) {
        throw error;
      }
      throw new AppError('获取诊断记录失败', 500);
    }
  }
  
  /**
   * 处理四诊合参分析请求
   */
  async processPatientDiagnosisRequest(request: FourDiagnosisCoordinatorRequest): Promise<any> {
    logger.info('处理四诊合参分析请求', { patientId: request.patientId });
    
    try {
      // 步骤1: 验证并收集四诊数据
      const diagnosticData = await this.collectDiagnosticData(request);
      
      // 步骤2: 验证数据完整性和一致性
      this.validateDiagnosticIntegrity(diagnosticData, request.patientId);
      
      // 步骤3: 解决诊断冲突（如果有）
      const resolvedData = await this.resolveDiagnosticConflicts(diagnosticData, request.patientId);
      
      // 步骤4: 使用分析引擎执行四诊合参分析
      const integratedAssessment = this.analysisEngine.performIntegratedAnalysis(resolvedData);
      
      // 步骤5: 根据分析结果生成健康建议（可选）
      if (request.includeHealthSuggestions) {
        integratedAssessment.healthSuggestions = await this.healthRecommendationService
          .generateHealthSuggestions(integratedAssessment, request.patientId);
      }
      
      // 步骤6: 保存四诊合参结果到数据库
      const savedDiagnosis = await this.saveDiagnosisResult(resolvedData, integratedAssessment, request.patientId);
      
      // 步骤7: 构建和返回响应
      return this.buildDiagnosisResponse(savedDiagnosis, request);
      
    } catch (error) {
      logger.error('四诊合参分析失败', { 
        patientId: request.patientId, 
        error: error instanceof Error ? error.message : String(error)
      });
      
      // 重新抛出AppError类型的错误
      if (error instanceof AppError) {
        throw error;
      }
      
      // 将其他类型的错误转换为AppError
      throw new AppError(
        error instanceof Error ? error.message : '四诊合参分析失败',
        ErrorType.ANALYSIS_ERROR,
        500,
        true,
        error,
        'coordinator-service',
        undefined,
        request.patientId
      );
    }
  }
  
  /**
   * 收集来自各个服务的四诊数据
   */
  private async collectDiagnosticData(request: FourDiagnosisCoordinatorRequest): Promise<any> {
    logger.debug('收集四诊数据', { patientId: request.patientId });
    
    const diagnosticData = {
      patientId: request.patientId,
      looking: null,
      smell: null,
      inquiry: null,
      touch: null
    };
    
    // 并行获取各诊断数据以提高性能
    const [lookingData, smellData, inquiryData, touchData] = await Promise.all([
      request.lookingDiagnosisId ? 
        this.lookingService.getDiagnosisById(request.lookingDiagnosisId).catch(err => {
          logger.warn('获取望诊数据失败', { error: err, patientId: request.patientId });
          return null;
        }) : null,
      
      request.smellDiagnosisId ? 
        this.smellService.getDiagnosisById(request.smellDiagnosisId).catch(err => {
          logger.warn('获取闻诊数据失败', { error: err, patientId: request.patientId });
          return null;
        }) : null,
      
      request.inquiryDiagnosisId ? 
        this.inquiryService.getDiagnosisById(request.inquiryDiagnosisId).catch(err => {
          logger.warn('获取问诊数据失败', { error: err, patientId: request.patientId });
          return null;
        }) : null,
      
      request.touchDiagnosisId ? 
        this.touchService.getDiagnosisById(request.touchDiagnosisId).catch(err => {
          logger.warn('获取切诊数据失败', { error: err, patientId: request.patientId });
          return null;
        }) : null
    ]);
    
    // 设置收集到的数据
    if (lookingData) diagnosticData.looking = lookingData;
    if (smellData) diagnosticData.smell = smellData;
    if (inquiryData) diagnosticData.inquiry = inquiryData;
    if (touchData) diagnosticData.touch = touchData;
    
    return diagnosticData;
  }
  
  /**
   * 验证诊断数据的完整性和一致性
   */
  private validateDiagnosticIntegrity(data: any, patientId: string): void {
    logger.debug('验证诊断数据完整性', { patientId });
    
    // 检查是否至少有一种诊断数据
    const hasDiagnosticData = data.looking || data.smell || data.inquiry || data.touch;
    
    if (!hasDiagnosticData) {
      throw AppError.insufficientDataError(
        '未提供任何诊断数据，无法执行分析',
        [],
        patientId
      );
    }
    
    // 记录可用的诊断方法
    const availableDiagnoses = [];
    if (data.looking) availableDiagnoses.push(DiagnosisType.LOOKING);
    if (data.smell) availableDiagnoses.push(DiagnosisType.SMELL);
    if (data.inquiry) availableDiagnoses.push(DiagnosisType.INQUIRY);
    if (data.touch) availableDiagnoses.push(DiagnosisType.TOUCH);
    
    logger.info(`可用诊断数据: ${availableDiagnoses.join(', ')}`, { patientId });
    
    // 如果只有一种诊断数据，给出警告（但仍然继续处理）
    if (availableDiagnoses.length === 1) {
      logger.warn(`只有一种诊断数据可用，分析可能不全面: ${availableDiagnoses[0]}`, { patientId });
    }
    
    // 检查各个诊断数据的有效性
    if (data.looking && (!data.looking.rawData || !data.looking.overallAssessment)) {
      logger.warn('望诊数据不完整', { patientId });
    }
    
    if (data.smell && (!data.smell.rawData || !data.smell.overallAssessment)) {
      logger.warn('闻诊数据不完整', { patientId });
    }
    
    if (data.inquiry && (!data.inquiry.rawData || !data.inquiry.overallAssessment)) {
      logger.warn('问诊数据不完整', { patientId });
    }
    
    if (data.touch && (!data.touch.rawData || !data.touch.overallAssessment)) {
      logger.warn('切诊数据不完整', { patientId });
    }
    
    // 检查诊断数据的时间一致性
    this.checkTimeConsistency(data, patientId);
  }
  
  /**
   * 检查诊断数据的时间一致性
   */
  private checkTimeConsistency(data: any, patientId: string): void {
    const timestamps = [];
    
    if (data.looking && data.looking.timestamp) {
      timestamps.push({
        type: DiagnosisType.LOOKING,
        time: new Date(data.looking.timestamp)
      });
    }
    
    if (data.smell && data.smell.timestamp) {
      timestamps.push({
        type: DiagnosisType.SMELL,
        time: new Date(data.smell.timestamp)
      });
    }
    
    if (data.inquiry && data.inquiry.timestamp) {
      timestamps.push({
        type: DiagnosisType.INQUIRY,
        time: new Date(data.inquiry.timestamp)
      });
    }
    
    if (data.touch && data.touch.timestamp) {
      timestamps.push({
        type: DiagnosisType.TOUCH,
        time: new Date(data.touch.timestamp)
      });
    }
    
    // 如果有多个时间戳，计算最大时间差
    if (timestamps.length > 1) {
      // 按时间排序
      timestamps.sort((a, b) => a.time.getTime() - b.time.getTime());
      
      // 计算最早和最晚时间戳之间的时间差（小时）
      const earliestTime = timestamps[0].time;
      const latestTime = timestamps[timestamps.length - 1].time;
      const timeDifferenceHours = (latestTime.getTime() - earliestTime.getTime()) / (1000 * 60 * 60);
      
      // 如果时间差超过24小时，记录警告
      if (timeDifferenceHours > 24) {
        logger.warn(`诊断数据时间差异较大: ${timeDifferenceHours.toFixed(1)}小时`, {
          patientId,
          earliestDiagnosis: timestamps[0].type,
          latestDiagnosis: timestamps[timestamps.length - 1].type,
          earliestTime: earliestTime.toISOString(),
          latestTime: latestTime.toISOString()
        });
      }
    }
  }
  
  /**
   * 解决诊断数据中的冲突
   */
  private async resolveDiagnosticConflicts(data: any, patientId: string): Promise<any> {
    logger.debug('解决诊断冲突', { patientId });
    
    // 深拷贝原始数据，避免修改原始数据
    const resolvedData = JSON.parse(JSON.stringify(data));
    
    // 检测是否存在冲突
    const conflicts = this.detectDiagnosticConflicts(data);
    
    // 如果没有冲突，直接返回原始数据
    if (conflicts.length === 0) {
      return resolvedData;
    }
    
    // 记录检测到的冲突
    logger.info(`检测到${conflicts.length}个诊断冲突`, { 
      patientId, 
      conflicts: conflicts.map(c => c.description) 
    });
    
    // 针对每个冲突应用解决策略
    for (const conflict of conflicts) {
      await this.applyConflictResolutionStrategy(resolvedData, conflict, patientId);
    }
    
    // 如果冲突无法自动解决，抛出错误
    const unresolvedConflicts = conflicts.filter(c => !c.resolved);
    if (unresolvedConflicts.length > 0) {
      logger.warn(`${unresolvedConflicts.length}个冲突无法自动解决`, {
        patientId,
        unresolvedConflicts: unresolvedConflicts.map(c => c.description)
      });
      
      // 转换为警告并继续处理，而不是抛出错误
      // 在实际应用中，可能需要更复杂的策略来处理无法解决的冲突
    }
    
    return resolvedData;
  }
  
  /**
   * 检测诊断数据中的冲突
   */
  private detectDiagnosticConflicts(data: any): Array<{
    type: string;
    description: string;
    affectedDiagnoses: DiagnosisType[];
    severity: 'high' | 'medium' | 'low';
    resolved: boolean;
    resolutionStrategy?: string;
  }> {
    const conflicts = [];
    
    // 示例冲突检测：寒热冲突
    // 在实际应用中，应该实现更复杂的冲突检测逻辑
    
    // 热性关键词
    const hotTerms = ['阳盛', '热', '火', '燥'];
    
    // 寒性关键词
    const coldTerms = ['阴盛', '寒', '凉', '湿'];
    
    // 记录含有热性和寒性关键词的诊断
    const hotDiagnoses = [];
    const coldDiagnoses = [];
    
    // 检查望诊结果
    if (data.looking && data.looking.overallAssessment) {
      const assessment = data.looking.overallAssessment;
      
      if (hotTerms.some(term => assessment.includes(term))) {
        hotDiagnoses.push(DiagnosisType.LOOKING);
      }
      
      if (coldTerms.some(term => assessment.includes(term))) {
        coldDiagnoses.push(DiagnosisType.LOOKING);
      }
    }
    
    // 检查闻诊结果
    if (data.smell && data.smell.overallAssessment) {
      const assessment = data.smell.overallAssessment;
      
      if (hotTerms.some(term => assessment.includes(term))) {
        hotDiagnoses.push(DiagnosisType.SMELL);
      }
      
      if (coldTerms.some(term => assessment.includes(term))) {
        coldDiagnoses.push(DiagnosisType.SMELL);
      }
    }
    
    // 检查问诊结果
    if (data.inquiry && data.inquiry.overallAssessment) {
      const assessment = data.inquiry.overallAssessment;
      
      if (hotTerms.some(term => assessment.includes(term))) {
        hotDiagnoses.push(DiagnosisType.INQUIRY);
      }
      
      if (coldTerms.some(term => assessment.includes(term))) {
        coldDiagnoses.push(DiagnosisType.INQUIRY);
      }
    }
    
    // 检查切诊结果
    if (data.touch && data.touch.overallAssessment) {
      const assessment = data.touch.overallAssessment;
      
      if (hotTerms.some(term => assessment.includes(term))) {
        hotDiagnoses.push(DiagnosisType.TOUCH);
      }
      
      if (coldTerms.some(term => assessment.includes(term))) {
        coldDiagnoses.push(DiagnosisType.TOUCH);
      }
    }
    
    // 如果同时存在热性和寒性特征，记录冲突
    if (hotDiagnoses.length > 0 && coldDiagnoses.length > 0) {
      conflicts.push({
        type: '寒热冲突',
        description: `诊断中同时存在寒性特征(${coldDiagnoses.join(',')})和热性特征(${hotDiagnoses.join(',')})`,
        affectedDiagnoses: [...new Set([...hotDiagnoses, ...coldDiagnoses])],
        severity: 'medium',
        resolved: false,
        resolutionStrategy: '根据诊断权重确定主导特征'
      });
    }
    
    // 更多冲突检测逻辑...
    
    return conflicts;
  }
  
  /**
   * 应用冲突解决策略
   */
  private async applyConflictResolutionStrategy(
    data: any, 
    conflict: {
      type: string;
      description: string;
      affectedDiagnoses: DiagnosisType[];
      severity: 'high' | 'medium' | 'low';
      resolved: boolean;
      resolutionStrategy?: string;
    },
    patientId: string
  ): Promise<void> {
    logger.debug(`应用冲突解决策略: ${conflict.type}`, { patientId });
    
    // 根据冲突类型应用不同的解决策略
    switch (conflict.type) {
      case '寒热冲突':
        this.resolveHotColdConflict(data, conflict);
        break;
        
      // 更多冲突类型...
      
      default:
        logger.warn(`未知的冲突类型: ${conflict.type}，无法应用解决策略`, { patientId });
        break;
    }
  }
  
  /**
   * 解决寒热冲突
   */
  private resolveHotColdConflict(data: any, conflict: any): void {
    // 诊断方法的权重
    const diagnosticWeights = {
      [DiagnosisType.LOOKING]: 0.3,
      [DiagnosisType.SMELL]: 0.2,
      [DiagnosisType.INQUIRY]: 0.3,
      [DiagnosisType.TOUCH]: 0.2
    };
    
    // 热性关键词
    const hotTerms = ['阳盛', '热', '火', '燥'];
    
    // 寒性关键词
    const coldTerms = ['阴盛', '寒', '凉', '湿'];
    
    // 计算热性和寒性特征的权重总和
    let hotWeight = 0;
    let coldWeight = 0;
    
    // 检查各诊断类型
    Object.entries(data).forEach(([key, value]) => {
      if (key === 'patientId') return;
      
      if (value && value.overallAssessment) {
        const assessment = value.overallAssessment;
        const diagnosisType = key as DiagnosisType;
        const weight = diagnosticWeights[diagnosisType] || 0;
        
        // 检查是否包含热性关键词
        if (hotTerms.some(term => assessment.includes(term))) {
          hotWeight += weight;
        }
        
        // 检查是否包含寒性关键词
        if (coldTerms.some(term => assessment.includes(term))) {
          coldWeight += weight;
        }
      }
    });
    
    // 根据权重确定主导特征
    let dominantFeature: 'hot' | 'cold' | 'mixed' = 'mixed';
    
    if (hotWeight > coldWeight * 1.5) {
      dominantFeature = 'hot';
    } else if (coldWeight > hotWeight * 1.5) {
      dominantFeature = 'cold';
    }
    
    // 根据主导特征调整各诊断的描述
    if (dominantFeature !== 'mixed') {
      // 在实际应用中，这里应该实现更复杂的调整逻辑
      // 例如，重新生成或修改与主导特征不一致的诊断描述
      
      logger.info(`解决寒热冲突，主导特征: ${dominantFeature}`, {
        hotWeight,
        coldWeight,
        affectedDiagnoses: conflict.affectedDiagnoses
      });
      
      // 标记冲突已解决
      conflict.resolved = true;
    } else {
      // 如果无法确定主导特征，保留原始诊断，但添加备注
      logger.info('无法确定寒热冲突的主导特征，保留原始诊断', {
        hotWeight,
        coldWeight,
        affectedDiagnoses: conflict.affectedDiagnoses
      });
      
      // 添加备注到每个受影响的诊断
      conflict.affectedDiagnoses.forEach(diagnosisType => {
        if (data[diagnosisType]) {
          const originalAssessment = data[diagnosisType].overallAssessment;
          data[diagnosisType].overallAssessment = 
            `${originalAssessment}\n【注意】此诊断与其他诊断存在寒热冲突，结果可能不完全准确。`;
        }
      });
      
      // 标记冲突已解决（采用了保留原始诊断并添加备注的策略）
      conflict.resolved = true;
    }
  }
  
  /**
   * 保存诊断结果到数据库
   */
  private async saveDiagnosisResult(rawData: any, integratedAssessment: any, patientId: string): Promise<any> {
    logger.debug('保存诊断结果', { patientId });
    
    try {
      // 创建新的诊断记录
      const diagnosis = new Diagnosis({
        patientId,
        timestamp: new Date(),
        looking: rawData.looking ? {
          data: rawData.looking.rawData,
          timestamp: rawData.looking.timestamp,
          overallAssessment: rawData.looking.overallAssessment
        } : undefined,
        smell: rawData.smell ? {
          data: rawData.smell.rawData,
          timestamp: rawData.smell.timestamp,
          overallAssessment: rawData.smell.overallAssessment
        } : undefined,
        inquiry: rawData.inquiry ? {
          data: rawData.inquiry.rawData,
          timestamp: rawData.inquiry.timestamp,
          overallAssessment: rawData.inquiry.overallAssessment
        } : undefined,
        touch: rawData.touch ? {
          data: rawData.touch.rawData,
          timestamp: rawData.touch.timestamp,
          overallAssessment: rawData.touch.overallAssessment
        } : undefined,
        integrated: {
          timestamp: integratedAssessment.timestamp,
          summary: integratedAssessment.summary,
          bodyCondition: integratedAssessment.bodyCondition,
          healthSuggestions: integratedAssessment.healthSuggestions,
          diagnosticConfidence: integratedAssessment.diagnosticConfidence,
          usedDiagnostics: integratedAssessment.usedDiagnostics
        },
        meta: {
          createdAt: new Date(),
          updatedAt: new Date(),
          version: 1,
          source: 'system',
          integrationStatus: 'completed'
        }
      });
      
      // 保存诊断记录
      const savedDiagnosis = await diagnosis.save();
      
      logger.info('诊断结果保存成功', { 
        patientId, 
        diagnosisId: savedDiagnosis._id 
      });
      
      return savedDiagnosis;
    } catch (error) {
      logger.error('保存诊断结果失败', { patientId, error });
      
      throw new AppError(
        '保存诊断结果失败',
        ErrorType.DATABASE_ERROR,
        500,
        true,
        error,
        'database',
        undefined,
        patientId
      );
    }
  }
  
  /**
   * 构建诊断响应
   */
  private buildDiagnosisResponse(diagnosis: any, request: FourDiagnosisCoordinatorRequest): any {
    // 获取患者的历史诊断记录，用于比较变化
    const constitutionHistory = [];
    
    // 构建响应对象
    const response = {
      patientId: diagnosis.patientId,
      assessmentId: diagnosis._id,
      timestamp: diagnosis.timestamp,
      integratedAssessment: diagnosis.integrated,
      diagnosisConfidence: diagnosis.integrated.diagnosticConfidence
    };
    
    // 如果请求包含历史数据
    if (request.includeHistoricalData) {
      response['constitutionHistory'] = constitutionHistory;
    }
    
    // 如果请求包含原始数据
    if (request.includeRawData) {
      response['rawData'] = {
        looking: diagnosis.looking,
        smell: diagnosis.smell,
        inquiry: diagnosis.inquiry,
        touch: diagnosis.touch
      };
    }
    
    return response;
  }
  
  /**
   * 获取患者的历史诊断记录
   */
  async getPatientDiagnosisHistory(patientId: string, limit: number = 10): Promise<any[]> {
    logger.debug('获取患者历史诊断记录', { patientId, limit });
    
    try {
      // 查询患者的历史诊断记录
      const diagnosticRecords = await Diagnosis.find({ patientId })
        .sort({ timestamp: -1 })
        .limit(limit)
        .select('patientId timestamp integrated.bodyCondition.constitutionType meta.diagnosisQualityScore')
        .lean();
      
      logger.info(`找到${diagnosticRecords.length}条历史诊断记录`, { patientId });
      
      return diagnosticRecords;
    } catch (error) {
      logger.error('获取患者历史诊断记录失败', { patientId, error });
      
      throw new AppError(
        '获取患者历史诊断记录失败',
        ErrorType.DATABASE_ERROR,
        500,
        true,
        error,
        'database',
        undefined,
        patientId
      );
    }
  }
  
  /**
   * 处理边缘情况：数据质量不佳
   */
  private handlePoorDataQuality(data: any, patientId: string): any {
    logger.debug('处理数据质量不佳的情况', { patientId });
    
    // 深拷贝原始数据
    const enhancedData = JSON.parse(JSON.stringify(data));
    
    // 记录原始数据质量问题
    const qualityIssues = [];
    
    // 检查各诊断数据的完整性
    if (enhancedData.looking && (!enhancedData.looking.rawData || Object.keys(enhancedData.looking.rawData).length < 3)) {
      qualityIssues.push('望诊数据不完整');
    }
    
    if (enhancedData.smell && (!enhancedData.smell.rawData || Object.keys(enhancedData.smell.rawData).length < 2)) {
      qualityIssues.push('闻诊数据不完整');
    }
    
    if (enhancedData.inquiry && (!enhancedData.inquiry.rawData || Object.keys(enhancedData.inquiry.rawData).length < 4)) {
      qualityIssues.push('问诊数据不完整');
    }
    
    if (enhancedData.touch && (!enhancedData.touch.rawData || Object.keys(enhancedData.touch.rawData).length < 3)) {
      qualityIssues.push('切诊数据不完整');
    }
    
    // 如果存在质量问题，添加相应备注
    if (qualityIssues.length > 0) {
      logger.warn(`检测到数据质量问题: ${qualityIssues.join(', ')}`, { patientId });
      
      // 添加备注到诊断数据中
      Object.keys(enhancedData).forEach(key => {
        if (key !== 'patientId' && enhancedData[key]) {
          const originalAssessment = enhancedData[key].overallAssessment || '';
          enhancedData[key].overallAssessment = 
            `${originalAssessment}\n【注意】数据质量不佳，结果可能不完全准确。`;
        }
      });
    }
    
    return enhancedData;
  }
  
  /**
   * 健康检查接口
   */
  async healthCheck(): Promise<{ status: string, version: string }> {
    return {
      status: 'healthy',
      version: '1.0.0'
    };
  }
}

// 导出默认实例
export default new FourDiagnosisCoordinatorService(); 