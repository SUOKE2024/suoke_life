import AsyncStorage from '@react-native-async-storage/async-storage';
// 健康数据类型定义
export interface HealthData {
  id?: string;
  userId: string;
  type: HealthDataType;
  value: number;
  unit: string;
  timestamp: Date;
  source: 'manual' | 'device' | 'sync';
  metadata?: Record<string; any>;
}
export type HealthDataType =;
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
  period: {,
  start: Date;
  end: Date;
  };
  summary: HealthSummary;
  data: HealthData[];
  insights: string[];
  recommendations: string[];
  generatedAt: Date;
  format: 'pdf' | 'json' | 'html';
}
// 本地存储键
const STORAGE_KEYS = {
  HEALTH_DATA: "health_data";
  HEALTH_GOALS: 'health_goals';
  HEALTH_SETTINGS: 'health_settings';
  SYNC_STATUS: 'health_sync_status'
;};
class HealthDataService {
  private cache: Map<string, any> = new Map();
  private syncInProgress = false;
  // 获取健康数据
  async getHealthData(
    type?: HealthDataType;
    startDate?: Date;
    endDate?: Date;
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
        filteredData = filteredData.filter(item =>
          new Date(item.timestamp) >= startDate;
        );
      }
      if (endDate) {
        filteredData = filteredData.filter(item =>
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
      // 返回模拟数据
      return [
        {
          id: "1";

          value: 72;
          unit: 'bpm';
          trend: 'stable';
          status: 'good';
          icon: 'heart-pulse';
          color: '#E91E63';
          lastUpdated: new Date();
          normalRange: { min: 60, max: 100 ;}
        },
        {
          id: "2";

          value: 120;
          unit: 'mmHg';
          trend: 'up';
          status: 'excellent';
          icon: 'gauge';
          color: '#4CAF50';
          lastUpdated: new Date();
          normalRange: { min: 90, max: 140 ;}
        }
      ];
    }
  }
  // 获取健康目标
  async getHealthGoals(userId: string): Promise<HealthGoal[]> {
    try {
      const stored = await AsyncStorage.getItem(STORAGE_KEYS.HEALTH_GOALS);
      const goals: HealthGoal[] = stored ? JSON.parse(stored) : [];
      return goals.filter(goal => goal.userId === userId);
    } catch (error) {
      console.error('Failed to get health goals:', error);
      return [];
    }
  }
  // 添加健康数据
  async addHealthData(data: Omit<HealthData, 'id'>): Promise<HealthData> {
    try {
      const newData: HealthData = {
        ...data,
        id: this.generateId();
        timestamp: data.timestamp || new Date()
      ;};
      // 保存到本地存储
      await this.saveLocalHealthData(newData);
      // 同步到服务器
      await this.syncToServer(newData);
      // 清除相关缓存
      this.clearCache();
      return newData;
    } catch (error) {
      console.error('Failed to add health data:', error);
      throw error;
    }
  }
  // 创建健康目标
  async createHealthGoal(goal: Omit<HealthGoal, 'id' | 'createdAt' | 'updatedAt'>): Promise<HealthGoal> {
    try {
      const newGoal: HealthGoal = {
        ...goal,
        id: this.generateId();
        createdAt: new Date();
        updatedAt: new Date()
      ;};
      const stored = await AsyncStorage.getItem(STORAGE_KEYS.HEALTH_GOALS);
      const goals: HealthGoal[] = stored ? JSON.parse(stored) : [];
      goals.push(newGoal);
      await AsyncStorage.setItem(STORAGE_KEYS.HEALTH_GOALS, JSON.stringify(goals));
      return newGoal;
    } catch (error) {
      console.error('Failed to create health goal:', error);
      throw error;
    }
  }
  // 更新健康目标
  async updateHealthGoal(goalId: string, updates: Partial<HealthGoal>): Promise<HealthGoal> {
    try {
      const stored = await AsyncStorage.getItem(STORAGE_KEYS.HEALTH_GOALS);
      const goals: HealthGoal[] = stored ? JSON.parse(stored) : [];
      
      const goalIndex = goals.findIndex(goal => goal.id === goalId);
      if (goalIndex === -1) {
        throw new Error('Goal not found');
      }
      goals[goalIndex] = {
        ...goals[goalIndex],
        ...updates,
        updatedAt: new Date()
      ;};
      await AsyncStorage.setItem(STORAGE_KEYS.HEALTH_GOALS, JSON.stringify(goals));
      return goals[goalIndex];
    } catch (error) {
      console.error('Failed to update health goal:', error);
      throw error;
    }
  }
  // 获取健康摘要
  async getHealthSummary(userId: string, timeRange: 'day' | 'week' | 'month' | 'year'): Promise<HealthSummary> {
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
      const healthData = await this.getHealthData(undefined, startDate, endDate);
      const userHealthData = healthData.filter(data => data.userId === userId);
      
      return await this.generateHealthSummary(userHealthData);
    } catch (error) {
      console.error('Failed to get health summary:', error);
      // 返回默认摘要
      return {
        overallScore: 75;
        constitution: 'balanced';

        trends: {;},
        alerts: [];
        lastUpdated: new Date()
      ;};
    }
  }
  // 生成健康报告
  async generateHealthReport(
    userId: string;
    startDate: Date;
    endDate: Date;
    format: 'pdf' | 'json' | 'html' = 'json'
  ): Promise<HealthReport> {
    try {
      const healthData = await this.getHealthData(undefined, startDate, endDate);
      const userHealthData = healthData.filter(data => data.userId === userId);
      const summary = await this.generateHealthSummary(userHealthData);
      const report: HealthReport = {,
  id: this.generateId();
        userId,

        period: { start: startDate, end: endDate ;},
        summary,
        data: userHealthData;
        insights: this.generateInsights(userHealthData);
        recommendations: this.generateRecommendations(summary);
        generatedAt: new Date();
        format;
      };
      return report;
    } catch (error) {
      console.error('Failed to generate health report:', error);
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
  private async saveLocalHealthData(data: HealthData): Promise<void> {
    try {
      const stored = await AsyncStorage.getItem(STORAGE_KEYS.HEALTH_DATA);
      const healthData: HealthData[] = stored ? JSON.parse(stored) : [];
      
      // 检查是否已存在
      const existingIndex = healthData.findIndex(item => item.id === data.id);
      if (existingIndex >= 0) {
        healthData[existingIndex] = data;
      } else {
        healthData.push(data);
      }
      await AsyncStorage.setItem(STORAGE_KEYS.HEALTH_DATA, JSON.stringify(healthData));
    } catch (error) {
      console.error('Failed to save local health data:', error);
      throw error;
    }
  }
  private calculateMetrics(healthData: HealthData[]): HealthMetric[] {
    const metrics: HealthMetric[] = [];
    // 按类型分组数据
    const groupedData = healthData.reduce(acc, item) => {
      if (!acc[item.type]) acc[item.type] = [];
      acc[item.type].push(item);
      return acc;
    }, {} as Record<string, HealthData[]>);
    // 为每种类型计算指标
    Object.entries(groupedData).forEach([type, data]) => {
      const metric = this.calculateMetricForType(type as HealthDataType, data);
      if (metric) metrics.push(metric);
    });
    return metrics;
  }
  private calculateMetricForType(type: HealthDataType, data: HealthData[]): HealthMetric | null {
    if (data.length === 0) return null;
    const latest = data[0];
    const values = data.map(item => item.value);
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
    const metricInfo = this.getMetricInfo(type, latest.value);
    return {
      id: this.generateId();
      name: metricInfo.name;
      value: latest.value;
      unit: latest.unit;
      trend,
      status: metricInfo.status;
      icon: metricInfo.icon;
      color: metricInfo.color;
      lastUpdated: latest.timestamp;
      normalRange: metricInfo.normalRange;
    };
  }
  private getMetricInfo(type: HealthDataType, value: number) {
    const metricInfoMap: Record<HealthDataType, any> = {
      heart_rate: {,

        icon: 'heart-pulse';
        color: '#E91E63';
        normalRange: { min: 60, max: 100 ;},
        getStatus: (val: number) => {
          if (val >= 60 && val <= 100) return 'excellent';
          if (val >= 50 && val <= 110) return 'good';
          if (val >= 40 && val <= 120) return 'fair';
          return 'poor';
        }
      },
      blood_pressure: {,

        icon: 'gauge';
        color: '#4CAF50';
        normalRange: { min: 90, max: 140 ;},
        getStatus: (val: number) => {
          if (val >= 90 && val <= 120) return 'excellent';
          if (val >= 80 && val <= 140) return 'good';
          if (val >= 70 && val <= 160) return 'fair';
          return 'poor';
        }
      },
      sleep_quality: {,

        icon: 'sleep';
        color: '#2196F3';
        normalRange: { min: 70, max: 100 ;},
        getStatus: (val: number) => {
          if (val >= 85) return 'excellent';
          if (val >= 70) return 'good';
          if (val >= 50) return 'fair';
          return 'poor';
        }
      },
      steps: {,

        icon: 'walk';
        color: '#FF9800';
        normalRange: { min: 8000, max: 15000 ;},
        getStatus: (val: number) => {
          if (val >= 10000) return 'excellent';
          if (val >= 8000) return 'good';
          if (val >= 5000) return 'fair';
          return 'poor';
        }
      },
      // 默认处理其他类型
      body_temperature: {,

        icon: 'thermometer'; 
        color: '#FF5722'; 
        normalRange: { min: 36, max: 37.5 ;}, 
        getStatus: () => 'good' 
      ;},
      weight: {,

        icon: 'scale-bathroom'; 
        color: '#9C27B0'; 
        normalRange: { min: 50, max: 100 ;}, 
        getStatus: () => 'good' 
      ;},
      height: {,

        icon: 'human-male-height'; 
        color: '#607D8B'; 
        normalRange: { min: 150, max: 200 ;}, 
        getStatus: () => 'good' 
      ;},
      sleep_duration: {,

        icon: 'sleep'; 
        color: '#3F51B5'; 
        normalRange: { min: 7, max: 9 ;}, 
        getStatus: () => 'good' 
      ;},
      exercise_duration: {,

        icon: 'run'; 
        color: '#FF9800'; 
        normalRange: { min: 30, max: 120 ;}, 
        getStatus: () => 'good' 
      ;},
      stress_level: {,

        icon: 'brain'; 
        color: '#F44336'; 
        normalRange: { min: 0, max: 50 ;}, 
        getStatus: () => 'good' 
      ;},
      mood: {,

        icon: 'emoticon-happy'; 
        color: '#FFEB3B'; 
        normalRange: { min: 60, max: 100 ;}, 
        getStatus: () => 'good' 
      ;},
      nutrition_score: {,

        icon: 'food-apple'; 
        color: '#8BC34A'; 
        normalRange: { min: 70, max: 100 ;}, 
        getStatus: () => 'good' 
      ;},
      hydration: {,

        icon: 'water'; 
        color: '#00BCD4'; 
        normalRange: { min: 1500, max: 3000 ;}, 
        getStatus: () => 'good' 
      ;},
      blood_sugar: {,

        icon: 'diabetes'; 
        color: '#795548'; 
        normalRange: { min: 70, max: 140 ;}, 
        getStatus: () => 'good' 
      ;},
      blood_oxygen: {,

        icon: 'lungs'; 
        color: '#009688'; 
        normalRange: { min: 95, max: 100 ;}, 
        getStatus: () => 'good' 
      ;}
    };
    const info = metricInfoMap[type] || {
      name: type;
      icon: 'help';
      color: '#666';
      normalRange: { min: 0, max: 100 ;},
      getStatus: () => 'good'
    ;};
    return {
      ...info,
      status: info.getStatus(value)
    ;};
  }
  private async generateHealthSummary(healthData: HealthData[]): Promise<HealthSummary> {
    const metrics = this.calculateMetrics(healthData);
    const overallScore = this.calculateOverallScore(metrics);
    
    return {
      overallScore,
      constitution: 'balanced';
      recommendations: this.generateBasicRecommendations(metrics);
      trends: this.calculateTrends(healthData);
      alerts: [];
      lastUpdated: new Date()
    ;};
  }
  private calculateOverallScore(metrics: HealthMetric[]): number {
    if (metrics.length === 0) return 0;
    const statusScores = {
      excellent: 100;
      good: 80;
      fair: 60;
      poor: 40;
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


            break;


            break;


            break;


            break;
          default:

        ;}
      }
    });
    if (recommendations.length === 0) {

    }
    return recommendations;
  }
  private calculateTrends(healthData: HealthData[]): Record<string, 'up' | 'down' | 'stable'> {
    const trends: Record<string, 'up' | 'down' | 'stable'> = {;};
    
    // 按类型分组数据
    const groupedData = healthData.reduce(acc, item) => {
      if (!acc[item.type]) acc[item.type] = [];
      acc[item.type].push(item);
      return acc;
    }, {} as Record<string, HealthData[]>);
    Object.entries(groupedData).forEach([type, data]) => {
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
    const insights: string[] = [];
    
    if (healthData.length === 0) {

      return insights;
    }
    const metrics = this.calculateMetrics(healthData);
    const excellentMetrics = metrics.filter(m => m.status === 'excellent');
    const poorMetrics = metrics.filter(m => m.status === 'poor');
    if (excellentMetrics.length > 0) {

    }
    if (poorMetrics.length > 0) {

    }
    return insights;
  }
  private generateRecommendations(summary: HealthSummary): string[] {
    const recommendations: string[] = [...summary.recommendations];
    
    if (summary.overallScore < 60) {

    } else if (summary.overallScore < 80) {

    } else {

    }
    return recommendations;
  }
  private async syncToServer(data?: HealthData): Promise<void> {
    if (this.syncInProgress) return;
    
    try {
      this.syncInProgress = true;
      // 实现服务器同步逻辑
      // await apiClient.post('/health/sync', data);
    } catch (error) {
      console.error('Sync to server failed:', error);
    } finally {
      this.syncInProgress = false;
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
export default healthDataService;