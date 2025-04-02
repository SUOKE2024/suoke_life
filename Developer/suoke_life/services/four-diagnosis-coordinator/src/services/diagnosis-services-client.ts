import { HttpClient } from '../utils/http-client';
import { Logger } from '../utils/logger';
import { AppError } from '../middlewares/error.middleware';

const logger = new Logger('DiagnosisServicesClient');

/**
 * 望诊服务客户端
 */
export class LookingDiagnosisClient {
  private client: HttpClient;
  
  constructor() {
    const baseUrl = process.env.LOOKING_DIAGNOSIS_SERVICE_URL || 'http://localhost:3001';
    this.client = new HttpClient(baseUrl);
    logger.info(`初始化望诊服务客户端: ${baseUrl}`);
  }
  
  /**
   * 获取患者望诊数据
   */
  async getPatientData(patientId: string): Promise<any> {
    try {
      return await this.client.get<any>(`/api/looking-diagnosis/${patientId}`);
    } catch (error) {
      logger.error(`获取患者望诊数据失败: ${patientId}`, { error });
      throw new AppError('无法获取患者望诊数据', 503);
    }
  }
  
  /**
   * 获取患者望诊历史记录
   */
  async getPatientHistory(patientId: string, startDate?: string, endDate?: string): Promise<any> {
    try {
      const params: any = {};
      if (startDate) params.startDate = startDate;
      if (endDate) params.endDate = endDate;
      
      return await this.client.get<any>(`/api/looking-diagnosis/${patientId}/history`, params);
    } catch (error) {
      logger.error(`获取患者望诊历史失败: ${patientId}`, { error, startDate, endDate });
      throw new AppError('无法获取患者望诊历史', 503);
    }
  }
  
  /**
   * 请求望诊分析
   */
  async requestAnalysis(patientId: string): Promise<any> {
    try {
      return await this.client.post<any>('/api/looking-diagnosis/analyze', { patientId });
    } catch (error) {
      logger.error(`请求望诊分析失败: ${patientId}`, { error });
      throw new AppError('无法完成望诊分析', 503);
    }
  }
}

/**
 * 闻诊服务客户端
 */
export class SmellDiagnosisClient {
  private client: HttpClient;
  
  constructor() {
    const baseUrl = process.env.SMELL_DIAGNOSIS_SERVICE_URL || 'http://localhost:3005';
    this.client = new HttpClient(baseUrl);
    logger.info(`初始化闻诊服务客户端: ${baseUrl}`);
  }
  
  /**
   * 获取患者闻诊数据
   */
  async getPatientData(patientId: string): Promise<any> {
    try {
      return await this.client.get<any>(`/api/smell-diagnosis/${patientId}`);
    } catch (error) {
      logger.error(`获取患者闻诊数据失败: ${patientId}`, { error });
      throw new AppError('无法获取患者闻诊数据', 503);
    }
  }
  
  /**
   * 获取患者闻诊历史记录
   */
  async getPatientHistory(patientId: string, startDate?: string, endDate?: string): Promise<any> {
    try {
      const params: any = {};
      if (startDate) params.startDate = startDate;
      if (endDate) params.endDate = endDate;
      
      return await this.client.get<any>(`/api/smell-diagnosis/${patientId}/history`, params);
    } catch (error) {
      logger.error(`获取患者闻诊历史失败: ${patientId}`, { error, startDate, endDate });
      throw new AppError('无法获取患者闻诊历史', 503);
    }
  }
  
  /**
   * 请求闻诊分析
   */
  async requestAnalysis(patientId: string): Promise<any> {
    try {
      return await this.client.post<any>('/api/smell-diagnosis/analyze', { patientId });
    } catch (error) {
      logger.error(`请求闻诊分析失败: ${patientId}`, { error });
      throw new AppError('无法完成闻诊分析', 503);
    }
  }
}

/**
 * 问诊服务客户端
 */
export class InquiryDiagnosisClient {
  private client: HttpClient;
  
  constructor() {
    const baseUrl = process.env.INQUIRY_DIAGNOSIS_SERVICE_URL || 'http://localhost:3004';
    this.client = new HttpClient(baseUrl);
    logger.info(`初始化问诊服务客户端: ${baseUrl}`);
  }
  
  /**
   * 获取患者问诊数据
   */
  async getPatientData(patientId: string): Promise<any> {
    try {
      return await this.client.get<any>(`/api/inquiry-diagnosis/${patientId}`);
    } catch (error) {
      logger.error(`获取患者问诊数据失败: ${patientId}`, { error });
      throw new AppError('无法获取患者问诊数据', 503);
    }
  }
  
  /**
   * 获取患者问诊历史记录
   */
  async getPatientHistory(patientId: string, startDate?: string, endDate?: string): Promise<any> {
    try {
      const params: any = {};
      if (startDate) params.startDate = startDate;
      if (endDate) params.endDate = endDate;
      
      return await this.client.get<any>(`/api/inquiry-diagnosis/${patientId}/history`, params);
    } catch (error) {
      logger.error(`获取患者问诊历史失败: ${patientId}`, { error, startDate, endDate });
      throw new AppError('无法获取患者问诊历史', 503);
    }
  }
  
  /**
   * 请求问诊分析
   */
  async requestAnalysis(patientId: string): Promise<any> {
    try {
      return await this.client.post<any>('/api/inquiry-diagnosis/analyze', { patientId });
    } catch (error) {
      logger.error(`请求问诊分析失败: ${patientId}`, { error });
      throw new AppError('无法完成问诊分析', 503);
    }
  }
}

/**
 * 切诊服务客户端
 */
export class TouchDiagnosisClient {
  private client: HttpClient;
  
  constructor() {
    const baseUrl = process.env.TOUCH_DIAGNOSIS_SERVICE_URL || 'http://localhost:3003';
    this.client = new HttpClient(baseUrl);
    logger.info(`初始化切诊服务客户端: ${baseUrl}`);
  }
  
  /**
   * 获取患者切诊数据
   */
  async getPatientData(patientId: string): Promise<any> {
    try {
      return await this.client.get<any>(`/api/touch-diagnosis/${patientId}`);
    } catch (error) {
      logger.error(`获取患者切诊数据失败: ${patientId}`, { error });
      throw new AppError('无法获取患者切诊数据', 503);
    }
  }
  
  /**
   * 获取患者切诊历史记录
   */
  async getPatientHistory(patientId: string, startDate?: string, endDate?: string): Promise<any> {
    try {
      const params: any = {};
      if (startDate) params.startDate = startDate;
      if (endDate) params.endDate = endDate;
      
      return await this.client.get<any>(`/api/touch-diagnosis/${patientId}/history`, params);
    } catch (error) {
      logger.error(`获取患者切诊历史失败: ${patientId}`, { error, startDate, endDate });
      throw new AppError('无法获取患者切诊历史', 503);
    }
  }
  
  /**
   * 请求切诊分析
   */
  async requestAnalysis(patientId: string): Promise<any> {
    try {
      return await this.client.post<any>('/api/touch-diagnosis/analyze', { patientId });
    } catch (error) {
      logger.error(`请求切诊分析失败: ${patientId}`, { error });
      throw new AppError('无法完成切诊分析', 503);
    }
  }
} 