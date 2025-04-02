/**
 * 供应链事件类型定义
 */
export type SupplyChainEventType = 
  // 生产阶段
  | 'production_started'
  | 'production_completed'
  | 'production_paused'
  | 'production_resumed'
  
  // 质检阶段
  | 'quality_check_started'
  | 'quality_check_passed'
  | 'quality_check_failed'
  
  // 包装阶段
  | 'packaging_started'
  | 'packaging_completed'
  
  // 运输阶段
  | 'shipment_started'
  | 'shipment_completed'
  | 'shipment_delayed'
  
  // 仓储阶段
  | 'storage_in'
  | 'storage_out'
  | 'inventory_checked'
  | 'low_inventory'
  | 'stock_replenished'
  
  // 交付阶段
  | 'delivery_started'
  | 'delivery_completed'
  | 'delivered'
  | 'delivery_failed'
  | 'returned'
  
  // 问题类型
  | 'quality_issue'
  | 'delay'
  | 'damage'
  
  // 认证与合规
  | 'certification_updated'
  | 'compliance_check'
  | 'traceability_verified'
  
  // 其他
  | 'custom';

/**
 * 供应链事件接口
 */
export interface SupplyChainEvent {
  /**
   * 事件ID
   */
  id?: string;
  
  /**
   * 产品ID
   */
  productId: string;
  
  /**
   * 事件类型
   */
  type: SupplyChainEventType;
  
  /**
   * 事件描述
   */
  description: string;
  
  /**
   * 事件时间戳
   */
  timestamp: string;
  
  /**
   * 事件位置
   */
  location?: string;
  
  /**
   * 操作人员ID
   */
  operatorId?: string;
  
  /**
   * 额外数据
   */
  metadata?: Record<string, any>;
}

/**
 * 供应链阶段定义
 */
export type SupplyChainStage = 
  | 'production'  // 生产
  | 'quality'     // 质检
  | 'packaging'   // 包装
  | 'storage'     // 仓储
  | 'shipment'    // 运输
  | 'delivery'    // 配送
  | 'completed';  // 完成

/**
 * 供应链状态接口
 */
export interface SupplyChainStatus {
  /**
   * 产品ID
   */
  productId: string;
  
  /**
   * 产品名称
   */
  productName: string;
  
  /**
   * 当前供应链阶段
   */
  currentStage: SupplyChainStage;
  
  /**
   * 当前进度百分比 (0-100)
   */
  progress: number;
  
  /**
   * 各阶段状态
   */
  stages: {
    /**
     * 阶段名称
     */
    name: SupplyChainStage;
    
    /**
     * 阶段状态
     */
    status: 'pending' | 'in_progress' | 'completed' | 'skipped' | 'failed';
    
    /**
     * 开始时间
     */
    startTime?: string;
    
    /**
     * 结束时间
     */
    endTime?: string;
    
    /**
     * 耗时（毫秒）
     */
    duration?: number;
  }[];
  
  /**
   * 最后更新时间
   */
  lastUpdateTime: string;
  
  /**
   * 预计完成时间
   */
  estimatedCompletionTime?: string;
  
  /**
   * 是否有质量问题
   */
  hasQualityIssues: boolean;
  
  /**
   * 是否有延迟
   */
  hasDelays: boolean;
  
  /**
   * 元数据
   */
  metadata?: Record<string, any>;
}

/**
 * 供应链分析接口
 */
export interface SupplyChainAnalysis {
  /**
   * 产品ID
   */
  productId: string;
  
  /**
   * 时间指标
   */
  timeMetrics: {
    /**
     * 生产时间（毫秒）
     */
    productionTime: number;
    
    /**
     * 包装时间（毫秒）
     */
    packagingTime: number;
    
    /**
     * 运输时间（毫秒）
     */
    shipmentTime: number;
    
    /**
     * 配送时间（毫秒）
     */
    deliveryTime: number;
    
    /**
     * 总时间（毫秒）
     */
    totalTime: number;
  };
  
  /**
   * 效率评分（0-100）
   */
  efficiencyScore: number;
  
  /**
   * 瓶颈环节
   */
  bottlenecks: {
    /**
     * 阶段名称
     */
    stage: SupplyChainStage;
    
    /**
     * 原因
     */
    reason: string;
    
    /**
     * 严重程度（0-100）
     */
    severity: number;
  }[];
  
  /**
   * 改进建议
   */
  recommendations: {
    /**
     * 阶段名称
     */
    stage: SupplyChainStage;
    
    /**
     * 建议内容
     */
    suggestion: string;
    
    /**
     * 预期改进（百分比）
     */
    expectedImprovement: number;
  }[];
  
  /**
   * 风险评估
   */
  risks: {
    /**
     * 风险类型
     */
    type: string;
    
    /**
     * 风险描述
     */
    description: string;
    
    /**
     * 风险级别（低、中、高）
     */
    level: 'low' | 'medium' | 'high';
    
    /**
     * 缓解策略
     */
    mitigationStrategy?: string;
  }[];
  
  /**
   * 与行业平均水平比较
   */
  industryComparison: {
    /**
     * 指标名称
     */
    metric: string;
    
    /**
     * 当前值
     */
    value: number;
    
    /**
     * 行业平均值
     */
    industryAverage: number;
    
    /**
     * 差异百分比
     */
    difference: number;
  }[];
  
  /**
   * 质量问题率
   */
  qualityIssueRate: number;
  
  /**
   * 延迟率
   */
  delayRate: number;
  
  /**
   * 分析时间戳
   */
  timestamp: string;
}

/**
 * 供应链预警级别
 */
export type SupplyChainAlertLevel = 'info' | 'warning' | 'critical';

/**
 * 供应链预警状态
 */
export type SupplyChainAlertStatus = 'pending' | 'acknowledged' | 'resolved';

/**
 * 供应链预警接口
 */
export interface SupplyChainAlert {
  /**
   * 预警ID
   */
  id?: string;
  
  /**
   * 预警标题
   */
  title: string;
  
  /**
   * 预警内容
   */
  message: string;
  
  /**
   * 预警级别
   */
  level: SupplyChainAlertLevel;
  
  /**
   * 预警状态
   */
  status?: SupplyChainAlertStatus;
  
  /**
   * 关联产品ID
   */
  productId?: string;
  
  /**
   * 关联事件ID
   */
  eventId?: string;
  
  /**
   * 预警时间戳
   */
  timestamp: string;
  
  /**
   * 确认用户ID
   */
  acknowledgedBy?: string;
  
  /**
   * 确认时间
   */
  acknowledgedAt?: string;
  
  /**
   * 解决时间
   */
  resolvedAt?: string;
  
  /**
   * 元数据
   */
  metadata?: Record<string, any>;
} 