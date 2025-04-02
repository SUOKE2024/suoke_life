import { Service } from 'typedi';
import axios from 'axios';
import { logger } from '../utils/logger';
import { IntegrationServiceException } from '../exceptions';

/**
 * 健康画像服务
 * 负责与健康画像微服务进行交互，获取和更新用户健康画像数据
 */
@Service()
export class HealthProfileService {
  private apiUrl: string;
  
  constructor() {
    this.apiUrl = process.env.HEALTH_PROFILE_SERVICE_URL || 'http://health-profile-service:3004/api/v1';
  }
  
  /**
   * 获取用户健康画像
   * @param userId 用户ID
   * @returns 用户健康画像数据
   */
  async getUserHealthProfile(userId: string): Promise<any> {
    try {
      const response = await axios.get(`${this.apiUrl}/users/${userId}/profile`);
      return response.data.data;
    } catch (error) {
      logger.error(`获取用户健康画像失败: ${error.message}`, { 
        userId, 
        service: 'health-profile-service',
        error: error.toString()
      });
      if (error.response && error.response.status === 404) {
        return null;
      }
      throw new IntegrationServiceException('健康画像服务', error.message);
    }
  }
  
  /**
   * 更新用户健康画像
   * @param userId 用户ID
   * @param profileData 健康画像数据
   * @returns 操作是否成功
   */
  async updateUserHealthProfile(userId: string, profileData: any): Promise<boolean> {
    try {
      await axios.patch(`${this.apiUrl}/users/${userId}/profile`, profileData);
      return true;
    } catch (error) {
      logger.error(`更新用户健康画像失败: ${error.message}`, {
        userId,
        service: 'health-profile-service',
        error: error.toString()
      });
      throw new IntegrationServiceException('健康画像服务', error.message);
    }
  }
  
  /**
   * 添加诊断结果到健康画像
   * @param userId 用户ID
   * @param diagnosisId 诊断ID
   * @param diagnosisData 诊断数据
   * @returns 操作是否成功
   */
  async addDiagnosisToHealthProfile(userId: string, diagnosisId: string, diagnosisData: any): Promise<boolean> {
    try {
      await axios.post(`${this.apiUrl}/users/${userId}/diagnoses`, {
        diagnosisId,
        diagnosisData,
        source: 'inquiry-diagnosis-service',
        timestamp: new Date().toISOString()
      });
      return true;
    } catch (error) {
      logger.error(`添加诊断到健康画像失败: ${error.message}`, {
        userId,
        diagnosisId,
        service: 'health-profile-service',
        error: error.toString()
      });
      throw new IntegrationServiceException('健康画像服务', error.message);
    }
  }

  /**
   * 检索用户历史诊断记录
   * @param userId 用户ID
   * @param limit 限制返回数量
   * @param offset 偏移量
   * @returns 历史诊断记录
   */
  async getUserDiagnosisHistory(userId: string, limit = 5, offset = 0): Promise<any[]> {
    try {
      const response = await axios.get(`${this.apiUrl}/users/${userId}/diagnoses`, {
        params: { limit, offset }
      });
      return response.data.data;
    } catch (error) {
      logger.error(`获取用户历史诊断记录失败: ${error.message}`, {
        userId,
        service: 'health-profile-service',
        error: error.toString()
      });
      if (error.response && error.response.status === 404) {
        return [];
      }
      throw new IntegrationServiceException('健康画像服务', error.message);
    }
  }

  /**
   * 获取用户体质信息
   * @param userId 用户ID
   * @returns 用户体质信息
   */
  async getUserConstitution(userId: string): Promise<any> {
    try {
      const response = await axios.get(`${this.apiUrl}/users/${userId}/constitution`);
      return response.data.data;
    } catch (error) {
      logger.error(`获取用户体质信息失败: ${error.message}`, {
        userId,
        service: 'health-profile-service',
        error: error.toString()
      });
      if (error.response && error.response.status === 404) {
        return null;
      }
      throw new IntegrationServiceException('健康画像服务', error.message);
    }
  }

  /**
   * 记录用户症状
   * @param userId 用户ID
   * @param symptoms 症状数组
   * @returns 操作是否成功
   */
  async recordUserSymptoms(userId: string, symptoms: Array<{ name: string, intensity?: number, duration?: string }>): Promise<boolean> {
    try {
      await axios.post(`${this.apiUrl}/users/${userId}/symptoms`, {
        symptoms,
        source: 'inquiry-diagnosis-service',
        timestamp: new Date().toISOString()
      });
      return true;
    } catch (error) {
      logger.error(`记录用户症状失败: ${error.message}`, {
        userId,
        service: 'health-profile-service',
        error: error.toString()
      });
      throw new IntegrationServiceException('健康画像服务', error.message);
    }
  }
} 