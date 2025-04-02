import axios from 'axios';
import config from 'config';
import { IWearableData } from '../models/wearable-data.model';
import logger from '../utils/logger';

const USER_SERVICE_URL = config.get<string>('services.userService.url');
const XIAOAI_SERVICE_URL = config.get<string>('services.xiaoaiService.url');

/**
 * 可穿戴设备数据集成服务
 * 负责处理可穿戴设备数据与用户服务的集成和数据分析结果的处理
 */
export class WearableDataIntegrationService {
  /**
   * 将可穿戴设备数据同步到用户健康画像
   * @param wearableData 可穿戴设备数据
   */
  async syncToUserHealthProfile(wearableData: IWearableData): Promise<void> {
    try {
      const healthData = this.mapWearableDataToHealthProfile(wearableData);
      await axios.post(`${USER_SERVICE_URL}/api/users/${wearableData.userId}/health-profile/wearable-data`, healthData);
      logger.info(`Successfully synced wearable data for user ${wearableData.userId} to health profile`);
    } catch (error) {
      logger.error(`Failed to sync wearable data for user ${wearableData.userId} to health profile:`, error);
      throw error;
    }
  }

  /**
   * 将异常数据发送给小艾进行分析和用户通知
   * @param wearableData 可穿戴设备数据
   * @param anomalies 检测到的异常
   */
  async notifyAnomalies(wearableData: IWearableData, anomalies: any[]): Promise<void> {
    if (!anomalies || anomalies.length === 0) return;

    try {
      await axios.post(`${XIAOAI_SERVICE_URL}/api/notifications/health-anomalies`, {
        userId: wearableData.userId,
        deviceType: wearableData.deviceType,
        dataType: wearableData.dataType,
        anomalies,
        detectedAt: new Date().toISOString(),
        severity: this.calculateOverallSeverity(anomalies)
      });
      logger.info(`Successfully sent anomaly notification for user ${wearableData.userId}`);
    } catch (error) {
      logger.error(`Failed to send anomaly notification for user ${wearableData.userId}:`, error);
      throw error;
    }
  }

  /**
   * 获取用户上一次设备数据的时间戳
   * @param userId 用户ID
   * @param deviceType 设备类型
   * @param dataType 数据类型
   */
  async getLastSyncTimestamp(userId: string, deviceType: string, dataType: string): Promise<Date | null> {
    try {
      const response = await axios.get(
        `${USER_SERVICE_URL}/api/users/${userId}/health-profile/last-sync`, 
        { params: { deviceType, dataType } }
      );
      
      if (response.data && response.data.lastSyncTime) {
        return new Date(response.data.lastSyncTime);
      }
      return null;
    } catch (error) {
      logger.error(`Failed to get last sync timestamp for user ${userId}:`, error);
      return null;
    }
  }

  /**
   * 将设备数据转换为多设备关联分析结果，并保存
   * @param userId 用户ID
   * @param correlationResults 关联分析结果
   */
  async saveDataCorrelations(userId: string, correlationResults: any[]): Promise<void> {
    try {
      await axios.post(
        `${USER_SERVICE_URL}/api/users/${userId}/health-profile/correlations`, 
        { correlations: correlationResults }
      );
      logger.info(`Successfully saved data correlations for user ${userId}`);
    } catch (error) {
      logger.error(`Failed to save data correlations for user ${userId}:`, error);
      throw error;
    }
  }

  /**
   * 将可穿戴设备数据映射到健康画像格式
   * @param wearableData 可穿戴设备数据
   */
  private mapWearableDataToHealthProfile(wearableData: IWearableData): any {
    // 获取最新的测量值
    const latestMeasurements = wearableData.measurements
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, 10);
    
    // 提取健康评分
    const healthScore = wearableData.analysisResults.healthScore || null;
    
    // 提取趋势信息
    const trends = wearableData.analysisResults.trends.map(trend => ({
      type: trend.type,
      description: trend.description,
      severity: trend.severity,
      period: {
        start: trend.startDate.toISOString(),
        end: trend.endDate.toISOString()
      }
    }));
    
    // 返回格式化后的健康画像数据
    return {
      deviceType: wearableData.deviceType,
      deviceId: wearableData.deviceId,
      dataType: wearableData.dataType,
      latestMeasurements,
      healthScore,
      trends,
      anomalies: wearableData.analysisResults.anomalies,
      recommendations: wearableData.analysisResults.recommendations,
      lastSyncTime: wearableData.lastSyncTime.toISOString()
    };
  }

  /**
   * 计算异常数据的整体严重性
   * @param anomalies 异常数据列表
   */
  private calculateOverallSeverity(anomalies: any[]): 'low' | 'medium' | 'high' {
    if (!anomalies || anomalies.length === 0) return 'low';
    
    // 计算严重程度分布
    const severityCounts = {
      low: 0,
      medium: 0,
      high: 0
    };
    
    anomalies.forEach(anomaly => {
      severityCounts[anomaly.severity]++;
    });
    
    // 如果有任何高严重性异常，整体评为高
    if (severityCounts.high > 0) return 'high';
    
    // 如果中等严重性异常超过一定数量或比例，整体评为中
    if (severityCounts.medium > 0 || 
       (severityCounts.medium / anomalies.length) > 0.3) {
      return 'medium';
    }
    
    // 其余情况评为低
    return 'low';
  }
}

export default new WearableDataIntegrationService();