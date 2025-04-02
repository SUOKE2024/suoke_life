import { Service } from 'typedi';
import axios, { AxiosInstance } from 'axios';
import { Logger } from '../utils/logger';
import { DiagnosisResult } from '../models/diagnosis.model';
import { InquiryDiagnosis } from '../models/inquiry.model';

/**
 * 四诊协调服务客户端
 * 负责与四诊协调服务通信，上报诊断结果
 */
@Service()
export class FourDiagnosisCoordinatorService {
  private logger = new Logger('FourDiagnosisCoordinatorService');
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
        'X-Service-ID': 'inquiry-diagnosis-service'
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
   * 上报问诊诊断结果到四诊协调服务
   * @param diagnosisResult 诊断结果
   * @returns 是否上报成功
   */
  async reportDiagnosis(diagnosisResult: DiagnosisResult): Promise<boolean> {
    try {
      if (!this.apiClient.defaults.baseURL) {
        this.logger.warn('未配置四诊协调服务URL，无法上报诊断结果');
        return false;
      }
      
      this.logger.info(`上报诊断结果，诊断ID: ${diagnosisResult.diagnosisId}`);
      
      const response = await this.apiClient.post('/diagnosis/inquiry', {
        diagnosisResult,
        timestamp: new Date().toISOString(),
        serviceId: 'inquiry-diagnosis-service'
      });
      
      if (response.status === 200 || response.status === 201) {
        this.logger.info(`诊断结果上报成功，诊断ID: ${diagnosisResult.diagnosisId}`);
        return true;
      } else {
        this.logger.warn(`诊断结果上报未成功，状态码: ${response.status}`);
        return false;
      }
    } catch (error) {
      this.logger.error(`上报诊断结果失败: ${error.message}`);
      return false;
    }
  }
  
  /**
   * 上报问诊会话诊断结果到四诊协调服务
   * @param sessionId 会话ID
   * @param inquiryDiagnosis 问诊诊断结果
   * @returns 是否上报成功
   */
  async reportInquiryDiagnosis(sessionId: string, inquiryDiagnosis: InquiryDiagnosis): Promise<boolean> {
    try {
      if (!this.apiClient.defaults.baseURL) {
        this.logger.warn('未配置四诊协调服务URL，无法上报问诊结果');
        return false;
      }
      
      this.logger.info(`上报问诊诊断结果，会话ID: ${sessionId}, 诊断ID: ${inquiryDiagnosis.diagnosisId}`);
      
      const response = await this.apiClient.post('/diagnosis/inquiry-session', {
        sessionId,
        inquiryDiagnosis,
        timestamp: new Date().toISOString(),
        serviceId: 'inquiry-diagnosis-service'
      });
      
      if (response.status === 200 || response.status === 201) {
        this.logger.info(`问诊诊断结果上报成功，会话ID: ${sessionId}`);
        return true;
      } else {
        this.logger.warn(`问诊诊断结果上报未成功，状态码: ${response.status}`);
        return false;
      }
    } catch (error) {
      this.logger.error(`上报问诊诊断结果失败: ${error.message}`);
      return false;
    }
  }
  
  /**
   * 从四诊协调服务获取综合诊断结果
   * @param sessionId 会话ID
   * @returns 四诊综合结果
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