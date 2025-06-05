import { apiClient } from './apiClient';

// 数据类型定义
export interface Constitution {
  id: string;
  name: string;
  type: string;
  characteristics: string[];
  description: string;
  recommendations: string[];
  symptoms: string[];
  lifestyle: {
    diet: string[];
    exercise: string[];
    sleep: string[];
    emotion: string[];
  };
  created_at: string;
  updated_at: string;
}

export interface Symptom {
  id: string;
  name: string;
  category: string;
  description: string;
  severity: 'mild' | 'moderate' | 'severe';
  related_constitutions: string[];
  related_syndromes: string[];
  treatments: string[];
  created_at: string;
  updated_at: string;
}

export interface Acupoint {
  id: string;
  name: string;
  chinese_name: string;
  location: string;
  meridian: string;
  functions: string[];
  indications: string[];
  techniques: string[];
  precautions: string[];
  coordinates?: {
    x: number;
    y: number;
    z?: number;
  };
  created_at: string;
  updated_at: string;
}

export interface Herb {
  id: string;
  name: string;
  chinese_name: string;
  latin_name: string;
  category: string;
  properties: {
    nature: string; // 性
    flavor: string; // 味
    meridian: string[]; // 归经
  };
  functions: string[];
  indications: string[];
  dosage: string;
  contraindications: string[];
  interactions: string[];
  created_at: string;
  updated_at: string;
}

export interface Syndrome {
  id: string;
  name: string;
  category: string;
  description: string;
  symptoms: string[];
  tongue_manifestation: string;
  pulse_manifestation: string;
  treatment_principles: string[];
  formulas: string[];
  created_at: string;
  updated_at: string;
}

export interface KnowledgeQuery {
  query: string;
  type: 'symptom' | 'treatment' | 'medicine' | 'general' | 'constitution' | 'acupoint';
  context?: {
    userId?: string;
    symptoms?: string[];
    constitution?: string;
    age?: number;
    gender?: string;
  };
  filters?: {
    category?: string;
    severity?: string;
    meridian?: string;
  };
}

export interface KnowledgeResult {
  id: string;
  title: string;
  content: string;
  type: string;
  relevance: number;
  source: string;
  category: string;
  tags: string[];
  related_items: {
    constitutions?: Constitution[];
    symptoms?: Symptom[];
    acupoints?: Acupoint[];
    herbs?: Herb[];
  };
  last_updated: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  statistics: {
    total_nodes: number;
    total_edges: number;
    node_types: Record<string, number>;
    edge_types: Record<string, number>;
  };
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, any>;
  position?: { x: number; y: number };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  weight?: number;
  properties?: Record<string, any>;
}

export interface RecommendationRequest {
  userId: string;
  constitution_id?: string;
  symptoms?: string[];
  preferences?: {
    treatment_type?: 'traditional' | 'modern' | 'integrated';
    lifestyle_focus?: string[];
  };
}

export interface HealthRecommendation {
  id: string;
  type: 'lifestyle' | 'diet' | 'exercise' | 'treatment' | 'prevention';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  evidence_level: number;
  implementation: {
    frequency: string;
    duration: string;
    instructions: string[];
  };
  contraindications?: string[];
}

// API客户端类
export class MedKnowledgeService {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    this.baseUrl = process.env.NODE_ENV === 'production' 
      ? 'https://api.suokelife.com/med-knowledge/api/v1'
      : 'http://localhost:8007/api/v1';
    this.timeout = 30000;
  }

  // 体质相关API
  async getConstitutions(): Promise<Constitution[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/constitutions`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch constitutions:', error);
      throw new Error('获取体质信息失败');
    }
  }

  async getConstitutionById(id: string): Promise<Constitution> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/constitutions/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch constitution ${id}:`, error);
      throw new Error('获取体质详情失败');
    }
  }

  async getConstitutionRecommendations(constitutionId: string): Promise<HealthRecommendation[]> {
    try {
      const response = await apiClient.get(
        `${this.baseUrl}/recommendations/constitutions/${constitutionId}`
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch constitution recommendations:`, error);
      throw new Error('获取体质建议失败');
    }
  }

  // 症状相关API
  async getSymptoms(): Promise<Symptom[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/symptoms`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch symptoms:', error);
      throw new Error('获取症状信息失败');
    }
  }

  async getSymptomById(id: string): Promise<Symptom> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/symptoms/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch symptom ${id}:`, error);
      throw new Error('获取症状详情失败');
    }
  }

  async searchSymptoms(query: string): Promise<Symptom[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/symptoms?search=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      console.error('Failed to search symptoms:', error);
      throw new Error('搜索症状失败');
    }
  }

  // 穴位相关API
  async getAcupoints(): Promise<Acupoint[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/acupoints`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch acupoints:', error);
      throw new Error('获取穴位信息失败');
    }
  }

  async getAcupointById(id: string): Promise<Acupoint> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/acupoints/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch acupoint ${id}:`, error);
      throw new Error('获取穴位详情失败');
    }
  }

  async getAcupointsByConstitution(constitutionId: string): Promise<Acupoint[]> {
    try {
      const response = await apiClient.get(
        `${this.baseUrl}/acupoints?constitution_id=${encodeURIComponent(constitutionId)}`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to fetch acupoints by constitution:', error);
      throw new Error('获取体质相关穴位失败');
    }
  }

  // 中药相关API
  async getHerbs(): Promise<Herb[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/herbs`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch herbs:', error);
      throw new Error('获取中药信息失败');
    }
  }

  async getHerbById(id: string): Promise<Herb> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/herbs/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch herb ${id}:`, error);
      throw new Error('获取中药详情失败');
    }
  }

  async getHerbsBySymptom(symptomId: string): Promise<Herb[]> {
    try {
      const response = await apiClient.get(
        `${this.baseUrl}/herbs?symptom_id=${encodeURIComponent(symptomId)}`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to fetch herbs by symptom:', error);
      throw new Error('获取症状相关中药失败');
    }
  }

  // 证型相关API
  async getSyndromes(): Promise<Syndrome[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/syndromes`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch syndromes:', error);
      throw new Error('获取证型信息失败');
    }
  }

  async getSyndromeById(id: string): Promise<Syndrome> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/syndromes/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch syndrome ${id}:`, error);
      throw new Error('获取证型详情失败');
    }
  }

  // 知识搜索API
  async searchKnowledge(query: KnowledgeQuery): Promise<KnowledgeResult[]> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/search`, query);
      return response.data;
    } catch (error) {
      console.error('Failed to search knowledge:', error);
      throw new Error('知识搜索失败');
    }
  }

  async getRecommendedKnowledge(userId: string, context?: any): Promise<KnowledgeResult[]> {
    try {
      const contextParam = context ? `?context=${encodeURIComponent(JSON.stringify(context))}` : '';
      const response = await apiClient.get(
        `${this.baseUrl}/knowledge/recommendations/${userId}${contextParam}`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to get recommended knowledge:', error);
      throw new Error('获取推荐知识失败');
    }
  }

  // 知识图谱API
  async getKnowledgeGraph(): Promise<GraphData> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/graph/visualization`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch knowledge graph:', error);
      throw new Error('获取知识图谱失败');
    }
  }

  async getGraphStatistics(): Promise<any> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/graph/statistics`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch graph statistics:', error);
      throw new Error('获取图谱统计失败');
    }
  }

  async getEntityRelationships(entityType: string, entityId: string): Promise<any> {
    try {
      const response = await apiClient.get(
        `${this.baseUrl}/graph/entities/${entityType}/${entityId}/relationships`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to fetch entity relationships:', error);
      throw new Error('获取实体关系失败');
    }
  }

  async getEntityNeighbors(entityType: string, entityId: string): Promise<any> {
    try {
      const response = await apiClient.get(
        `${this.baseUrl}/graph/entities/${entityType}/${entityId}/neighbors`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to fetch entity neighbors:', error);
      throw new Error('获取相邻实体失败');
    }
  }

  async findGraphPaths(fromId: string, toId: string): Promise<any> {
    try {
      const response = await apiClient.get(
        `${this.baseUrl}/graph/paths?from=${encodeURIComponent(fromId)}&to=${encodeURIComponent(toId)}`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to find graph paths:', error);
      throw new Error('查找图谱路径失败');
    }
  }

  // 个性化推荐API
  async getPersonalizedRecommendations(request: RecommendationRequest): Promise<HealthRecommendation[]> {
    try {
      const response = await apiClient.post(`${this.baseUrl}/recommendations`, request);
      return response.data;
    } catch (error) {
      console.error('Failed to get personalized recommendations:', error);
      throw new Error('获取个性化推荐失败');
    }
  }

  // 健康检查API
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/health`);
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw new Error('服务健康检查失败');
    }
  }
}

// 导出单例实例
export const medKnowledgeService = new MedKnowledgeService(); 