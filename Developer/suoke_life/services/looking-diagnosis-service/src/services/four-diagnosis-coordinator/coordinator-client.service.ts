import { Service } from 'typedi';
import axios, { AxiosInstance } from 'axios';
import { Logger } from '../../utils/logger';
import { TongueDiagnosisResult } from '../../models/diagnosis/tongue.model';
import { FaceDiagnosisResult } from '../face-analysis/face-analysis.service';

/**
 * 诊断结果通用接口
 */
export interface DiagnosisResultReport {
  diagnosisId: string;
  sessionId: string;
  userId?: string;
  diagnosisType: string;
  timestamp: Date;
  result: any;
  metadata?: Record<string, any>;
}

/**
 * 四诊协调服务客户端
 * 负责与四诊协调服务通信，上报诊断结果
 */
@Service()
export class CoordinatorClientService {
  private logger = new Logger('CoordinatorClientService');
  private apiClient: AxiosInstance;
  
  constructor() {
    const baseURL = process.env.FOUR_DIAGNOSIS_COORDINATOR_URL;
    
    if (!baseURL) {
      this.logger.warn('未配置四诊协调服务URL，将无法与协调服务通信');
    }
    
    this.apiClient = axios.create({
      baseURL,
      timeout: 10000, // 10秒超时
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Service-ID': 'looking-diagnosis-service'
      }
    });
    
    // 请求拦截器
    this.apiClient.interceptors.request.use(
      (config) => {
        this.logger.info(`发送请求到四诊协调服务: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        this.logger.error(`请求错误: ${error.message}`);
        return Promise.reject(error);
      }
    );
    
    // 响应拦截器
    this.apiClient.interceptors.response.use(
      (response) => {
        this.logger.info(`收到四诊协调服务响应: ${response.status}`);
        return response;
      },
      (error) => {
        if (error.response) {
          this.logger.error(`响应错误: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
        } else if (error.request) {
          this.logger.error(`请求错误: 未收到响应`);
        } else {
          this.logger.error(`错误: ${error.message}`);
        }
        return Promise.reject(error);
      }
    );
  }
  
  /**
   * 上报舌诊结果到四诊协调服务
   * @param diagnosisResult 舌诊结果
   * @returns 是否上报成功
   */
  async reportTongueDiagnosis(diagnosisResult: TongueDiagnosisResult): Promise<boolean> {
    try {
      if (!this.apiClient.defaults.baseURL) {
        this.logger.warn('未配置四诊协调服务URL，无法上报舌诊结果');
        return false;
      }
      
      this.logger.info(`上报舌诊结果，诊断ID: ${diagnosisResult.diagnosisId}`);
      
      const response = await this.apiClient.post('/diagnosis/tongue', {
        diagnosisResult,
        timestamp: new Date().toISOString(),
        serviceId: 'looking-diagnosis-service'
      });
      
      if (response.status === 200 || response.status === 201) {
        this.logger.info(`舌诊结果上报成功，诊断ID: ${diagnosisResult.diagnosisId}`);
        return true;
      } else {
        this.logger.warn(`舌诊结果上报未成功，状态码: ${response.status}`);
        return false;
      }
    } catch (error) {
      this.logger.error(`上报舌诊结果失败: ${error.message}`);
      return false;
    }
  }
  
  /**
   * 上报面诊结果到四诊协调服务
   * @param diagnosisResult 面诊结果
   * @returns 是否上报成功
   */
  async reportFaceDiagnosis(diagnosisResult: FaceDiagnosisResult): Promise<boolean> {
    try {
      if (!this.apiClient.defaults.baseURL) {
        this.logger.warn('未配置四诊协调服务URL，无法上报面诊结果');
        return false;
      }
      
      this.logger.info(`上报面诊结果，诊断ID: ${diagnosisResult.diagnosisId}`);
      
      const response = await this.apiClient.post('/diagnosis/face', {
        diagnosisResult,
        timestamp: new Date().toISOString(),
        serviceId: 'looking-diagnosis-service'
      });
      
      if (response.status === 200 || response.status === 201) {
        this.logger.info(`面诊结果上报成功，诊断ID: ${diagnosisResult.diagnosisId}`);
        return true;
      } else {
        this.logger.warn(`面诊结果上报未成功，状态码: ${response.status}`);
        return false;
      }
    } catch (error) {
      this.logger.error(`上报面诊结果失败: ${error.message}`);
      return false;
    }
  }
  
  /**
   * 上报通用诊断结果到四诊协调服务
   * @param diagnosisReport 诊断结果报告
   * @returns 是否上报成功
   */
  async reportDiagnosisResult(diagnosisReport: DiagnosisResultReport): Promise<boolean> {
    try {
      if (!this.apiClient.defaults.baseURL) {
        this.logger.warn(`未配置四诊协调服务URL，无法上报${diagnosisReport.diagnosisType}结果`);
        return false;
      }
      
      this.logger.info(`上报${diagnosisReport.diagnosisType}结果，诊断ID: ${diagnosisReport.diagnosisId}`);
      
      const response = await this.apiClient.post(`/diagnosis/${diagnosisReport.diagnosisType}`, {
        diagnosisReport,
        timestamp: new Date().toISOString(),
        serviceId: 'looking-diagnosis-service'
      });
      
      if (response.status === 200 || response.status === 201) {
        this.logger.info(`${diagnosisReport.diagnosisType}结果上报成功，诊断ID: ${diagnosisReport.diagnosisId}`);
        return true;
      } else {
        this.logger.warn(`${diagnosisReport.diagnosisType}结果上报未成功，状态码: ${response.status}`);
        return false;
      }
    } catch (error) {
      this.logger.error(`上报${diagnosisReport.diagnosisType}结果失败: ${error.message}`);
      return false;
    }
  }
  
  /**
   * 从四诊协调服务获取诊断结果
   * @param sessionId 会话ID
   * @returns 四诊结果
   */
  async getIntegratedDiagnosis(sessionId: string): Promise<any> {
    try {
      if (!this.apiClient.defaults.baseURL) {
        this.logger.warn('未配置四诊协调服务URL，无法获取综合诊断结果');
        return null;
      }
      
      this.logger.info(`获取综合诊断结果，会话ID: ${sessionId}`);
      
      const response = await this.apiClient.get(`/diagnosis/integrated/${sessionId}`);
      
      if (response.status === 200) {
        this.logger.info(`获取综合诊断结果成功，会话ID: ${sessionId}`);
        return response.data;
      } else {
        this.logger.warn(`获取综合诊断结果未成功，状态码: ${response.status}`);
        return null;
      }
    } catch (error) {
      this.logger.error(`获取综合诊断结果失败: ${error.message}`);
      return null;
    }
  }
} 