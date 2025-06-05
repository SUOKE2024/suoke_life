import { apiClient, ApiResponse } from './apiClient';

// 健康数据类型定义
export interface HealthData {
  id?: string;
  userId: string;
  dataType: HealthDataType;
  value: number | string | object;
  unit?: string;
  timestamp: string;
  source: DataSource;
  metadata?: Record<string, any>;
  tags?: string[];
  isPrivate?: boolean;
  createdAt?: string;
  updatedAt?: string;
}

// 生命体征数据
export interface VitalSigns {
  id?: string;
  userId: string;
  heartRate?: number;
  bloodPressure?: {
    systolic: number;
    diastolic: number;
  };
  temperature?: number;
  oxygenSaturation?: number;
  respiratoryRate?: number;
  weight?: number;
  height?: number;
  bmi?: number;
  timestamp: string;
  source: DataSource;
  notes?: string;
}

// 中医五诊数据
export interface TCMDiagnosisData {
  id?: string;
  userId: string;
  diagnosisType: TCMDiagnosisType;
  observations: TCMObservation[];
  conclusion?: string;
  recommendations?: string[];
  practitionerId?: string;
  timestamp: string;
  confidence?: number;
  metadata?: Record<string, any>;
}

// 中医观察数据
export interface TCMObservation {
  category: string;
  subcategory?: string;
  value: string | number;
  description?: string;
  severity?: 'mild' | 'moderate' | 'severe';
  confidence?: number;
}

// 健康趋势分析
export interface HealthTrend {
  dataType: HealthDataType;
  period: 'daily' | 'weekly' | 'monthly' | 'yearly';
  trend: 'increasing' | 'decreasing' | 'stable';
  changeRate: number;
  averageValue: number;
  minValue: number;
  maxValue: number;
  dataPoints: Array<{
    timestamp: string;
    value: number;
  }>;
}

// 健康报告
export interface HealthReport {
  id: string;
  userId: string;
  reportType: 'comprehensive' | 'vital_signs' | 'tcm_analysis' | 'trend_analysis';
  period: {
    startDate: string;
    endDate: string;
  };
  summary: string;
  insights: string[];
  recommendations: string[];
  riskFactors: string[];
  trends: HealthTrend[];
  score: number;
  generatedAt: string;
}

// 枚举类型
export enum HealthDataType {
  VITAL_SIGNS = 'vital_signs',
  BLOOD_GLUCOSE = 'blood_glucose',
  BLOOD_PRESSURE = 'blood_pressure',
  HEART_RATE = 'heart_rate',
  TEMPERATURE = 'temperature',
  WEIGHT = 'weight',
  HEIGHT = 'height',
  BMI = 'bmi',
  SLEEP = 'sleep',
  EXERCISE = 'exercise',
  NUTRITION = 'nutrition',
  MEDICATION = 'medication',
  SYMPTOMS = 'symptoms',
  TCM_DIAGNOSIS = 'tcm_diagnosis',
  LAB_RESULTS = 'lab_results',
  MENTAL_HEALTH = 'mental_health'
}

export enum DataSource {
  MANUAL = 'manual',
  DEVICE = 'device',
  WEARABLE = 'wearable',
  MEDICAL_DEVICE = 'medical_device',
  LABORATORY = 'laboratory',
  HEALTHCARE_PROVIDER = 'healthcare_provider',
  AI_ANALYSIS = 'ai_analysis'
}

export enum TCMDiagnosisType {
  LOOK = 'look',      // 望诊
  LISTEN = 'listen',  // 闻诊
  ASK = 'ask',        // 问诊
  TOUCH = 'touch',    // 切诊
  CALCULATE = 'calculate' // 算诊
}

export enum ExportFormat {
  JSON = 'json',
  CSV = 'csv',
  PDF = 'pdf',
  XML = 'xml'
}

export enum ImportFormat {
  JSON = 'json',
  CSV = 'csv',
  APPLE_HEALTH = 'apple_health',
  GOOGLE_FIT = 'google_fit'
}

// 查询参数
export interface HealthDataQuery {
  userId?: string;
  dataType?: HealthDataType;
  startDate?: string;
  endDate?: string;
  source?: DataSource;
  tags?: string[];
  limit?: number;
  offset?: number;
  sortBy?: 'timestamp' | 'createdAt' | 'value';
  sortOrder?: 'asc' | 'desc';
}

// 健康数据服务类
export class HealthDataService {
  private readonly baseUrl = '/api/v1/health-data';

  // 创建健康数据
  async createHealthData(data: Omit<HealthData, 'id' | 'createdAt' | 'updatedAt'>): Promise<ApiResponse<HealthData>> {
    return await apiClient.post<HealthData>(`${this.baseUrl}/`, data);
  }

  // 批量创建健康数据
  async createBatchHealthData(dataList: Omit<HealthData, 'id' | 'createdAt' | 'updatedAt'>[]): Promise<ApiResponse<HealthData[]>> {
    return await apiClient.post<HealthData[]>(`${this.baseUrl}/batch`, { data: dataList });
  }

  // 获取健康数据
  async getHealthData(id: string): Promise<ApiResponse<HealthData>> {
    return await apiClient.get<HealthData>(`${this.baseUrl}/${id}`);
  }

  // 查询健康数据列表
  async queryHealthData(query: HealthDataQuery): Promise<ApiResponse<{
    data: HealthData[];
    total: number;
    page: number;
    pageSize: number;
  }>> {
    const queryString = new URLSearchParams(query as any).toString();
    return await apiClient.get<{
      data: HealthData[];
      total: number;
      page: number;
      pageSize: number;
    }>(`${this.baseUrl}/?${queryString}`);
  }

  // 更新健康数据
  async updateHealthData(id: string, data: Partial<HealthData>): Promise<ApiResponse<HealthData>> {
    return await apiClient.post<HealthData>(`${this.baseUrl}/${id}`, { ...data, _method: 'PUT' });
  }

  // 删除健康数据
  async deleteHealthData(id: string): Promise<ApiResponse<void>> {
    return await apiClient.post<void>(`${this.baseUrl}/${id}`, { _method: 'DELETE' });
  }

  // 生命体征相关方法
  async createVitalSigns(data: Omit<VitalSigns, 'id'>): Promise<ApiResponse<VitalSigns>> {
    return await apiClient.post<VitalSigns>(`${this.baseUrl}/vital-signs`, data);
  }

  async getVitalSigns(userId: string, startDate?: string, endDate?: string): Promise<ApiResponse<VitalSigns[]>> {
    const params = new URLSearchParams({ userId });
    if (startDate) params.append('startDate', startDate);
    if (endDate) params.append('endDate', endDate);
    
    return await apiClient.get<VitalSigns[]>(`${this.baseUrl}/vital-signs?${params.toString()}`);
  }

  async getLatestVitalSigns(userId: string): Promise<ApiResponse<VitalSigns>> {
    return await apiClient.get<VitalSigns>(`${this.baseUrl}/vital-signs/latest?userId=${userId}`);
  }

  // 中医五诊相关方法
  async createTCMDiagnosis(data: Omit<TCMDiagnosisData, 'id'>): Promise<ApiResponse<TCMDiagnosisData>> {
    return await apiClient.post<TCMDiagnosisData>(`${this.baseUrl}/tcm-diagnosis`, data);
  }

  async getTCMDiagnosis(userId: string, diagnosisType?: TCMDiagnosisType): Promise<ApiResponse<TCMDiagnosisData[]>> {
    const params = new URLSearchParams({ userId });
    if (diagnosisType) params.append('diagnosisType', diagnosisType);
    
    return await apiClient.get<TCMDiagnosisData[]>(`${this.baseUrl}/tcm-diagnosis?${params.toString()}`);
  }

  async updateTCMDiagnosis(id: string, data: Partial<TCMDiagnosisData>): Promise<ApiResponse<TCMDiagnosisData>> {
    return await apiClient.post<TCMDiagnosisData>(`${this.baseUrl}/tcm-diagnosis/${id}`, { ...data, _method: 'PUT' });
  }

  // 健康趋势分析
  async getHealthTrends(
    userId: string, 
    dataType: HealthDataType, 
    period: 'daily' | 'weekly' | 'monthly' | 'yearly'
  ): Promise<ApiResponse<HealthTrend>> {
    const params = new URLSearchParams({ userId, dataType, period });
    return await apiClient.get<HealthTrend>(`${this.baseUrl}/trends?${params.toString()}`);
  }

  async getMultipleHealthTrends(
    userId: string,
    dataTypes: HealthDataType[],
    period: 'daily' | 'weekly' | 'monthly' | 'yearly'
  ): Promise<ApiResponse<HealthTrend[]>> {
    return await apiClient.post<HealthTrend[]>(`${this.baseUrl}/trends/multiple`, {
      userId,
      dataTypes,
      period
    });
  }

  // 健康报告
  async generateHealthReport(
    userId: string,
    reportType: 'comprehensive' | 'vital_signs' | 'tcm_analysis' | 'trend_analysis',
    startDate: string,
    endDate: string
  ): Promise<ApiResponse<HealthReport>> {
    return await apiClient.post<HealthReport>(`${this.baseUrl}/reports/generate`, {
      userId,
      reportType,
      startDate,
      endDate
    });
  }

  async getHealthReport(reportId: string): Promise<ApiResponse<HealthReport>> {
    return await apiClient.get<HealthReport>(`${this.baseUrl}/reports/${reportId}`);
  }

  async getUserHealthReports(userId: string): Promise<ApiResponse<HealthReport[]>> {
    return await apiClient.get<HealthReport[]>(`${this.baseUrl}/reports?userId=${userId}`);
  }

  // 数据统计
  async getHealthDataStats(userId: string, period?: string): Promise<ApiResponse<{
    totalRecords: number;
    dataTypeDistribution: Record<string, number>;
    sourceDistribution: Record<string, number>;
    recentActivity: Array<{
      date: string;
      count: number;
    }>;
  }>> {
    const params = new URLSearchParams({ userId });
    if (period) params.append('period', period);
    
    return await apiClient.get(`${this.baseUrl}/stats?${params.toString()}`);
  }

  // 数据导出
  async exportHealthData(
    userId: string,
    format: ExportFormat,
    startDate?: string,
    endDate?: string,
    dataTypes?: HealthDataType[]
  ): Promise<ApiResponse<{ downloadUrl: string }>> {
    return await apiClient.post<{ downloadUrl: string }>(`${this.baseUrl}/export`, {
      userId,
      format,
      startDate,
      endDate,
      dataTypes
    });
  }

  // 数据导入
  async importHealthData(
    userId: string,
    format: ImportFormat,
    fileData: string | ArrayBuffer,
    options?: {
      mergeStrategy?: 'replace' | 'merge' | 'skip';
      validateData?: boolean;
    }
  ): Promise<ApiResponse<{
    importedCount: number;
    skippedCount: number;
    errorCount: number;
    errors: string[];
  }>> {
    return await apiClient.post(`${this.baseUrl}/import`, {
      userId,
      format,
      fileData,
      options
    });
  }

  // 数据同步
  async syncHealthData(userId: string, lastSyncTime?: string): Promise<ApiResponse<{
    newData: HealthData[];
    updatedData: HealthData[];
    deletedIds: string[];
    lastSyncTime: string;
  }>> {
    const params = new URLSearchParams({ userId });
    if (lastSyncTime) params.append('lastSyncTime', lastSyncTime);
    
    return await apiClient.get(`${this.baseUrl}/sync?${params.toString()}`);
  }

  // 健康提醒设置
  async setHealthReminder(
    userId: string,
    dataType: HealthDataType,
    reminderConfig: {
      enabled: boolean;
      frequency: 'daily' | 'weekly' | 'monthly';
      time?: string;
      threshold?: {
        min?: number;
        max?: number;
      };
    }
  ): Promise<ApiResponse<void>> {
    return await apiClient.post(`${this.baseUrl}/reminders`, {
      userId,
      dataType,
      ...reminderConfig
    });
  }

  async getHealthReminders(userId: string): Promise<ApiResponse<Array<{
    dataType: HealthDataType;
    enabled: boolean;
    frequency: string;
    time?: string;
    threshold?: any;
  }>>> {
    return await apiClient.get(`${this.baseUrl}/reminders?userId=${userId}`);
  }

  // 健康数据验证
  async validateHealthData(data: Omit<HealthData, 'id' | 'createdAt' | 'updatedAt'>): Promise<ApiResponse<{
    isValid: boolean;
    errors: string[];
    warnings: string[];
  }>> {
    return await apiClient.post(`${this.baseUrl}/validate`, data);
  }

  // 健康数据搜索
  async searchHealthData(
    userId: string,
    query: string,
    filters?: {
      dataTypes?: HealthDataType[];
      dateRange?: {
        start: string;
        end: string;
      };
    }
  ): Promise<ApiResponse<HealthData[]>> {
    return await apiClient.post<HealthData[]>(`${this.baseUrl}/search`, {
      userId,
      query,
      filters
    });
  }
}

// 创建健康数据服务实例
export const healthDataService = new HealthDataService(); 