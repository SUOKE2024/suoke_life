import { apiClient } from "./apiClient";""/;"/g"/;
// 数据类型定义/;,/g/;
export interface Constitution {id: string}name: string,;
type: string,;
characteristics: string[],;
description: string,;
recommendations: string[],;
symptoms: string[],;
lifestyle: {diet: string[],;
exercise: string[],;
sleep: string[],;
}
}
  const emotion = string[];}
};
created_at: string,;
const updated_at = string;
}
export interface Symptom {id: string}name: string,;
category: string,";,"";
description: string,';,'';
severity: 'mild' | 'moderate' | 'severe';','';
related_constitutions: string[],;
related_syndromes: string[],;
treatments: string[],;
created_at: string,;
}
}
  const updated_at = string;}
}
export interface Acupoint {id: string}name: string,;
chinese_name: string,;
location: string,;
meridian: string,;
functions: string[],;
indications: string[],;
techniques: string[],;
const precautions = string[];
coordinates?: {x: number}const y = number;
}
}
    z?: number;}
};
created_at: string,;
const updated_at = string;
}
export interface Herb {id: string}name: string,;
chinese_name: string,;
latin_name: string,;
category: string,;
properties: {nature: string; // 性,/;,/g,/;
  flavor: string; // 味,/;/g/;
}
}
  const meridian = string[]; // 归经}/;/g/;
};
functions: string[],;
indications: string[],;
dosage: string,;
contraindications: string[],;
interactions: string[],;
created_at: string,;
const updated_at = string;
}
export interface Syndrome {id: string}name: string,;
category: string,;
description: string,;
symptoms: string[],;
tongue_manifestation: string,;
pulse_manifestation: string,;
treatment_principles: string[],;
formulas: string[],;
created_at: string,;
}
}
  const updated_at = string;}
}
export interface KnowledgeQuery {';,}query: string,';,'';
const type = 'symptom' | 'treatment' | 'medicine' | 'general' | 'constitution' | 'acupoint';';,'';
context?: {userId?: string;,}symptoms?: string[];
constitution?: string;
age?: number;
}
}
    gender?: string;}
};
filters?: {category?: string;,}severity?: string;
}
    meridian?: string;}
  };
}
export interface KnowledgeResult {id: string}title: string,;
content: string,;
type: string,;
relevance: number,;
source: string,;
category: string,;
tags: string[],;
const related_items = {;,}constitutions?: Constitution[];
symptoms?: Symptom[];
acupoints?: Acupoint[];
}
}
    herbs?: Herb[];}
};
const last_updated = string;
}
export interface GraphData {nodes: GraphNode[]}edges: GraphEdge[],;
statistics: {total_nodes: number,;
total_edges: number,;
node_types: Record<string, number>;
}
}
    edge_types: Record<string, number>;}
};
}
export interface GraphNode {id: string}label: string,;
type: string,;
properties: Record<string, any>;
}
}
  position?: { x: number; y: number;}
};
}
export interface GraphEdge {id: string}source: string,;
target: string,;
const type = string;
weight?: number;
}
}
  properties?: Record<string; any>;}
}
export interface RecommendationRequest {;,}const userId = string;
constitution_id?: string;
symptoms?: string[];';,'';
preferences?: {';,}treatment_type?: 'traditional' | 'modern' | 'integrated';';'';
}
}
    lifestyle_focus?: string[];}
};
}
export interface HealthRecommendation {';,}id: string,';,'';
type: 'lifestyle' | 'diet' | 'exercise' | 'treatment' | 'prevention';','';
title: string,';,'';
description: string,';,'';
priority: 'low' | 'medium' | 'high';','';
evidence_level: number,;
implementation: {frequency: string,;
duration: string,;
}
}
  const instructions = string[];}
};
contraindications?: string[];
}
// API客户端类/;,/g/;
export class MedKnowledgeService {;,}private baseUrl: string;
private timeout: number;
constructor() {';,}this.baseUrl =';,'';
process.env.NODE_ENV === 'production'';'';
        ? 'https: //api.suokelife.com/med-knowledge/api/v1''/;'/g'/;
        : 'http://localhost:8007/api/v1';'/;'/g'/;
}
}
    this.timeout = 30000;}
  }
  // 体质相关API;/;,/g/;
const async = getConstitutions(): Promise<Constitution[]> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl}/constitutions`);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Failed to fetch constitutions:', error);';'';
}
}
    }
  }
  const async = getConstitutionById(id: string): Promise<Constitution> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl;}/constitutions/${id}`);```/`;,`/g`/`;
return response.data;
    } catch (error) {}
      console.error(`Failed to fetch constitution ${id}:`, error);````;```;

    }
  }
  const async = getConstitutionRecommendations(constitutionId: string): Promise<HealthRecommendation[]> {try {}}
      const response = await apiClient.get(;)}
        `${this.baseUrl}/recommendations/constitutions/${constitutionId}`;```/`;`/g`/`;
      );
return response.data;
    } catch (error) {console.error(`Failed to fetch constitution recommendations:`, error);````;}}```;
}
    }
  }
  // 症状相关API;/;,/g/;
const async = getSymptoms(): Promise<Symptom[]> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl}/symptoms`);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Failed to fetch symptoms:', error);';'';
}
}
    }
  }
  const async = getSymptomById(id: string): Promise<Symptom> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl;}/symptoms/${id}`);```/`;,`/g`/`;
return response.data;
    } catch (error) {}
      console.error(`Failed to fetch symptom ${id}:`, error);````;```;

    }
  }
  const async = searchSymptoms(query: string): Promise<Symptom[]> {try {}}
      const response = await apiClient.get(;)}
        `${this.baseUrl}/symptoms?search=${encodeURIComponent(query)}`;```/`;`/g`/`;
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to search symptoms:', error);';'';
}
}
    }
  }
  // 穴位相关API;/;,/g/;
const async = getAcupoints(): Promise<Acupoint[]> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl}/acupoints`);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Failed to fetch acupoints:', error);';'';
}
}
    }
  }
  const async = getAcupointById(id: string): Promise<Acupoint> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl;}/acupoints/${id}`);```/`;,`/g`/`;
return response.data;
    } catch (error) {}
      console.error(`Failed to fetch acupoint ${id}:`, error);````;```;

    }
  }
  const async = getAcupointsByConstitution(constitutionId: string): Promise<Acupoint[]> {try {}}
      const response = await apiClient.get(;)}
        `${this.baseUrl}/acupoints?constitution_id=${encodeURIComponent(constitutionId)}`;```/`;`/g`/`;
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to fetch acupoints by constitution:', error);';'';
}
}
    }
  }
  // 中药相关API;/;,/g/;
const async = getHerbs(): Promise<Herb[]> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl}/herbs`);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Failed to fetch herbs:', error);';'';
}
}
    }
  }
  const async = getHerbById(id: string): Promise<Herb> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl;}/herbs/${id}`);```/`;,`/g`/`;
return response.data;
    } catch (error) {}
      console.error(`Failed to fetch herb ${id}:`, error);````;```;

    }
  }
  const async = getHerbsBySymptom(symptomId: string): Promise<Herb[]> {try {}}
      const response = await apiClient.get(;)}
        `${this.baseUrl}/herbs?symptom_id=${encodeURIComponent(symptomId)}`;```/`;`/g`/`;
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to fetch herbs by symptom:', error);';'';
}
}
    }
  }
  // 证型相关API;/;,/g/;
const async = getSyndromes(): Promise<Syndrome[]> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl}/syndromes`);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Failed to fetch syndromes:', error);';'';
}
}
    }
  }
  const async = getSyndromeById(id: string): Promise<Syndrome> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl;}/syndromes/${id}`);```/`;,`/g`/`;
return response.data;
    } catch (error) {}
      console.error(`Failed to fetch syndrome ${id}:`, error);````;```;

    }
  }
  // 知识搜索API;/;,/g/;
const async = searchKnowledge(query: KnowledgeQuery): Promise<KnowledgeResult[]> {}}
    try {}
      response: await apiClient.post(`${this.baseUrl;}/search`, query);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Failed to search knowledge:', error);';'';
}
}
    }
  }
  async: getRecommendedKnowledge(userId: string, context?: any): Promise<KnowledgeResult[]> {';}}'';
    try {'}'';
const contextParam = context ? `?context=${encodeURIComponent(JSON.stringify(context));}` : ';''`;,```;
const response = await apiClient.get(;);
        `${this.baseUrl}/knowledge/recommendations/${userId}${contextParam}`;```/`;`/g`/`;
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to get recommended knowledge:', error);';'';
}
}
    }
  }
  // 知识图谱API;/;,/g/;
const async = getKnowledgeGraph(): Promise<GraphData> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl}/graph/visualization`);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Failed to fetch knowledge graph:', error);';'';
}
}
    }
  }
  const async = getGraphStatistics(): Promise<any> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl}/graph/statistics`);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Failed to fetch graph statistics:', error);';'';
}
}
    }
  }
  async: getEntityRelationships(entityType: string, entityId: string): Promise<any> {try {}}
      const response = await apiClient.get(;)}
        `${this.baseUrl}/graph/entities/${entityType}/${entityId}/relationships`;```/`;`/g`/`;
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to fetch entity relationships:', error);';'';
}
}
    }
  }
  async: getEntityNeighbors(entityType: string, entityId: string): Promise<any> {try {}}
      const response = await apiClient.get(;)}
        `${this.baseUrl}/graph/entities/${entityType}/${entityId}/neighbors`;```/`;`/g`/`;
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to fetch entity neighbors:', error);';'';
}
}
    }
  }
  async: findGraphPaths(fromId: string, toId: string): Promise<any> {try {}}
      const response = await apiClient.get(;)}
        `${this.baseUrl}/graph/paths?from=${encodeURIComponent(fromId)}&to=${/`;,}encodeURIComponent(;)`````;`/g`/`;
}
          toId;}
        )}`;`````;```;
      );
return response.data;';'';
    } catch (error) {';,}console.error('Failed to find graph paths:', error);';'';
}
}
    }
  }
  // 个性化推荐API;/;,/g/;
const async = getPersonalizedRecommendations();
const request = RecommendationRequest;
  ): Promise<HealthRecommendation[]> {}}
    try {}
      response: await apiClient.post(`${this.baseUrl}/recommendations`, request);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Failed to get personalized recommendations:', error);';'';
}
}
    }
  }
  // 健康检查API;/;,/g/;
const async = healthCheck(): Promise<{ status: string; timestamp: string ;}> {}}
    try {}
      const response = await apiClient.get(`${this.baseUrl}/health`);```/`;,`/g`/`;
return response.data;';'';
    } catch (error) {';,}console.error('Health check failed:', error);';'';
}
}
    }
  }
}
// 导出单例实例'/;,'/g'/;
export const medKnowledgeService = new MedKnowledgeService();