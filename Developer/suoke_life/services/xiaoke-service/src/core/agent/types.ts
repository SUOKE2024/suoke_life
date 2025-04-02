/**
 * 智能体配置类型
 */
export interface AgentConfig {
  agent: {
    name: string;
    id: string;
    version: string;
    description: string;
    avatar: string;
    greeting: string;
    capabilities: string[];
    priority: string;
    visibility: string;
    role: string;
    specializations: string[];
  };
  models: {
    primary: ModelConfig;
    embedding: ModelConfig;
    product_analyzer?: ModelConfig;
    traceability_analyzer?: ModelConfig;
    multimodal_processor?: ModelConfig;
    enhanced_multimodal?: {
      vision_analyzer?: ModelConfig;
      audio_analyzer?: ModelConfig;
      multimodal_integration?: {
        cross_modal_verification: boolean;
        confidence_boosting: boolean;
        contradiction_detection: boolean;
        fusion_methods: string[];
        active_fusion_method: string;
        modality_weighting: Record<string, number>;
        output_formats: Record<string, boolean>;
      };
    };
  };
  tools: {
    enabled: boolean;
    list: ToolConfig[];
  };
}

/**
 * 模型配置类型
 */
export interface ModelConfig {
  id: string;
  type: string;
  path: string;
  config: Record<string, any>;
}

/**
 * 工具配置类型
 */
export interface ToolConfig {
  name: string;
  description: string;
  parameters: ToolParameter[];
}

/**
 * 工具参数类型
 */
export interface ToolParameter {
  name: string;
  type: string;
  description: string;
  required: boolean;
}

/**
 * 智能体能力类型
 */
export interface AgentCapability {
  name: string;
  description: string;
}

/**
 * 智能体运行状态
 */
export enum AgentStatus {
  INITIALIZING = 'initializing',
  READY = 'ready',
  BUSY = 'busy',
  ERROR = 'error',
  PAUSED = 'paused',
  TERMINATED = 'terminated'
}

/**
 * 智能体响应类型
 */
export interface AgentResponse {
  messageId: string;
  content: string;
  timestamp: string;
  metadata?: {
    tool?: string;
    confidence?: number;
    processingTime?: number;
    references?: string[];
    [key: string]: any;
  };
}

/**
 * 智能体请求类型
 */
export interface AgentRequest {
  messageId: string;
  content: string;
  timestamp: string;
  userId?: string;
  metadata?: {
    context?: string;
    history?: AgentMessage[];
    [key: string]: any;
  };
}

/**
 * 智能体消息类型
 */
export interface AgentMessage {
  id: string;
  role: 'user' | 'agent' | 'system';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

/**
 * 工具调用结果类型
 */
export interface ToolCallResult {
  success: boolean;
  data?: any;
  error?: string;
  toolName: string;
  executionTime: number;
}

/**
 * 产品信息类型
 */
export interface ProductInfo {
  id: string;
  name: string;
  description: string;
  category: string;
  price: number;
  unit: string;
  stock: number;
  images: string[];
  producer: {
    id: string;
    name: string;
    location: string;
    contact: string;
  };
  certifications: string[];
  nutritionFacts: Record<string, any>;
  tcmProperties?: {
    nature?: string;
    taste?: string[];
    meridians?: string[];
    effects?: string[];
  };
  harvestDate?: string;
  expiryDate?: string;
  storageConditions?: string;
  seasonality?: {
    peak: string[];
    available: string[];
  };
  traceabilityId?: string;
  blockchainVerified?: boolean;
  metadata?: Record<string, any>;
}

/**
 * 溯源记录类型
 */
export interface TraceabilityRecord {
  id: string;
  productId: string;
  productName: string;
  stages: TraceabilityStage[];
  verificationMethod: string;
  blockchainTxId?: string;
  verifiedAt: string;
  completeness: number;
}

/**
 * 溯源阶段类型
 */
export interface TraceabilityStage {
  name: string;
  location: string;
  timestamp: string;
  description: string;
  handledBy: string;
  evidence?: {
    images?: string[];
    documents?: string[];
    certifications?: string[];
  };
  metadata?: Record<string, any>;
}

/**
 * 订单类型
 */
export interface Order {
  id: string;
  userId: string;
  items: OrderItem[];
  status: string;
  totalPrice: number;
  createdAt: string;
  updatedAt: string;
  paymentMethod?: string;
  paymentStatus?: string;
  deliveryAddress?: string;
  deliveryDate?: string;
  deliveryStatus?: string;
  notes?: string;
  metadata?: Record<string, any>;
}

/**
 * 订单项类型
 */
export interface OrderItem {
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
}

/**
 * 订阅服务类型
 */
export interface Subscription {
  id: string;
  userId: string;
  serviceName: string;
  serviceType: string;
  status: string;
  startDate: string;
  endDate: string;
  price: number;
  billingCycle: string;
  autoRenew: boolean;
  details: Record<string, any>;
  metadata?: Record<string, any>;
}

/**
 * 活动评价类型
 */
export interface ActivityReview {
  userId: string;        // 用户ID
  rating: number;        // 评分（1-5）
  comment: string;       // 评论内容
  date: string;          // 评价日期（ISO字符串）
  photoUrls?: string[];  // 图片链接（可选）
}

/**
 * 农场活动类型
 */
export interface FarmActivity {
  id: string;                    // 活动ID
  name: string;                  // 活动名称
  description: string;           // 活动描述
  location: string;              // 活动地点
  startDate: string;             // 开始日期（ISO字符串）
  endDate: string;               // 结束日期（ISO字符串）
  capacity: number;              // 最大容量
  currentRegistrations: number;  // 当前注册人数
  price: number;                 // 价格（CNY）
  category: string;              // 活动类别
  organizer: string;             // 组织者
  contactInfo: string;           // 联系信息
  images: string[];              // 图片链接
  requirements?: string;         // 参与要求（可选）
  included?: string;             // 包含项目（可选）
  reviews: ActivityReview[];     // 活动评价
  metadata?: Record<string, any>; // 元数据（可选）
}