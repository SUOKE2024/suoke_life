import axios from 'axios';
import { API_BASE_URL, AGENT_SERVICE_PORTS } from '../../config/constants';

// 创建专用的soer API客户端
const soerClient = axios.create({
  baseURL: `${API_BASE_URL}:${AGENT_SERVICE_PORTS.soer}`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 健康计划请求和响应类型
export interface HealthPlanRequest {
  user_id: string;
  constitution_type: string;
  health_goals: string[];
  preferences: Record<string, string[]>;
  current_season: string;
}

export interface HealthPlanResponse {
  plan_id: string;
  diet_recommendations: string[];
  exercise_recommendations: string[];
  lifestyle_recommendations: string[];
  supplement_recommendations: string[];
  schedule: Record<string, string>;
  confidence_score: number;
}

// 传感器数据请求和响应类型
export interface DataPoint {
  timestamp: string;
  values: Record<string, number>;
  metadata?: Record<string, string>;
}

export interface SensorData {
  sensor_type: string;
  device_id: string;
  data_points: DataPoint[];
}

export interface SensorDataRequest {
  user_id: string;
  data: SensorData[];
}

export interface HealthMetric {
  metric_name: string;
  current_value: number;
  reference_min: number;
  reference_max: number;
  interpretation: string;
  trend: string;
}

export interface Insight {
  category: string;
  description: string;
  confidence: number;
  suggestions: string[];
}

export interface SensorDataResponse {
  metrics: HealthMetric[];
  insights: Insight[];
}

// 营养请求和响应类型
export interface FoodEntry {
  food_name: string;
  quantity: number;
  unit: string;
  timestamp: string;
  properties?: Record<string, string>;
}

export interface NutritionRequest {
  user_id: string;
  food_entries: FoodEntry[];
  analysis_type: string;
}

export interface NutrientBalance {
  nutrient: string;
  current: number;
  target: number;
  status: string;
}

export interface FoodSuggestion {
  food: string;
  benefits: string[];
  recommendation_strength: number;
  reason: string;
}

export interface ConstitutionalAnalysis {
  five_elements_balance: Record<string, number>;
  five_tastes_distribution: Record<string, number>;
  imbalance_corrections: string[];
}

export interface NutritionResponse {
  nutrient_summary: Record<string, number>;
  balance: NutrientBalance[];
  suggestions: FoodSuggestion[];
  constitutional_analysis: ConstitutionalAnalysis;
}

// 睡眠相关类型
export interface SleepPhase {
  phase_type: string;
  start_time: string;
  end_time: string;
}

export interface SleepData {
  sleep_start: string;
  sleep_end: string;
  phases: SleepPhase[];
  efficiency: number;
  awakenings: number;
}

export interface SleepRequest {
  user_id: string;
  recent_sleep: SleepData[];
  constitution_type: string;
  lifestyle_factors: Record<string, string>;
}

export interface SleepQuality {
  overall_score: number;
  component_scores: Record<string, number>;
  improvement_areas: string[];
  positive_aspects: string[];
}

export interface SleepRecommendation {
  category: string;
  suggestion: string;
  reasoning: string;
  expected_impact: number;
  is_personalized: boolean;
}

export interface SleepResponse {
  sleep_quality: SleepQuality;
  recommendations: SleepRecommendation[];
  environmental_factors: string[];
  optimal_sleep_schedule: string;
}

// 情绪分析类型
export interface EmotionalInput {
  input_type: string;
  data: string;
  metadata?: Record<string, string>;
  timestamp: string;
}

export interface EmotionalStateRequest {
  user_id: string;
  inputs: EmotionalInput[];
}

export interface EmotionalImpact {
  affected_systems: string[];
  tcm_interpretation: string;
  severity: number;
}

export interface EmotionalSuggestion {
  intervention_type: string;
  description: string;
  estimated_effectiveness: number;
  is_urgent: boolean;
}

export interface EmotionalStateResponse {
  emotion_scores: Record<string, number>;
  primary_emotion: string;
  emotional_tendency: string;
  health_impact: EmotionalImpact;
  suggestions: EmotionalSuggestion[];
}

// 索儿智能体API服务
const soerApi = {
  /**
   * 生成个性化健康计划
   * @param data 健康计划请求数据
   * @returns 健康计划响应
   */
  generateHealthPlan: async (data: HealthPlanRequest): Promise<HealthPlanResponse> => {
    try {
      const response = await soerClient.post('/api/v1/soer/health-plans', data);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || '生成健康计划失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取特定健康计划
   * @param planId 健康计划ID
   * @returns 健康计划响应
   */
  getHealthPlan: async (planId: string): Promise<HealthPlanResponse> => {
    try {
      const response = await soerClient.get(`/api/v1/soer/health-plans/${planId}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || '获取健康计划失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取用户当前活跃的健康计划
   * @param userId 用户ID
   * @returns 健康计划响应
   */
  getActivePlan: async (userId: string): Promise<HealthPlanResponse> => {
    try {
      const response = await soerClient.get(`/api/v1/soer/users/${userId}/active-plan`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || '获取活跃健康计划失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取用户健康画像
   * @param userId 用户ID
   * @param summary 是否仅返回摘要
   * @returns 健康画像数据
   */
  getHealthProfile: async (userId: string, summary: boolean = false): Promise<Record<string, any>> => {
    try {
      const response = await soerClient.get(`/api/v1/soer/users/${userId}/health-profile`, {
        params: { summary }
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || '获取健康画像失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 分析传感器数据
   * @param userId 用户ID
   * @param request 传感器数据请求
   * @returns 传感器数据分析结果
   */
  analyzeSensorData: async (userId: string, request: SensorDataRequest): Promise<SensorDataResponse> => {
    try {
      const response = await soerClient.post(`/api/v1/soer/users/${userId}/sensor-data/analyze`, request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || '分析传感器数据失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 跟踪用户营养摄入
   * @param userId 用户ID
   * @param request 营养请求数据
   * @returns 营养分析结果
   */
  trackNutrition: async (userId: string, request: NutritionRequest): Promise<NutritionResponse> => {
    try {
      const response = await soerClient.post(`/api/v1/soer/users/${userId}/nutrition/track`, request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || '追踪营养摄入失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 生成个性化饮食推荐
   * @param userId 用户ID
   * @param constitutionType 体质类型
   * @param season 当前季节
   * @param preferences 用户偏好
   * @returns 饮食推荐
   */
  generateDietRecommendations: async (
    userId: string,
    constitutionType: string,
    season: string,
    preferences?: Record<string, any>
  ): Promise<Record<string, any>> => {
    try {
      const response = await soerClient.post(
        `/api/v1/soer/users/${userId}/diet-recommendations`,
        preferences,
        {
          params: { constitution_type: constitutionType, season }
        }
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || '生成饮食推荐失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取食物详情
   * @param foodName 食物名称
   * @returns 食物详情
   */
  getFoodDetails: async (foodName: string): Promise<Record<string, any>> => {
    try {
      const response = await soerClient.get(`/api/v1/soer/food/${foodName}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || '获取食物详情失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 根据体质获取食谱
   * @param constitutionType 体质类型
   * @param season 季节（可选）
   * @returns 食谱列表
   */
  getRecipesByConstitution: async (
    constitutionType: string,
    season?: string
  ): Promise<Record<string, any>[]> => {
    try {
      const response = await soerClient.get(`/api/v1/soer/constitutions/${constitutionType}/recipes`, {
        params: season ? { season } : {}
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || '获取体质食谱失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 分析情绪状态
   * @param request 情绪状态请求数据
   * @returns 情绪状态分析结果
   */
  analyzeEmotionalState: async (request: EmotionalStateRequest): Promise<EmotionalStateResponse> => {
    try {
      const response = await soerClient.post('/api/v1/soer/emotional-analysis', request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || '分析情绪状态失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 获取睡眠建议
   * @param request 睡眠请求数据
   * @returns 睡眠建议
   */
  getSleepRecommendations: async (request: SleepRequest): Promise<SleepResponse> => {
    try {
      const response = await soerClient.post('/api/v1/soer/sleep-analysis', request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || '获取睡眠建议失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },

  /**
   * 智能体健康检查
   * @returns 健康状态
   */
  healthCheck: async (): Promise<{ status: string; service: string; version: string }> => {
    try {
      const response = await soerClient.get('/health');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.detail || '健康检查失败，请稍后再试';
        throw new Error(message);
      }
      throw error;
    }
  },
};

export default soerApi; 