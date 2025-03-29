/**
 * 代理服务模型
 */

/**
 * 代理状态枚举
 */
export enum AgentStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  BUSY = 'busy',
  MAINTENANCE = 'maintenance'
}

/**
 * 代理实体接口
 */
export interface Agent {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  serviceUrl: string;
  status: AgentStatus;
  metadata: Record<string, any>;
  isDefault?: boolean;
}

/**
 * 代理查询请求接口
 */
export interface AgentQueryRequest {
  message: string;
  sessionId: string;
  userId: string;
  context?: Record<string, any>;
  metadata?: Record<string, any>;
}

/**
 * 代理查询响应接口
 */
export interface AgentQueryResponse {
  content: string;
  metadata?: Record<string, any>;
  suggestions?: string[];
  confidence?: number;
  sourceReferences?: Array<{
    title: string;
    url?: string;
    snippet?: string;
  }>;
  domainClassifications?: Array<{
    domain: string;
    confidence: number;
  }>;
  responseId?: string;
}

/**
 * 代理详细查询响应接口
 */
export interface AgentQueryDetailResponse extends AgentQueryResponse {
  agentId: string;
  sessionId: string;
  timestamp: string;
  processingTime?: number;
  rawResponse?: any;
}

/**
 * 代理健康状态接口
 */
export interface AgentHealthStatus {
  agentId: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  details?: {
    latency?: number;
    errorRate?: number;
    memoryUsage?: number;
    cpuUsage?: number;
    [key: string]: any;
  };
}