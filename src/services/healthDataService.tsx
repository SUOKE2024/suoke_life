import React from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiClient } from './apiClient';
// 健康数据类型定义
export interface HealthData {
  id: string;
  userId: string;
  type: HealthDataType;
  value: number;
  unit: string;
  timestamp: Date;
  source: 'manual' | 'device' | 'sync';
  metadata?: Record<string, any>;
}
export type HealthDataType =
  | 'heart_rate'
  | 'blood_pressure'
  | 'body_temperature'
  | 'weight'
  | 'height'
  | 'sleep_duration'
  | 'sleep_quality'
  | 'steps'
  | 'exercise_duration'
  | 'stress_level'
  | 'mood'
  | 'nutrition_score'
  | 'hydration'
  | 'blood_sugar'
  | 'blood_oxygen';
export interface HealthMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  status: 'excellent' | 'good' | 'fair' | 'poor';
  icon: string;
  color: string;
  lastUpdated: Date;
  normalRange?: {
    min: number;
  max: number;
};
}
export interface HealthGoal {
  id: string;
  userId: string;
  title: string;
  description: string;
  type: HealthDataType;
  targetValue: number;
  currentValue: number;
  unit: string;
  deadline: Date;
  progress: number;
  category: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}
export interface HealthSummary {
  overallScore: number;
  constitution: string;
  recommendations: string[];
  trends: Record<string, 'up' | 'down' | 'stable'>;
  alerts: HealthAlert[];
  lastUpdated: Date;
}
export interface HealthAlert {
  id: string;
  type: 'warning' | 'info' | 'critical';
  title: string;
  message: string;
  timestamp: Date;
  isRead: boolean;
  actionRequired: boolean;
}
export interface HealthReport {
  id: string;
  userId: string;
  title: string;
  period: {;
    start: Date;
  end: Date;
};
  summary: HealthSummary,
  data: HealthData[];
  insights: string[],
  recommendations: string[];
  generatedAt: Date,
  format: 'pdf' | 'json' | 'html';
}
// 本地存储键
const STORAGE_KEYS = {
      HEALTH_DATA: "health_data",
      HEALTH_GOALS: 'health_goals',
  HEALTH_SETTINGS: 'health_settings',
  SYNC_STATUS: 'health_sync_status',
};
class HealthDataService {
  private cache: Map<string, any> = new Map();
  private syncInProgress = false;
  // 获取健康数据
  async getHealthData()
    type?: HealthDataType,
    startDate?: Date,
    endDate?: Date,
    limit?: number;
  ): Promise<HealthData[]> {
    try {
      // 先尝试从缓存获取
      const cacheKey = `health_data_${type}_${startDate}_${endDate}_${limit}`;
      if (this.cache.has(cacheKey)) {
        return this.cache.get(cacheKey);
      }
      // 从本地存储获取
      const localData = await this.getLocalHealthData();
      let filteredData = localData;
      // 应用过滤条件
      if (type) {
        filteredData = filteredData.filter(item => item.type === type);
      }
      if (startDate) {
        filteredData = filteredData.filter(item =>)
          new Date(item.timestamp) >= startDate;
        );
      }
      if (endDate) {
        filteredData = filteredData.filter(item =>)
          new Date(item.timestamp) <= endDate;
        );
      }
      // 按时间排序
      filteredData.sort(a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );
      // 应用限制
      if (limit) {
        filteredData = filteredData.slice(0, limit);
      }
      // 缓存结果
      this.cache.set(cacheKey, filteredData);
      return filteredData;
    } catch (error) {
      console.error('Failed to get health data:', error);
      throw error;
    }
  }
  // 添加健康数据
  async addHealthData(data: Omit<HealthData, 'id' | 'timestamp'>): Promise<HealthData> {
    try {
      const newData: HealthData = {
        ...data,
        id: this.generateId(),
        timestamp: new Date(),
      };
      // 保存到本地存储
      await this.saveHealthDataLocally(newData);
      // 清除相关缓存
      this.clearCache();
      // 异步同步到服务器
      this.syncToServer(newData);
      return newData;
    } catch (error) {
      console.error('Failed to add health data:', error);
      throw error;
    }
  }
  // 批量添加健康数据
  async addHealthDataBatch(dataList: Omit<HealthData, 'id' | 'timestamp'>[]): Promise<HealthData[]> {
    try {
      const newDataList: HealthData[] = dataList.map(data => ({
        ...data,
        id: this.generateId(),
        timestamp: new Date(),
      }));
      // 批量保存到本地存储
      for (const data of newDataList) {
        await this.saveHealthDataLocally(data);
      }
      // 清除相关缓存
      this.clearCache();
      // 异步同步到服务器
      this.syncBatchToServer(newDataList);
      return newDataList;
    } catch (error) {
      console.error('Failed to add health data batch:', error);
      throw error;
    }
  }
  // 更新健康数据
  async updateHealthData(id: string, updates: Partial<HealthData>): Promise<HealthData> {
    try {
      const localData = await this.getLocalHealthData();
      const index = localData.findIndex(item => item.id === id);
      if (index === -1) {
        throw new Error('Health data not found');
      }
      const updatedData = {
        ...localData[index],
        ...updates,
        updatedAt: new Date(),
      };
      localData[index] = updatedData;
      await this.saveAllHealthData(localData);
      // 清除相关缓存
      this.clearCache();
      // 异步同步到服务器
      this.syncToServer(updatedData);
      return updatedData;
    } catch (error) {
      console.error('Failed to update health data:', error);
      throw error;
    }
  }
  // 删除健康数据
  async deleteHealthData(id: string): Promise<void> {
    try {
      const localData = await this.getLocalHealthData();
      const filteredData = localData.filter(item => item.id !== id);
            await this.saveAllHealthData(filteredData);
      // 清除相关缓存
      this.clearCache();
      // 异步同步删除到服务器
      this.syncDeleteToServer(id);
    } catch (error) {
      console.error('Failed to delete health data:', error);
      throw error;
    }
  }
  // 获取健康指标
  async getHealthMetrics(timeRange: 'day' | 'week' | 'month' | 'year'): Promise<HealthMetric[]> {
    try {
      const endDate = new Date();
      let startDate = new Date();
      // 计算时间范围
      switch (timeRange) {
        case 'day':
          startDate.setDate(endDate.getDate() - 1);
          break;
        case 'week':
          startDate.setDate(endDate.getDate() - 7);
          break;
        case 'month':
          startDate.setMonth(endDate.getMonth() - 1);
          break;
        case 'year':
          startDate.setFullYear(endDate.getFullYear() - 1);
          break;
      }
      // 获取时间范围内的数据
      const healthData = await this.getHealthData(undefined, startDate, endDate);
      // 计算指标
      const metrics = this.calculateMetrics(healthData);
      return metrics;
    } catch (error) {
      console.error('Failed to get health metrics:', error);
      throw error;
    }
  }
  // 获取健康目标
  async getHealthGoals(): Promise<HealthGoal[]> {
    try {
      const stored = await AsyncStorage.getItem(STORAGE_KEYS.HEALTH_GOALS);
      if (!stored) return [];
      const goals: HealthGoal[] = JSON.parse(stored);
            // 更新进度
      for (const goal of goals) {
        const currentData = await this.getLatestHealthData(goal.type);
        if (currentData) {
          goal.currentValue = currentData.value;
          goal.progress = Math.min(currentData.value / goal.targetValue) * 100, 100);
        }
      }
      return goals.filter(goal => goal.isActive);
    } catch (error) {
      console.error('Failed to get health goals:', error);
      return [];
    }
  }
  // 创建健康目标
  async createHealthGoal(goal: Omit<HealthGoal, 'id' | 'createdAt' | 'updatedAt' | 'progress'>): Promise<HealthGoal> {
    try {
      const newGoal: HealthGoal = {
        ...goal,
        id: this.generateId(),
        progress: 0,
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      const goals = await this.getHealthGoals();
      goals.push(newGoal);
      await AsyncStorage.setItem(STORAGE_KEYS.HEALTH_GOALS, JSON.stringify(goals));
      return newGoal;
    } catch (error) {
      console.error('Failed to create health goal:', error);
      throw error;
    }
  }
  // 更新健康目标
  async updateHealthGoal(id: string, updates: Partial<HealthGoal>): Promise<HealthGoal> {
    try {
      const goals = await this.getHealthGoals();
      const index = goals.findIndex(goal => goal.id === id);
      if (index === -1) {
        throw new Error('Health goal not found');
      }
      const updatedGoal = {
        ...goals[index],
        ...updates,
        updatedAt: new Date(),
      };
      goals[index] = updatedGoal;
      await AsyncStorage.setItem(STORAGE_KEYS.HEALTH_GOALS, JSON.stringify(goals));
      return updatedGoal;
    } catch (error) {
      console.error('Failed to update health goal:', error);
      throw error;
    }
  }
  // 生成健康报告
  async generateHealthReport()
    startDate: Date,
    endDate: Date,
    format: 'pdf' | 'json' | 'html' = 'json'
  ): Promise<HealthReport> {
    try {
      const healthData = await this.getHealthData(undefined, startDate, endDate);
      const summary = await this.generateHealthSummary(healthData);
      const insights = this.generateInsights(healthData);
      const recommendations = this.generateRecommendations(summary);
      const report: HealthReport = {,
  id: this.generateId(),
        userId: 'current_user', // 应该从认证状态获取
        title: `健康报告 ${startDate.toLocaleDateString()} - ${endDate.toLocaleDateString()}`,
        period: { start: startDate, end: endDate },
        summary,
        data: healthData,
        insights,
        recommendations,
        generatedAt: new Date(),
        format,
      };
      return report;
    } catch (error) {
      console.error('Failed to generate health report:', error);
      throw error;
    }
  }
  // 同步数据到服务器
  async syncToServer(data?: HealthData): Promise<void> {
    if (this.syncInProgress) return;
    try {
      this.syncInProgress = true;
      if (data) {
        // 同步单个数据
        await apiClient.post("HEALTH_DATA",/data', data);
      } else {
        // 同步所有未同步的数据
        const localData = await this.getLocalHealthData();
        const unsyncedData = localData.filter(item => item.source === 'manual');
                if (unsyncedData.length > 0) {
          await apiClient.post("HEALTH_DATA",/data/batch', { data: unsyncedData });
        }
      }
      // 更新同步状态
      await AsyncStorage.setItem(STORAGE_KEYS.SYNC_STATUS, JSON.stringify({
        lastSync: new Date(),
        status: 'success',
      }));
    } catch (error) {
      console.error('Failed to sync to server:', error);
      // 记录同步失败状态
      await AsyncStorage.setItem(STORAGE_KEYS.SYNC_STATUS, JSON.stringify({
        lastSync: new Date(),
        status: 'failed',
        error: error.message,
      }));
    } finally {
      this.syncInProgress = false;
    }
  }
  // 从服务器同步数据
  async syncFromServer(): Promise<void> {
    try {
      const response = await apiClient.get("HEALTH_DATA",/data/sync');
      if (response.success && response.data) {
        const serverData: HealthData[] = response.data;
                // 合并服务器数据到本地
        const localData = await this.getLocalHealthData();
        const mergedData = this.mergeHealthData(localData, serverData);
                await this.saveAllHealthData(mergedData);
        this.clearCache();
      }
    } catch (error) {
      console.error('Failed to sync from server:', error);
      throw error;
    }
  }
  // 私有方法
  private async getLocalHealthData(): Promise<HealthData[]> {
    try {
      const stored = await AsyncStorage.getItem(STORAGE_KEYS.HEALTH_DATA);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Failed to get local health data:', error);
      return [];
    }
  }
  private async saveHealthDataLocally(data: HealthData): Promise<void> {
    try {
      const localData = await this.getLocalHealthData();
      localData.unshift(data);
      await this.saveAllHealthData(localData);
    } catch (error) {
      console.error('Failed to save health data locally:', error);
      throw error;
    }
  }
  private async saveAllHealthData(data: HealthData[]): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.HEALTH_DATA, JSON.stringify(data));
    } catch (error) {
      console.error('Failed to save all health data:', error);
      throw error;
    }
  }
  private async getLatestHealthData(type: HealthDataType): Promise<HealthData | null> {
    try {
      const data = await this.getHealthData(type, undefined, undefined, 1);
      return data.length > 0 ? data[0] : null;
    } catch (error) {
      console.error('Failed to get latest health data:', error);
      return null;
    }
  }
  private calculateMetrics(healthData: HealthData[]): HealthMetric[] {
    // 这里实现指标计算逻辑
    const metrics: HealthMetric[] = [];
    // 按类型分组数据
    const groupedData = healthData.reduce(acc, item) => {
      if (!acc[item.type]) acc[item.type] = [];
      acc[item.type].push(item);
      return acc;
    }, {} as Record<string, HealthData[]>);
    // 为每种类型计算指标
    Object.entries(groupedData).forEach((([type, data]) => {
      const metric = this.calculateMetricForType(type as HealthDataType, data);
      if (metric) metrics.push(metric);
    });
    return metrics;
  }
  private calculateMetricForType(type: HealthDataType, data: HealthData[]): HealthMetric | null {
    if (data.length === 0) return null;
    const latest = data[0];
    const values = data.map(item => item.value);
    const average = values.reduce(sum, val) => sum + val, 0) / values.length;
    // 计算趋势
    let trend: 'up' | 'down' | 'stable' = 'stable';
    if (data.length >= 2) {
      const recent = values.slice(0, Math.min(3, values.length));
      const older = values.slice(Math.min(3, values.length));
            if (recent.length > 0 && older.length > 0) {
        const recentAvg = recent.reduce(sum, val) => sum + val, 0) / recent.length;
        const olderAvg = older.reduce(sum, val) => sum + val, 0) / older.length;
                if (recentAvg > olderAvg * 1.05) trend = 'up';
        else if (recentAvg < olderAvg * 0.95) trend = 'down';
      }
    }
    // 根据类型确定状态和显示信息
    const metricInfo = this.getMetricInfo(type, latest.value, average);
    return {
      id: this.generateId(),
      name: metricInfo.name,
      value: latest.value,
      unit: latest.unit,
      trend,
      status: metricInfo.status,
      icon: metricInfo.icon,
      color: metricInfo.color,
      lastUpdated: latest.timestamp,
      normalRange: metricInfo.normalRange,
    };
  }
  private getMetricInfo(type: HealthDataType, value: number, average: number) {
    // 根据健康数据类型返回相应的显示信息和状态评估
    const metricInfoMap: Record<HealthDataType, any> = {
      heart_rate: {,
  name: '心率',
        icon: 'heart-pulse',
        color: '#E91E63',
        normalRange: { min: 60, max: 100 },
        getStatus: (val: number) => {
          if (val >= 60 && val <= 100) return 'excellent';
          if (val >= 50 && val <= 110) return 'good';
          if (val >= 40 && val <= 120) return 'fair';
          return 'poor';
        }
      },
      blood_pressure: {,
  name: '血压',
        icon: 'gauge',
        color: '#4CAF50',
        normalRange: { min: 90, max: 140 },
        getStatus: (val: number) => {
          if (val >= 90 && val <= 120) return 'excellent';
          if (val >= 80 && val <= 140) return 'good';
          if (val >= 70 && val <= 160) return 'fair';
          return 'poor';
        }
      },
      sleep_quality: {,
  name: '睡眠质量',
        icon: 'sleep',
        color: '#2196F3',
        normalRange: { min: 70, max: 100 },
        getStatus: (val: number) => {
          if (val >= 85) return 'excellent';
          if (val >= 70) return 'good';
          if (val >= 50) return 'fair';
          return 'poor';
        }
      },
      steps: {,
  name: '步数',
        icon: 'walk',
        color: '#FF9800',
        normalRange: { min: 8000, max: 15000 },
        getStatus: (val: number) => {
          if (val >= 10000) return 'excellent';
          if (val >= 8000) return 'good';
          if (val >= 5000) return 'fair';
          return 'poor';
        }
      },
      // 可以继续添加其他类型...
    };
    const info = metricInfoMap[type] || {
      name: type,
      icon: 'help',
      color: '#666',
      normalRange: { min: 0, max: 100 },
      getStatus: () => 'good'
    };
    return {
      ...info,
      status: info.getStatus(value)
    };
  }
  private async generateHealthSummary(healthData: HealthData[]): Promise<HealthSummary> {
    // 实现健康总结生成逻辑
    const metrics = this.calculateMetrics(healthData);
    const overallScore = this.calculateOverallScore(metrics);
        return {
      overallScore,
      constitution: 'balanced', // 这里应该基于中医理论计算
      recommendations: this.generateBasicRecommendations(metrics),
      trends: this.calculateTrends(healthData),
      alerts: [], // 这里应该基于数据生成警告
      lastUpdated: new Date(),
    };
  }
  private calculateOverallScore(metrics: HealthMetric[]): number {
    if (metrics.length === 0) return 0;
    const statusScores = {
      excellent: 100,
      good: 80,
      fair: 60,
      poor: 40,
    };
    const totalScore = metrics.reduce(sum, metric) => {
      return sum + statusScores[metric.status];
    }, 0);
    return Math.round(totalScore / metrics.length);
  }
  private generateBasicRecommendations(metrics: HealthMetric[]): string[] {
    const recommendations: string[] = [];
    metrics.forEach(metric => {
      if (metric.status === 'poor' || metric.status === 'fair') {
        switch (metric.name) {
          case '心率':
            recommendations.push('建议进行适量的有氧运动来改善心率');
            break;
          case '睡眠质量':
            recommendations.push('建议保持规律的作息时间，改善睡眠环境');
            break;
          case '步数':
            recommendations.push('建议增加日常活动量，每天至少走8000步');
            break;
          default:
            recommendations.push(`建议关注${metric.name}的改善`);
        }
      }
    });
    return recommendations;
  }
  private calculateTrends(healthData: HealthData[]): Record<string, 'up' | 'down' | 'stable'> {
    const trends: Record<string, 'up' | 'down' | 'stable'> = {};
    // 按类型分组并计算趋势
    const groupedData = healthData.reduce(acc, item) => {
      if (!acc[item.type]) acc[item.type] = [];
      acc[item.type].push(item);
      return acc;
    }, {} as Record<string, HealthData[]>);
    Object.entries(groupedData).forEach((([type, data]) => {
      if (data.length >= 2) {
        const recent = data.slice(0, Math.min(3, data.length));
        const older = data.slice(Math.min(3, data.length));
                if (recent.length > 0 && older.length > 0) {
          const recentAvg = recent.reduce(sum, item) => sum + item.value, 0) / recent.length;
          const olderAvg = older.reduce(sum, item) => sum + item.value, 0) / older.length;
                    if (recentAvg > olderAvg * 1.05) trends[type] = 'up';
          else if (recentAvg < olderAvg * 0.95) trends[type] = 'down';
          else trends[type] = 'stable';
        } else {
          trends[type] = 'stable';
        }
      } else {
        trends[type] = 'stable';
      }
    });
    return trends;
  }
  private generateInsights(healthData: HealthData[]): string[] {
    // 生成健康洞察
    const insights: string[] = [];
        // 这里可以实现更复杂的洞察生成逻辑
    if (healthData.length > 0) {
      insights.push(`在分析期间共记录了${healthData.length}条健康数据`);
            const types = [...new Set(healthData.map(item => item.type))];
      insights.push(`监测了${types.length}种不同的健康指标`);
    }
    return insights;
  }
  private generateRecommendations(summary: HealthSummary): string[] {
    const recommendations: string[] = [...summary.recommendations];
        // 基于总体评分添加建议
    if (summary.overallScore < 60) {
      recommendations.push('建议咨询专业医生，制定个性化的健康改善计划');
    } else if (summary.overallScore < 80) {
      recommendations.push('继续保持良好的健康习惯，注意改善薄弱环节');
    } else {
      recommendations.push('您的健康状况良好，请继续保持');
    }
    return recommendations;
  }
  private mergeHealthData(localData: HealthData[], serverData: HealthData[]): HealthData[] {
    const merged = [...localData];
    const localIds = new Set(localData.map(item => item.id));
    // 添加服务器上有但本地没有的数据
    serverData.forEach(serverItem => {
      if (!localIds.has(serverItem.id)) {
        merged.push(serverItem);
      }
    });
    // 按时间排序
    merged.sort(a, b) =>
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
    return merged;
  }
  private async syncBatchToServer(dataList: HealthData[]): Promise<void> {
    try {
      await apiClient.post("HEALTH_DATA",/data/batch', { data: dataList });
    } catch (error) {
      console.error('Failed to sync batch to server:', error);
    }
  }
  private async syncDeleteToServer(id: string): Promise<void> {
    try {
      await apiClient.delete(`/health/data/${id}`);
    } catch (error) {
      console.error('Failed to sync delete to server:', error);
    }
  }
  private clearCache(): void {
    this.cache.clear();
  }
  private generateId(): string {
    return `health_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
// 导出单例实例
export const healthDataService = new HealthDataService();
// 导出React组件（如果需要）
export const HealthDataProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <>{children}</>;
};
export default healthDataService;