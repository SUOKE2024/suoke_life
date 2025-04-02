/**
 * 供应链事件类型
 */
export type SupplyChainEventType = 
  | 'production_started'
  | 'production_completed'
  | 'quality_check'
  | 'quality_issue'
  | 'packaging_started'
  | 'packaging_completed'
  | 'shipment_started'
  | 'shipment_completed'
  | 'delivery_started'
  | 'delivery_completed'
  | 'delay'
  | 'low_inventory'
  | 'stock_replenished'
  | 'certification_updated'
  | 'traceability_verified';

/**
 * 供应链事件
 */
export interface SupplyChainEvent {
  id: string;
  productId: string;
  type: SupplyChainEventType;
  timestamp: string;
  location?: string;
  description: string;
  metadata?: Record<string, any>;
}

/**
 * 供应链阶段
 */
export interface SupplyChainStage {
  id: string;
  name: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'delayed' | 'error';
  startTime?: string;
  endTime?: string;
  location?: string;
  responsibleParty?: string;
  notes?: string;
  metadata?: Record<string, any>;
}

/**
 * 供应链状态
 */
export interface SupplyChainStatus {
  productId: string;
  productName: string;
  currentStage: string;
  progress: number; // 0-100
  stages: SupplyChainStage[];
  lastUpdated: string;
  estimatedCompletion: string;
  metadata?: Record<string, any>;
}

/**
 * 供应链分析
 */
export interface SupplyChainAnalysis {
  productId: string;
  insights: {
    efficiencyScore: number; // 0-100
    bottlenecks: string[];
    recommendations: string[];
    keyMetrics: Record<string, number>;
  };
  riskAssessment: {
    overallRisk: 'low' | 'medium' | 'high';
    factors: Array<{
      name: string;
      risk: 'low' | 'medium' | 'high';
      description: string;
    }>;
  };
  comparisonWithAverage: Record<string, {
    value: number;
    average: number;
    difference: number;
  }>;
  timestamp: string;
}

/**
 * 供应链预警
 */
export interface SupplyChainAlert {
  id?: string;
  level: 'info' | 'warning' | 'critical';
  message: string;
  details: any;
  timestamp: string;
  acknowledged?: boolean;
  acknowledgedBy?: string;
  acknowledgedAt?: string;
  resolvedAt?: string;
}

/**
 * 供应链可视化数据
 */
export interface SupplyChainVisualizationData {
  nodes: Array<{
    id: string;
    name: string;
    status: string;
    type: string;
    position: {
      x: number;
      y: number;
    };
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    status: string;
  }>;
  metadata: {
    productId: string;
    productName: string;
    currentStage: string;
    estimatedCompletion: string;
    lastUpdated: string;
  };
} 