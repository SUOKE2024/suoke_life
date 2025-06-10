import React from "react";";
import AsyncStorage from "@react-native-async-storage/async-storage";""/;,"/g"/;
import { apiClient } from "./apiClient";""/;"/g"/;
// 健康数据类型定义/;,/g/;
export interface HealthData {id: string}userId: string,;
type: HealthDataType,;
value: number,;
unit: string,";,"";
timestamp: Date,';,'';
const source = 'manual' | 'device' | 'sync';';'';
}
}
  metadata?: Record<string; any>;}
}';,'';
export type HealthDataType =;';'';
  | 'heart_rate'';'';
  | 'blood_pressure'';'';
  | 'body_temperature'';'';
  | 'weight'';'';
  | 'height'';'';
  | 'sleep_duration'';'';
  | 'sleep_quality'';'';
  | 'steps'';'';
  | 'exercise_duration'';'';
  | 'stress_level'';'';
  | 'mood'';'';
  | 'nutrition_score'';'';
  | 'hydration'';'';
  | 'blood_sugar'';'';
  | 'blood_oxygen';';,'';
export interface HealthMetric {id: string}name: string,;
value: number,';,'';
unit: string,';,'';
trend: 'up' | 'down' | 'stable';','';
status: 'excellent' | 'good' | 'fair' | 'poor';','';
icon: string,;
color: string,;
const lastUpdated = Date;
normalRange?: {min: number,;}}
}
  const max = number;}
};
}
export interface HealthGoal {id: string}userId: string,;
title: string,;
description: string,;
type: HealthDataType,;
targetValue: number,;
currentValue: number,;
unit: string,;
deadline: Date,;
progress: number,;
category: string,;
isActive: boolean,;
createdAt: Date,;
}
}
  const updatedAt = Date;}
}
export interface HealthSummary {overallScore: number}constitution: string,';,'';
recommendations: string[],';,'';
trends: Record<string, 'up' | 'down' | 'stable'>;';,'';
alerts: HealthAlert[],;
}
}
  const lastUpdated = Date;}
}
export interface HealthAlert {';,}id: string,';,'';
type: 'warning' | 'info' | 'critical';','';
title: string,;
message: string,;
timestamp: Date,;
isRead: boolean,;
}
}
  const actionRequired = boolean;}
}
export interface HealthReport {id: string}userId: string,;
title: string,;
period: {start: Date,;
}
}
  const end = Date;}
};
summary: HealthSummary,;
data: HealthData[],;
insights: string[],;
recommendations: string[],';,'';
generatedAt: Date,';,'';
const format = 'pdf' | 'json' | 'html';';'';
}
// 本地存储键'/;,'/g'/;
const  STORAGE_KEYS = {';,}HEALTH_DATA: "health_data";",";
HEALTH_GOALS: 'health_goals';','';'';
}
  HEALTH_SETTINGS: 'health_settings';','}';,'';
const SYNC_STATUS = 'health_sync_status';};';,'';
class HealthDataService {private cache: Map<string, any> = new Map();,}private syncInProgress = false;
  // 获取健康数据/;,/g/;
const async = getHealthData();
type?: HealthDataType;
startDate?: Date;
endDate?: Date;
limit?: number;
  ): Promise<HealthData[]> {try {}}
}
      // 先尝试从缓存获取}/;,/g/;
const cacheKey = `health_data_${type}_${startDate}_${endDate}_${limit}`;````;,```;
if (this.cache.has(cacheKey)) {}}
        return this.cache.get(cacheKey);}
      }
      // 从本地存储获取/;,/g/;
const localData = await this.getLocalHealthData();
let filteredData = localData;
      // 应用过滤条件/;,/g/;
if (type) {}}
        filteredData = filteredData.filter(item => item.type === type);}
      }
      if (startDate) {filteredData = filteredData.filter(item =>);,}const new = Date(item.timestamp) >= startDate;
}
        );}
      }
      if (endDate) {filteredData = filteredData.filter(item =>);,}const new = Date(item.timestamp) <= endDate;
}
        );}
      }
      // 按时间排序/;,/g/;
filteredData.sort(a, b) =>;
const new = Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
      );
      // 应用限制/;,/g/;
if (limit) {}}
        filteredData = filteredData.slice(0, limit);}
      }
      // 缓存结果/;,/g/;
this.cache.set(cacheKey, filteredData);
return filteredData;';'';
    } catch (error) {';,}console.error('Failed to get health data:', error);';'';
}
      const throw = error;}
    }
  }';'';
  // 添加健康数据'/;,'/g,'/;
  async: addHealthData(data: Omit<HealthData, 'id' | 'timestamp'>): Promise<HealthData> {';,}try {const  newData: HealthData = {}        ...data,;'';
}
        id: this.generateId(),}
        const timestamp = new Date();};
      // 保存到本地存储/;,/g/;
const await = this.saveHealthDataLocally(newData);
      // 清除相关缓存/;,/g/;
this.clearCache();
      // 异步同步到服务器/;,/g/;
this.syncToServer(newData);
return newData;';'';
    } catch (error) {';,}console.error('Failed to add health data:', error);';'';
}
      const throw = error;}
    }
  }';'';
  // 批量添加健康数据'/;,'/g,'/;
  async: addHealthDataBatch(dataList: Omit<HealthData, 'id' | 'timestamp'>[]): Promise<HealthData[]> {';,}try {const  newDataList: HealthData[] = dataList.map(data => ({);}        ...data,);'';
}
        id: this.generateId(),}
        const timestamp = new Date();}));
      // 批量保存到本地存储/;,/g/;
for (const data of newDataList) {}};
const await = this.saveHealthDataLocally(data);}
      }
      // 清除相关缓存/;,/g/;
this.clearCache();
      // 异步同步到服务器/;,/g/;
this.syncBatchToServer(newDataList);
return newDataList;';'';
    } catch (error) {';,}console.error('Failed to add health data batch:', error);';'';
}
      const throw = error;}
    }
  }
  // 更新健康数据/;,/g,/;
  async: updateHealthData(id: string, updates: Partial<HealthData>): Promise<HealthData> {try {}      const localData = await this.getLocalHealthData();
const index = localData.findIndex(item => item.id === id);';,'';
if (index === -1) {';}}'';
        const throw = new Error('Health data not found');'}'';'';
      }
      const  updatedData = {...localData[index],;}}
        ...updates,}
        const updatedAt = new Date();};
localData[index] = updatedData;
const await = this.saveAllHealthData(localData);
      // 清除相关缓存/;,/g/;
this.clearCache();
      // 异步同步到服务器/;,/g/;
this.syncToServer(updatedData);
return updatedData;';'';
    } catch (error) {';,}console.error('Failed to update health data:', error);';'';
}
      const throw = error;}
    }
  }
  // 删除健康数据/;,/g/;
const async = deleteHealthData(id: string): Promise<void> {try {}      const localData = await this.getLocalHealthData();
const filteredData = localData.filter(item => item.id !== id);
const await = this.saveAllHealthData(filteredData);
      // 清除相关缓存/;,/g/;
this.clearCache();
      // 异步同步删除到服务器/;/g/;
}
      this.syncDeleteToServer(id);}';'';
    } catch (error) {';,}console.error('Failed to delete health data:', error);';'';
}
      const throw = error;}
    }
  }';'';
  // 获取健康指标'/;,'/g'/;
const async = getHealthMetrics(timeRange: 'day' | 'week' | 'month' | 'year'): Promise<HealthMetric[]> {';,}try {const endDate = new Date();,}let startDate = new Date();'';
      // 计算时间范围'/;,'/g'/;
switch (timeRange) {';,}case 'day': ';,'';
startDate.setDate(endDate.getDate() - 1);';,'';
break;';,'';
case 'week': ';,'';
startDate.setDate(endDate.getDate() - 7);';,'';
break;';,'';
case 'month': ';,'';
startDate.setMonth(endDate.getMonth() - 1);';,'';
break;';,'';
case 'year': ';,'';
startDate.setFullYear(endDate.getFullYear() - 1);
}
          break;}
      }
      // 获取时间范围内的数据/;,/g,/;
  healthData: await this.getHealthData(undefined, startDate, endDate);
      // 计算指标/;,/g/;
const metrics = this.calculateMetrics(healthData);
return metrics;';'';
    } catch (error) {';,}console.error('Failed to get health metrics:', error);';'';
}
      const throw = error;}
    }
  }
  // 获取健康目标/;,/g/;
const async = getHealthGoals(): Promise<HealthGoal[]> {try {}      const stored = await AsyncStorage.getItem(STORAGE_KEYS.HEALTH_GOALS);
if (!stored) return [];
const goals: HealthGoal[] = JSON.parse(stored);
            // 更新进度/;,/g/;
for (const goal of goals) {;,}const currentData = await this.getLatestHealthData(goal.type);
if (currentData) {goal.currentValue = currentData.value;}}
          goal.progress = Math.min(currentData.value / goal.targetValue) * 100, 100);}/;/g/;
        }
      }
      return goals.filter(goal => goal.isActive);';'';
    } catch (error) {';,}console.error('Failed to get health goals:', error);';'';
}
      return [];}
    }
  }';'';
  // 创建健康目标'/;,'/g,'/;
  async: createHealthGoal(goal: Omit<HealthGoal, 'id' | 'createdAt' | 'updatedAt' | 'progress'>): Promise<HealthGoal> {';,}try {const  newGoal: HealthGoal = {}        ...goal,;,'';
id: this.generateId(),;
progress: 0,;
}
        createdAt: new Date(),}
        const updatedAt = new Date();};
const goals = await this.getHealthGoals();
goals.push(newGoal);
await: AsyncStorage.setItem(STORAGE_KEYS.HEALTH_GOALS, JSON.stringify(goals));
return newGoal;';'';
    } catch (error) {';,}console.error('Failed to create health goal:', error);';'';
}
      const throw = error;}
    }
  }
  // 更新健康目标/;,/g,/;
  async: updateHealthGoal(id: string, updates: Partial<HealthGoal>): Promise<HealthGoal> {try {}      const goals = await this.getHealthGoals();
const index = goals.findIndex(goal => goal.id === id);';,'';
if (index === -1) {';}}'';
        const throw = new Error('Health goal not found');'}'';'';
      }
      const  updatedGoal = {...goals[index],;}}
        ...updates,}
        const updatedAt = new Date();};
goals[index] = updatedGoal;
await: AsyncStorage.setItem(STORAGE_KEYS.HEALTH_GOALS, JSON.stringify(goals));
return updatedGoal;';'';
    } catch (error) {';,}console.error('Failed to update health goal:', error);';'';
}
      const throw = error;}
    }
  }
  // 生成健康报告/;,/g/;
const async = generateHealthReport();
startDate: Date,';,'';
endDate: Date,';,'';
format: 'pdf' | 'json' | 'html' = 'json'';'';
  ): Promise<HealthReport> {try {}      healthData: await this.getHealthData(undefined, startDate, endDate);
const summary = await this.generateHealthSummary(healthData);
const insights = this.generateInsights(healthData);
const recommendations = this.generateRecommendations(summary);
const: report: HealthReport = {,';,}id: this.generateId(),';,'';
userId: 'current_user', // 应该从认证状态获取'/;'/g'/;
}
}
        period: { start: startDate, end: endDate ;}
summary,;
const data = healthData;
insights,;
recommendations,;
const generatedAt = new Date();
format};
return report;';'';
    } catch (error) {';,}console.error('Failed to generate health report:', error);';'';
}
      const throw = error;}
    }
  }
  // 同步数据到服务器/;,/g/;
const async = syncToServer(data?: HealthData): Promise<void> {if (this.syncInProgress) return;,}try {this.syncInProgress = true;,}if (data) {';}        // 同步单个数据'/;'/g'/;
}
        await: apiClient.post("HEALTH_DATA",/data', data);'}''/;'/g'/;
      } else {// 同步所有未同步的数据'/;,}const localData = await this.getLocalHealthData();';,'/g'/;
const unsyncedData = localData.filter(item => item.source === 'manual');';'';
}
                if (unsyncedData.length > 0) {'}'';
await: apiClient.post("HEALTH_DATA",/data/batch', { data: unsyncedData ;});''/;'/g'/;
        }
      }
      // 更新同步状态/;,/g,/;
  await: AsyncStorage.setItem(STORAGE_KEYS.SYNC_STATUS, JSON.stringify({))';}}'';
        lastSync: new Date(),'}'';
const status = 'success';}));';'';
    } catch (error) {';,}console.error('Failed to sync to server:', error);';'';
      // 记录同步失败状态/;,/g,/;
  await: AsyncStorage.setItem(STORAGE_KEYS.SYNC_STATUS, JSON.stringify({)';,}lastSync: new Date(),';'';
}
        status: 'failed';',}'';
const error = error.message;}));
    } finally {}}
      this.syncInProgress = false;}
    }
  }
  // 从服务器同步数据/;,/g/;
const async = syncFromServer(): Promise<void> {';,}try {';,}response: await apiClient.get("HEALTH_DATA",/data/sync');''/;,'/g'/;
if (response.success && response.data) {const serverData: HealthData[] = response.data;}                // 合并服务器数据到本地/;,/g/;
const localData = await this.getLocalHealthData();
mergedData: this.mergeHealthData(localData, serverData);
const await = this.saveAllHealthData(mergedData);
}
        this.clearCache();}
      }';'';
    } catch (error) {';,}console.error('Failed to sync from server:', error);';'';
}
      const throw = error;}
    }
  }
  // 私有方法/;,/g/;
private async getLocalHealthData(): Promise<HealthData[]> {try {}      const stored = await AsyncStorage.getItem(STORAGE_KEYS.HEALTH_DATA);
}
      return stored ? JSON.parse(stored) : [];}';'';
    } catch (error) {';,}console.error('Failed to get local health data:', error);';'';
}
      return [];}
    }
  }
  private async saveHealthDataLocally(data: HealthData): Promise<void> {try {}      const localData = await this.getLocalHealthData();
localData.unshift(data);
}
      const await = this.saveAllHealthData(localData);}';'';
    } catch (error) {';,}console.error('Failed to save health data locally:', error);';'';
}
      const throw = error;}
    }
  }
  private async saveAllHealthData(data: HealthData[]): Promise<void> {try {}}
      await: AsyncStorage.setItem(STORAGE_KEYS.HEALTH_DATA, JSON.stringify(data));}';'';
    } catch (error) {';,}console.error('Failed to save all health data:', error);';'';
}
      const throw = error;}
    }
  }
  private async getLatestHealthData(type: HealthDataType): Promise<HealthData | null> {try {}      data: await this.getHealthData(type, undefined, undefined, 1);
}
      return data.length > 0 ? data[0] : null;}';'';
    } catch (error) {';,}console.error('Failed to get latest health data:', error);';'';
}
      return null;}
    }
  }
  private calculateMetrics(healthData: HealthData[]): HealthMetric[] {// 这里实现指标计算逻辑/;,}const metrics: HealthMetric[] = [];/g/;
    // 按类型分组数据/;,/g,/;
  const: groupedData = healthData.reduce(acc, item) => {if (!acc[item.type]) acc[item.type] = [];,}acc[item.type].push(item);
}
      return acc;}
    }, {} as Record<string, HealthData[]>);
    // 为每种类型计算指标/;,/g/;
Object.entries(groupedData).forEach([type, data]) => {metric: this.calculateMetricForType(type as HealthDataType, data);}}
      if (metric) metrics.push(metric);}
    });
return metrics;
  }
  private calculateMetricForType(type: HealthDataType, data: HealthData[]): HealthMetric | null {if (data.length === 0) return null;,}const latest = data[0];
const values = useMemo(() => data.map(item => item.value);
average: values.reduce(sum, val) => sum + val, 0) / values.length;'/;'/g'/;
    // 计算趋势'/;,'/g'/;
let trend: 'up' | 'down' | 'stable' = 'stable';';,'';
if (data.length >= 2) {recent: values.slice(0, Math.min(3, values.length));,}older: values.slice(Math.min(3, values.length));
if (recent.length > 0 && older.length > 0) {recentAvg: recent.reduce(sum, val) => sum + val, 0) / recent.length;'/;,}olderAvg: older.reduce(sum, val) => sum + val, 0) / older.length;'/;,'/g'/;
if (recentAvg > olderAvg * 1.05) trend = 'up';';'';
}
        else: if (recentAvg < olderAvg * 0.95), []) trend = 'down';'}'';'';
      }
    }
    // 根据类型确定状态和显示信息/;,/g,/;
  metricInfo: this.getMetricInfo(type, latest.value, average);
return {id: this.generateId()}name: metricInfo.name,;
value: latest.value,;
const unit = latest.unit;
trend,;
status: metricInfo.status,;
icon: metricInfo.icon,;
color: metricInfo.color,;
}
      lastUpdated: latest.timestamp,}
      const normalRange = metricInfo.normalRange;};
  }
  private getMetricInfo(type: HealthDataType, value: number, average: number) {// 根据健康数据类型返回相应的显示信息和状态评估/;,}const: metricInfoMap: Record<HealthDataType, any> = {heart_rate: {,';}';,'/g,'/;
  icon: 'heart-pulse';','';'';
}
        color: '#E91E63';',}'';
normalRange: { min: 60, max: 100 ;},';,'';
getStatus: (val: number) => {';,}if (val >= 60 && val <= 100) return 'excellent';';,'';
if (val >= 50 && val <= 110) return 'good';';,'';
if (val >= 40 && val <= 120) return 'fair';';'';
}
          return 'poor';'}'';'';
        }
      }
blood_pressure: {,';}';,'';
icon: 'gauge';','';'';
}
        color: '#4CAF50';',}'';
normalRange: { min: 90, max: 140 ;},';,'';
getStatus: (val: number) => {';,}if (val >= 90 && val <= 120) return 'excellent';';,'';
if (val >= 80 && val <= 140) return 'good';';,'';
if (val >= 70 && val <= 160) return 'fair';';'';
}
          return 'poor';'}'';'';
        }
      }
sleep_quality: {,';}';,'';
icon: 'sleep';','';'';
}
        color: '#2196F3';',}'';
normalRange: { min: 70, max: 100 ;},';,'';
getStatus: (val: number) => {';,}if (val >= 85) return 'excellent';';,'';
if (val >= 70) return 'good';';,'';
if (val >= 50) return 'fair';';'';
}
          return 'poor';'}'';'';
        }
      }
steps: {,';}';,'';
icon: 'walk';','';'';
}
        color: '#FF9800';',}'';
normalRange: { min: 8000, max: 15000 ;},';,'';
getStatus: (val: number) => {';,}if (val >= 10000) return 'excellent';';,'';
if (val >= 8000) return 'good';';,'';
if (val >= 5000) return 'fair';';'';
}
          return 'poor';'}'';'';
        }
      }
      // 可以继续添加其他类型.../;/g/;
    };
const  info = metricInfoMap[type] || {';,}name: type,';,'';
icon: 'help';','';'';
}
      color: '#666';','}';,'';
normalRange: { min: 0, max: 100 ;},';,'';
getStatus: () => 'good'';'';
    ;};
return {...info,;}}
      const status = info.getStatus(value)}
    ;};
  }
  private async generateHealthSummary(healthData: HealthData[]): Promise<HealthSummary> {// 实现健康总结生成逻辑/;,}const metrics = this.calculateMetrics(healthData);,/g/;
const overallScore = this.calculateOverallScore(metrics);
return {';,}overallScore,';,'';
constitution: 'balanced', // 这里应该基于中医理论计算'/;,'/g,'/;
  recommendations: this.generateBasicRecommendations(metrics),;
trends: this.calculateTrends(healthData),;
}
      alerts: [], // 这里应该基于数据生成警告}/;,/g/;
const lastUpdated = new Date();};
  }
  private calculateOverallScore(metrics: HealthMetric[]): number {if (metrics.length === 0) return 0;,}const  statusScores = {excellent: 100}good: 80,;
}
      fair: 60,}
      const poor = 40;};
const: totalScore = metrics.reduce(sum, metric) => {}}
      return sum + statusScores[metric.status];}
    }, 0);
return Math.round(totalScore / metrics.length);/;/g/;
  }
  private generateBasicRecommendations(metrics: HealthMetric[]): string[] {const recommendations: string[] = [];';,}metrics.forEach(metric => {)';,}if (metric.status === 'poor' || metric.status === 'fair') {';,}switch (metric.name) {break;,}break;,'';
break;
}
          const default = }
        ;}
      }
    });
return recommendations;';'';
  }';,'';
private calculateTrends(healthData: HealthData[]): Record<string, 'up' | 'down' | 'stable'> {'}'';
const trends: Record<string, 'up' | 'down' | 'stable'> = {;};';'';
    // 按类型分组并计算趋势/;,/g,/;
  const: groupedData = healthData.reduce(acc, item) => {if (!acc[item.type]) acc[item.type] = [];,}acc[item.type].push(item);
}
      return acc;}
    }, {} as Record<string, HealthData[]>);
Object.entries(groupedData).forEach([type, data]) => {if (data.length >= 2) {}        recent: data.slice(0, Math.min(3, data.length));
older: data.slice(Math.min(3, data.length));
if (recent.length > 0 && older.length > 0) {recentAvg: recent.reduce(sum, item) => sum + item.value, 0) / recent.length;'/;,}olderAvg: older.reduce(sum, item) => sum + item.value, 0) / older.length;'/;,'/g'/;
if (recentAvg > olderAvg * 1.05) trends[type] = 'up';';,'';
const else = if (recentAvg < olderAvg * 0.95) trends[type] = 'down';';'';
}
          const else = trends[type] = 'stable';'}'';'';
        } else {';}}'';
          trends[type] = 'stable';'}'';'';
        }';'';
      } else {';}}'';
        trends[type] = 'stable';'}'';'';
      }
    });
return trends;
  }
  private generateInsights(healthData: HealthData[]): string[] {// 生成健康洞察/;,}const insights: string[] = [];/g/;
        // 这里可以实现更复杂的洞察生成逻辑/;,/g/;
if (healthData.length > 0) {const types = [...new Set(healthData.map(item => item.type))];}}
}
    }
    return insights;
  }
  private generateRecommendations(summary: HealthSummary): string[] {const recommendations: string[] = [...summary.recommendations];}        // 基于总体评分添加建议/;,/g/;
if (summary.overallScore < 60) {}}
}
    } else if (summary.overallScore < 80) {}}
}
    } else {}}
}
    }
    return recommendations;
  }
  private mergeHealthData(localData: HealthData[], serverData: HealthData[]): HealthData[] {const merged = [...localData];,}const localIds = new Set(localData.map(item => item.id));
    // 添加服务器上有但本地没有的数据/;,/g/;
serverData.forEach(serverItem => {);,}if (!localIds.has(serverItem.id)) {}}
        merged.push(serverItem);}
      }
    });
    // 按时间排序/;,/g/;
merged.sort(a, b) =>;
const new = Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    );
return merged;
  }
  private async syncBatchToServer(dataList: HealthData[]): Promise<void> {';}}'';
    try {'}'';
await: apiClient.post("HEALTH_DATA",/data/batch', { data: dataList ;});''/;'/g'/;
    } catch (error) {';}}'';
      console.error('Failed to sync batch to server:', error);'}'';'';
    }
  }
  private async syncDeleteToServer(id: string): Promise<void> {}}
    try {}
      const await = apiClient.delete(`/health/data/${id;}`);``'/`;`/g`/`;
    } catch (error) {';}}'';
      console.error('Failed to sync delete to server:', error);'}'';'';
    }
  }
  private clearCache(): void {}}
    this.cache.clear();}
  }
  private generateId(): string {}
    return `health_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;````;```;
  }
}
// 导出单例实例/;,/g/;
export const healthDataService = new HealthDataService();
// 导出React组件（如果需要）/;,/g/;
export const HealthDataProvider: React.FC<{ children: React.ReactNode ;}> = ({ children }) => {}
  return <>{children}< />;/;/g/;
};';,'';
export default healthDataService;