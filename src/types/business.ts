// 商业化模式类型定义
export interface SubscriptionTier {
  id: string;
  name: string;
  level: 'basic' | 'premium' | 'professional' | 'enterprise';
  price: {
    monthly: number;
    yearly: number;
    discount?: number;
  };
  features: SubscriptionFeature[];
  limits: ServiceLimits;
  aiCapabilities: AICapabilities;
  priority: number;
}

export interface SubscriptionFeature {
  id: string;
  name: string;
  description: string;
  category: 'ai' | 'health' | 'community' | 'data' | 'support';
  enabled: boolean;
  usage?: {
    limit: number;
    period: 'daily' | 'monthly' | 'yearly';
  };
}

export interface ServiceLimits {
  aiConsultations: number; // 每月AI咨询次数
  expertConsultations: number; // 专家咨询次数
  healthReports: number; // 健康报告生成
  dataStorage: number; // 数据存储GB
  familyMembers: number; // 家庭成员数量
  communityPosts: number; // 社区发帖数
}

export interface AICapabilities {
  multimodalAnalysis: boolean; // 多模态分析
  emotionComputing: boolean; // 情感计算
  personalizedRecommendations: boolean; // 个性化推荐
  predictiveHealth: boolean; // 预测性健康分析
  realTimeMonitoring: boolean; // 实时监控
  advancedDiagnostics: boolean; // 高级诊断
}

// B端合作模式
export interface BPartnerType {
  id: string;
  type: 'hospital' | 'clinic' | 'checkup_center' | 'pharmacy' | 'insurance' | 'wellness_center';
  name: string;
  description: string;
  services: BPartnerService[];
  integrationLevel: 'basic' | 'standard' | 'premium' | 'enterprise';
  revenue: RevenueModel;
}

export interface BPartnerService {
  id: string;
  name: string;
  category: 'diagnosis' | 'treatment' | 'prevention' | 'monitoring' | 'consultation';
  pricing: ServicePricing;
  availability: ServiceAvailability;
}

export interface ServicePricing {
  model: 'per_use' | 'subscription' | 'revenue_share' | 'fixed_fee';
  basePrice: number;
  revenueShare?: number; // 分成比例
  volume?: VolumeDiscount[];
}

export interface VolumeDiscount {
  minVolume: number;
  discount: number;
}

export interface ServiceAvailability {
  regions: string[];
  timeSlots: TimeSlot[];
  capacity: number;
  waitTime: number; // 预计等待时间（分钟）
}

export interface TimeSlot {
  start: string;
  end: string;
  days: number[]; // 0-6 (周日到周六)
}

// 生态变现模式
export interface EcosystemRevenue {
  id: string;
  category: 'health_products' | 'agricultural_products' | 'knowledge_payment' | 'services';
  products: EcosystemProduct[];
  revenueStreams: RevenueStream[];
}

export interface EcosystemProduct {
  id: string;
  name: string;
  category: string;
  description: string;
  price: ProductPricing;
  supplier: Supplier;
  healthBenefits: string[];
  aiRecommendation: AIRecommendation;
  inventory: InventoryInfo;
}

export interface ProductPricing {
  basePrice: number;
  currency: string;
  discounts: Discount[];
  bundleOffers: BundleOffer[];
}

export interface Discount {
  type: 'subscription' | 'volume' | 'seasonal' | 'first_time' | 'loyalty';
  value: number;
  isPercentage: boolean;
  conditions: string[];
}

export interface BundleOffer {
  id: string;
  name: string;
  products: string[];
  discountPercentage: number;
  validUntil: Date;
}

export interface Supplier {
  id: string;
  name: string;
  type: 'manufacturer' | 'distributor' | 'farmer' | 'expert' | 'institution';
  rating: number;
  certifications: string[];
  location: string;
}

export interface AIRecommendation {
  score: number; // 0-100
  reasons: string[];
  personalizedFor: string[]; // 用户特征
  healthGoals: string[];
  contraindications?: string[];
}

export interface InventoryInfo {
  stock: number;
  reserved: number;
  available: number;
  restockDate?: Date;
  supplier: string;
}

// 收入模式
export interface RevenueModel {
  primary: RevenueStream;
  secondary: RevenueStream[];
  projections: RevenueProjection[];
}

export interface RevenueStream {
  type: 'subscription' | 'commission' | 'advertising' | 'data_licensing' | 'service_fee' | 'product_sales';
  percentage: number;
  description: string;
  growth: GrowthMetrics;
}

export interface RevenueProjection {
  period: 'monthly' | 'quarterly' | 'yearly';
  amount: number;
  growth: number;
  confidence: number; // 0-100
}

export interface GrowthMetrics {
  currentMRR: number; // Monthly Recurring Revenue
  growthRate: number; // 月增长率
  churnRate: number; // 流失率
  ltv: number; // Customer Lifetime Value
  cac: number; // Customer Acquisition Cost
}

// 个性化定价
export interface PersonalizedPricing {
  userId: string;
  basePrice: number;
  adjustments: PriceAdjustment[];
  finalPrice: number;
  validUntil: Date;
  factors: PricingFactor[];
}

export interface PriceAdjustment {
  type: 'discount' | 'premium' | 'loyalty' | 'volume' | 'regional';
  value: number;
  reason: string;
  weight: number;
}

export interface PricingFactor {
  factor: 'usage_history' | 'health_risk' | 'engagement' | 'location' | 'age' | 'income_level';
  value: number;
  impact: number; // -1 to 1
}

// ==================== 支付系统类型定义 ====================

// 支付方式
export type PaymentMethod = 'alipay' | 'wechat' | 'apple_pay' | 'bank_card' | 'balance';

// 支付状态
export type PaymentStatus = 'pending' | 'success' | 'failed' | 'cancelled' | 'refund_processing' | 'refunded' | 'refund_failed';

// 支付请求
export interface PaymentRequest {
  orderId: string;
  amount: number;
  currency: string;
  paymentMethod: PaymentMethod;
  description: string;
  userId: string;
  productId?: string;
  metadata?: Record<string; any>;
}

// 支付结果
export interface PaymentResult {
  success: boolean;
  orderId: string;
  paymentMethod: PaymentMethod;
  status: PaymentStatus;
  paymentUrl?: string;
  paymentData?: any;
  refundId?: string;
  errorMessage?: string;
  timestamp: string;
}

// 支付配置
export interface PaymentConfig {
  alipay: {
    appId: string;
    privateKey: string;
    publicKey: string;
    gatewayUrl: string;
  };
  wechat: {
    appId: string;
    mchId: string;
    apiKey: string;
    notifyUrl: string;
  };
}

// ==================== 物流系统类型定义 ====================

// 物流状态
export type LogisticsStatus = 'pending' | 'picked_up' | 'in_transit' | 'out_for_delivery' | 'delivered' | 'failed' | 'returned';

// 物流公司
export type LogisticsProvider = 'sf_express' | 'ems' | 'yto' | 'sto' | 'zto' | 'yunda' | 'jd_logistics';

// 收货地址
export interface ShippingAddress {
  id: string;
  recipientName: string;
  phone: string;
  province: string;
  city: string;
  district: string;
  detailAddress: string;
  postalCode?: string;
  isDefault: boolean;
}

// 物流信息
export interface LogisticsInfo {
  orderId: string;
  trackingNumber: string;
  provider: LogisticsProvider;
  status: LogisticsStatus;
  shippingAddress: ShippingAddress;
  estimatedDelivery?: string;
  actualDelivery?: string;
  trackingHistory: LogisticsTrackingEvent[];
  cost: number;
}

// 物流跟踪事件
export interface LogisticsTrackingEvent {
  timestamp: string;
  status: LogisticsStatus;
  location: string;
  description: string;
}

// ==================== 数据分析类型定义 ====================

// 用户行为事件
export interface UserBehaviorEvent {
  id: string;
  userId: string;
  eventType: 'page_view' | 'click' | 'purchase' | 'subscription' | 'consultation' | 'product_view' | 'search';
  eventData: Record<string, any>;
  timestamp: string;
  sessionId: string;
  deviceInfo: DeviceInfo;
  location?: LocationInfo;
}

// 设备信息
export interface DeviceInfo {
  platform: 'ios' | 'android' | 'web';
  deviceModel: string;
  osVersion: string;
  appVersion: string;
  screenSize: string;
}

// 位置信息
export interface LocationInfo {
  latitude: number;
  longitude: number;
  city: string;
  province: string;
  country: string;
}

// 用户行为分析结果
export interface UserBehaviorAnalysis {
  userId: string;
  period: string;
  metrics: {
    sessionCount: number;
    avgSessionDuration: number;
    pageViews: number;
    conversionRate: number;
    retentionRate: number;
  };
  preferences: UserPreference[];
  healthGoals: string[];
  engagementScore: number;
}

// 用户偏好
export interface UserPreference {
  category: string;
  items: string[];
  confidence: number;
  lastUpdated: string;
}

// ==================== 合作伙伴扩展类型定义 ====================

// 食农结合产品
export interface AgricultureProduct extends EcosystemProduct {
  farmInfo: FarmInfo;
  seasonality: SeasonInfo;
  nutritionFacts: NutritionInfo;
  organicCertification: boolean;
  traceability: TraceabilityInfo;
}

// 农场信息
export interface FarmInfo {
  farmId: string;
  farmName: string;
  location: string;
  farmSize: number; // 亩
  farmingMethod: 'organic' | 'conventional' | 'sustainable';
  certifications: string[];
  farmerInfo: {
    name: string;
    experience: number; // 年
    specialties: string[];
  };
}

// 季节信息
export interface SeasonInfo {
  plantingSeason: string;
  harvestSeason: string;
  bestConsumptionPeriod: string;
  storageRequirements: string;
}

// 营养信息
export interface NutritionInfo {
  calories: number; // per 100g
  protein: number;
  carbohydrates: number;
  fat: number;
  fiber: number;
  vitamins: Record<string, number>;
  minerals: Record<string, number>;
}

// 溯源信息
export interface TraceabilityInfo {
  batchNumber: string;
  plantingDate: string;
  harvestDate: string;
  processingSteps: ProcessingStep[];
  qualityChecks: QualityCheck[];
}

// 加工步骤
export interface ProcessingStep {
  step: string;
  date: string;
  location: string;
  responsible: string;
}

// 质量检查
export interface QualityCheck {
  checkType: string;
  result: 'pass' | 'fail';
  date: string;
  inspector: string;
  report?: string;
}

// 山水养生产品
export interface WellnessProduct extends Omit<EcosystemProduct, 'healthBenefits'> {
  wellnessType: 'retreat' | 'therapy' | 'meditation' | 'spa' | 'exercise' | 'accommodation';
  location: WellnessLocation;
  duration: string;
  capacity: number;
  seasonality: string[];
  healthBenefits: HealthBenefit[]; // 覆盖基类的string[]类型
  requirements: string[];
}

// 养生地点
export interface WellnessLocation {
  name: string;
  address: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  environment: 'mountain' | 'forest' | 'lake' | 'seaside' | 'hot_spring' | 'temple';
  facilities: string[];
  accessibility: string;
}

// 健康益处
export interface HealthBenefit {
  category: 'physical' | 'mental' | 'spiritual';
  benefit: string;
  evidence: string;
  tcmPrinciple?: string; // 中医原理
}

// ==================== 用户反馈类型定义 ====================

// 用户反馈
export interface UserFeedback {
  id: string;
  userId: string;
  type: 'bug_report' | 'feature_request' | 'improvement' | 'complaint' | 'praise';
  category: 'ui_ux' | 'performance' | 'content' | 'service' | 'product' | 'payment';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  attachments?: string[];
  createdAt: string;
  updatedAt: string;
  assignedTo?: string;
  resolution?: string;
}

// 产品改进建议
export interface ProductImprovement {
  id: string;
  source: 'user_feedback' | 'analytics' | 'expert_review' | 'market_research';
  area: 'functionality' | 'performance' | 'usability' | 'content' | 'design';
  description: string;
  impact: 'low' | 'medium' | 'high';
  effort: 'low' | 'medium' | 'high';
  priority: number; // 1-10
  status: 'proposed' | 'approved' | 'in_development' | 'testing' | 'released';
  metrics: ImprovementMetrics;
}

// 改进指标
export interface ImprovementMetrics {
  userSatisfaction?: number;
  usageIncrease?: number;
  performanceGain?: number;
  errorReduction?: number;
  conversionImprovement?: number;
} 