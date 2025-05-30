/**
 * 小克智能体类型定义
 * SUOKE频道版主，负责服务订阅、农产品预制、供应链管理等商业化服务
 */

// 基础数据类型
export interface UserProfile {
  id: string;
  basicInfo: BasicUserInfo;
  healthProfile: HealthProfile;
  preferences: UserPreferences;
  membershipLevel: 'basic' | 'premium' | 'vip' | 'enterprise';
  subscriptions: ServiceSubscription[];
  paymentMethods: PaymentMethod[];
  deliveryAddresses: DeliveryAddress[];
  loyaltyPoints: number;
  referralCode?: string;
}

export interface BasicUserInfo {
  name: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  location: Location;
  timezone: string;
  language: string;
  contactInfo: ContactInfo;
}

export interface HealthProfile {
  constitution: ConstitutionType;
  chronicConditions: string[];
  allergies: string[];
  medications: Medication[];
  dietaryRestrictions: string[];
  healthGoals: HealthGoal[];
  riskFactors: RiskFactor[];
  preferredTreatmentTypes: ('tcm' | 'western' | 'integrative')[];
}

export interface UserPreferences {
  communicationStyle: 'formal' | 'casual' | 'professional';
  language: string;
  currency: string;
  notifications: NotificationPreferences;
  privacy: PrivacySettings;
  servicePreferences: ServicePreferences;
  productPreferences: ProductPreferences;
}

// 服务相关类型
export interface ServiceContext {
  userId: string;
  sessionId: string;
  type: 'service_inquiry' | 'doctor_matching' | 'product_search' | 'appointment' | 'subscription' | 'general';
  category?: ServiceCategory;
  urgency: 'low' | 'medium' | 'high' | 'urgent';
  budget?: BudgetRange;
  location?: Location;
  timeframe?: TimeFrame;
  healthContext?: HealthContext;
  previousInteractions: InteractionHistory[];
  currentNeed?: string;
}

export interface ServiceRecommendation {
  id: string;
  name: string;
  category: ServiceCategory;
  subcategory?: string;
  description: string;
  detailedDescription: string;
  price: PricingInfo;
  provider: ServiceProvider;
  availability: AvailabilityInfo;
  matchScore: number; // 0-100
  benefits: string[];
  features: ServiceFeature[];
  requirements: string[];
  contraindications?: string[];
  estimatedDuration: string;
  location: ServiceLocation;
  reviews: Review[];
  certifications: Certification[];
  insuranceCoverage?: InsuranceCoverage;
  customizationOptions?: CustomizationOption[];
}

// 名医资源相关类型
export interface DoctorProfile {
  id: string;
  personalInfo: DoctorPersonalInfo;
  professionalInfo: DoctorProfessionalInfo;
  specialties: MedicalSpecialty[];
  availability: DoctorAvailability;
  consultationTypes: ConsultationType[];
  pricing: ConsultationPricing;
  location: DoctorLocation;
  reviews: DoctorReview[];
  achievements: Achievement[];
  publications: Publication[];
  languages: string[];
  tcmSpecialties?: TCMSpecialty[];
  matchingAlgorithmData: DoctorMatchingData;
}

export interface DoctorMatchingResult {
  doctor: DoctorProfile;
  matchScore: number; // 0-100
  matchingFactors: MatchingFactor[];
  recommendationReason: string;
  estimatedWaitTime: string;
  nextAvailableSlot: Date;
  consultationOptions: ConsultationOption[];
  estimatedCost: CostEstimate;
  patientFeedbackPrediction: FeedbackPrediction;
}

export interface AppointmentBooking {
  id: string;
  doctorId: string;
  patientId: string;
  appointmentType: AppointmentType;
  scheduledTime: Date;
  duration: number; // minutes
  status: AppointmentStatus;
  consultationType: ConsultationType;
  location: AppointmentLocation;
  notes: string;
  symptoms: string[];
  urgency: 'routine' | 'urgent' | 'emergency';
  paymentInfo: PaymentInfo;
  reminders: ReminderSettings[];
  followUpRequired: boolean;
  cancellationPolicy: CancellationPolicy;
  createdAt: Date;
  updatedAt: Date;
}

// 农产品相关类型
export interface AgriculturalProduct {
  id: string;
  basicInfo: ProductBasicInfo;
  nutritionInfo: NutritionInfo;
  healthBenefits: HealthBenefit[];
  tcmProperties?: TCMProductProperties;
  origin: ProductOrigin;
  cultivation: CultivationInfo;
  certifications: ProductCertification[];
  supplyChain: SupplyChainInfo;
  pricing: ProductPricing;
  availability: ProductAvailability;
  customization: CustomizationOptions;
  reviews: ProductReview[];
  sustainability: SustainabilityMetrics;
  traceability: TraceabilityInfo;
}

export interface SupplyChainInfo {
  id: string;
  productId: string;
  stages: SupplyChainStage[];
  blockchainHash: string;
  verificationStatus: 'verified' | 'pending' | 'failed' | 'disputed';
  traceabilityScore: number; // 0-100
  transparencyLevel: 'basic' | 'detailed' | 'comprehensive';
  certificationChain: CertificationChain[];
  qualityCheckpoints: QualityCheckpoint[];
  sustainabilityMetrics: SustainabilityMetrics;
  riskAssessment: RiskAssessment;
  complianceStatus: ComplianceStatus;
}

export interface SupplyChainStage {
  id: string;
  name: string;
  description: string;
  type: 'cultivation' | 'harvest' | 'processing' | 'packaging' | 'storage' | 'transport' | 'distribution';
  location: Location;
  timestamp: Date;
  duration: number; // hours
  responsible: ResponsibleParty;
  certifications: string[];
  qualityMetrics: QualityMetrics;
  environmentalConditions: EnvironmentalConditions;
  documentation: Document[];
  verificationMethod: 'manual' | 'iot' | 'blockchain' | 'third_party';
  verificationStatus: 'verified' | 'pending' | 'failed';
}

// 第三方API集成相关类型
export interface ThirdPartyService {
  id: string;
  name: string;
  type: 'insurance' | 'payment' | 'logistics' | 'healthcare' | 'government' | 'certification';
  provider: ServiceProvider;
  apiVersion: string;
  endpoints: APIEndpoint[];
  authentication: AuthenticationInfo;
  rateLimit: RateLimit;
  pricing: APIPricing;
  reliability: ReliabilityMetrics;
  compliance: ComplianceInfo;
  integration: IntegrationConfig;
  monitoring: MonitoringConfig;
}

export interface APIIntegrationResult {
  serviceId: string;
  requestId: string;
  status: 'success' | 'failure' | 'timeout' | 'rate_limited';
  data?: any;
  error?: APIError;
  responseTime: number;
  timestamp: Date;
  retryCount: number;
  cacheHit: boolean;
}

// 保险相关类型
export interface InsuranceService {
  providerId: string;
  policyTypes: InsurancePolicyType[];
  coverage: CoverageInfo;
  eligibilityCheck: EligibilityChecker;
  claimProcess: ClaimProcess;
  preauthorization: PreauthorizationProcess;
  reimbursement: ReimbursementInfo;
  networkProviders: NetworkProvider[];
}

export interface InsuranceClaim {
  id: string;
  policyNumber: string;
  patientId: string;
  providerId: string;
  serviceDate: Date;
  services: ClaimedService[];
  totalAmount: number;
  approvedAmount?: number;
  status: ClaimStatus;
  submissionDate: Date;
  processingTime?: number;
  documents: ClaimDocument[];
  notes: string[];
}

// 支付相关类型
export interface PaymentService {
  providerId: string;
  supportedMethods: PaymentMethod[];
  currencies: string[];
  fees: FeeStructure;
  security: SecurityFeatures;
  compliance: PaymentCompliance;
  integration: PaymentIntegration;
  fraud: FraudDetection;
  reporting: PaymentReporting;
}

export interface PaymentTransaction {
  id: string;
  userId: string;
  amount: number;
  currency: string;
  method: PaymentMethod;
  status: PaymentStatus;
  description: string;
  metadata: PaymentMetadata;
  fees: TransactionFee[];
  timestamp: Date;
  confirmationCode?: string;
  refundInfo?: RefundInfo;
  disputeInfo?: DisputeInfo;
}

// 物流相关类型
export interface LogisticsService {
  providerId: string;
  serviceTypes: LogisticsServiceType[];
  coverage: DeliveryCoverage;
  pricing: LogisticsPricing;
  tracking: TrackingCapabilities;
  insurance: LogisticsInsurance;
  specialHandling: SpecialHandlingOptions;
  sustainability: LogisticsSustainability;
}

export interface DeliveryOrder {
  id: string;
  userId: string;
  items: DeliveryItem[];
  pickup: PickupInfo;
  delivery: DeliveryInfo;
  service: LogisticsServiceType;
  status: DeliveryStatus;
  tracking: TrackingInfo;
  pricing: DeliveryPricing;
  specialInstructions: string[];
  insurance?: DeliveryInsurance;
  timeline: DeliveryTimeline;
  proof: DeliveryProof;
}

// 店铺管理相关类型
export interface OnlineStore {
  id: string;
  basicInfo: StoreBasicInfo;
  products: StoreProduct[];
  categories: ProductCategory[];
  inventory: InventoryManagement;
  orders: StoreOrder[];
  customers: StoreCustomer[];
  analytics: StoreAnalytics;
  marketing: MarketingTools;
  settings: StoreSettings;
  integrations: StoreIntegration[];
  compliance: StoreCompliance;
}

export interface StoreProduct {
  id: string;
  basicInfo: ProductBasicInfo;
  variants: ProductVariant[];
  inventory: ProductInventory;
  pricing: ProductPricing;
  marketing: ProductMarketing;
  seo: ProductSEO;
  reviews: ProductReview[];
  recommendations: ProductRecommendation[];
  healthBenefits?: HealthBenefit[];
  tcmProperties?: TCMProductProperties;
  certifications: ProductCertification[];
  supplyChain: SupplyChainInfo;
}

export interface StoreOrder {
  id: string;
  customerId: string;
  items: OrderItem[];
  pricing: OrderPricing;
  payment: OrderPayment;
  shipping: OrderShipping;
  status: OrderStatus;
  timeline: OrderTimeline;
  communication: OrderCommunication[];
  fulfillment: OrderFulfillment;
  returns?: ReturnInfo;
  feedback?: OrderFeedback;
}

// 个性化推荐相关类型
export interface RecommendationEngine {
  userId: string;
  algorithms: RecommendationAlgorithm[];
  userProfile: UserProfile;
  behaviorData: UserBehaviorData;
  preferences: UserPreferences;
  contextualFactors: ContextualFactor[];
  recommendations: Recommendation[];
  feedback: RecommendationFeedback[];
  performance: RecommendationPerformance;
}

export interface Recommendation {
  id: string;
  type: 'product' | 'service' | 'doctor' | 'content' | 'action';
  item: any;
  score: number; // 0-100
  reasoning: string[];
  confidence: number; // 0-100
  category: string;
  tags: string[];
  personalizedFactors: PersonalizationFactor[];
  timing: RecommendationTiming;
  context: RecommendationContext;
  alternatives: AlternativeRecommendation[];
}

// 小克智能体接口
export interface XiaokeAgent {
  // 核心消息处理
  processMessage(message: string, context: ServiceContext): Promise<ServiceResponse>;
  
  // 名医资源智能匹配与预约管理
  matchDoctors(
    symptoms: string[],
    userProfile: UserProfile,
    preferences?: DoctorPreferences
  ): Promise<DoctorMatchingResult[]>;
  
  bookAppointment(
    doctorId: string,
    timeSlot: Date,
    appointmentType: AppointmentType,
    patientInfo: PatientInfo
  ): Promise<AppointmentBooking>;
  
  manageAppointments(userId: string, action: AppointmentAction): Promise<AppointmentManagementResult>;
  
  // 医疗服务订阅与个性化推荐
  recommendServices(
    userProfile: UserProfile,
    healthData?: HealthData,
    context?: ServiceContext
  ): Promise<ServiceRecommendation[]>;
  
  subscribeToService(
    serviceId: string,
    plan: SubscriptionPlan,
    customization?: ServiceCustomization
  ): Promise<ServiceSubscription>;
  
  manageSubscriptions(userId: string, action: SubscriptionAction): Promise<SubscriptionManagementResult>;
  
  // 农产品溯源与定制配送管理
  searchProducts(
    query: ProductSearchQuery,
    filters?: ProductFilters
  ): Promise<AgriculturalProduct[]>;
  
  getProductDetails(productId: string, includeSupplyChain?: boolean): Promise<AgriculturalProduct>;
  
  getSupplyChainInfo(productId: string): Promise<SupplyChainInfo>;
  
  customizeProduct(
    productId: string,
    customization: ProductCustomization
  ): Promise<CustomizedProduct>;
  
  arrangeDelivery(
    orderId: string,
    deliveryPreferences: DeliveryPreferences
  ): Promise<DeliveryOrder>;
  
  // 第三方医疗服务API集成
  integrateInsuranceService(
    insuranceProvider: string,
    policyInfo: InsurancePolicyInfo
  ): Promise<InsuranceIntegrationResult>;
  
  processInsuranceClaim(
    claimInfo: InsuranceClaimInfo
  ): Promise<InsuranceClaim>;
  
  integratePaymentService(
    paymentProvider: string,
    paymentInfo: PaymentInfo
  ): Promise<PaymentIntegrationResult>;
  
  processPayment(
    paymentRequest: PaymentRequest
  ): Promise<PaymentTransaction>;
  
  integrateLogisticsService(
    logisticsProvider: string,
    serviceConfig: LogisticsConfig
  ): Promise<LogisticsIntegrationResult>;
  
  trackDelivery(trackingNumber: string): Promise<TrackingInfo>;
  
  // 在线店铺管理与健康商品推荐
  manageStore(storeId: string, action: StoreAction): Promise<StoreManagementResult>;
  
  addProduct(storeId: string, product: StoreProduct): Promise<ProductAddResult>;
  
  updateInventory(storeId: string, updates: InventoryUpdate[]): Promise<InventoryUpdateResult>;
  
  processOrder(orderId: string, action: OrderAction): Promise<OrderProcessingResult>;
  
  generateHealthProductRecommendations(
    userProfile: UserProfile,
    healthGoals: HealthGoal[]
  ): Promise<HealthProductRecommendation[]>;
  
  // 个性化推荐系统
  generatePersonalizedRecommendations(
    userId: string,
    type: RecommendationType,
    context?: RecommendationContext
  ): Promise<Recommendation[]>;
  
  updateRecommendationFeedback(
    recommendationId: string,
    feedback: RecommendationFeedback
  ): Promise<void>;
  
  // 智能体协作
  coordinateWithOtherAgents(task: AgentTask): Promise<AgentCoordinationResult>;
  shareUserContext(targetAgent: AgentType, context: SharedContext): Promise<void>;
  
  // 状态管理
  getHealthStatus(): Promise<AgentHealthStatus>;
  setPersonality(traits: PersonalityTraits): void;
  getPersonality(): PersonalityTraits;
  cleanup(userId: string): Promise<void>;
}

// 占位符类型定义 - 需要在其他文件中完整定义
export interface Location { [key: string]: any; }
export interface ContactInfo { [key: string]: any; }
export interface ConstitutionType { [key: string]: any; }
export interface Medication { [key: string]: any; }
export interface HealthGoal { [key: string]: any; }
export interface RiskFactor { [key: string]: any; }
export interface NotificationPreferences { [key: string]: any; }
export interface PrivacySettings { [key: string]: any; }
export interface ServicePreferences { [key: string]: any; }
export interface ProductPreferences { [key: string]: any; }
export interface ServiceCategory { [key: string]: any; }
export interface BudgetRange { [key: string]: any; }
export interface TimeFrame { [key: string]: any; }
export interface HealthContext { [key: string]: any; }
export interface InteractionHistory { [key: string]: any; }
export interface PricingInfo { [key: string]: any; }
export interface ServiceProvider { [key: string]: any; }
export interface AvailabilityInfo { [key: string]: any; }
export interface ServiceFeature { [key: string]: any; }
export interface ServiceLocation { [key: string]: any; }
export interface Review { [key: string]: any; }
export interface Certification { [key: string]: any; }
export interface InsuranceCoverage { [key: string]: any; }
export interface CustomizationOption { [key: string]: any; }
export interface DoctorPersonalInfo { [key: string]: any; }
export interface DoctorProfessionalInfo { [key: string]: any; }
export interface MedicalSpecialty { [key: string]: any; }
export interface DoctorAvailability { [key: string]: any; }
export interface ConsultationType { [key: string]: any; }
export interface ConsultationPricing { [key: string]: any; }
export interface DoctorLocation { [key: string]: any; }
export interface DoctorReview { [key: string]: any; }
export interface Achievement { [key: string]: any; }
export interface Publication { [key: string]: any; }
export interface TCMSpecialty { [key: string]: any; }
export interface DoctorMatchingData { [key: string]: any; }
export interface MatchingFactor { [key: string]: any; }
export interface ConsultationOption { [key: string]: any; }
export interface CostEstimate { [key: string]: any; }
export interface FeedbackPrediction { [key: string]: any; }
export interface AppointmentType { [key: string]: any; }
export interface AppointmentStatus { [key: string]: any; }
export interface AppointmentLocation { [key: string]: any; }
export interface PaymentInfo { [key: string]: any; }
export interface ReminderSettings { [key: string]: any; }
export interface CancellationPolicy { [key: string]: any; }
export interface ProductBasicInfo { [key: string]: any; }
export interface NutritionInfo { [key: string]: any; }
export interface HealthBenefit { [key: string]: any; }
export interface TCMProductProperties { [key: string]: any; }
export interface ProductOrigin { [key: string]: any; }
export interface CultivationInfo { [key: string]: any; }
export interface ProductCertification { [key: string]: any; }
export interface ProductPricing { [key: string]: any; }
export interface ProductAvailability { [key: string]: any; }
export interface CustomizationOptions { [key: string]: any; }
export interface ProductReview { [key: string]: any; }
export interface SustainabilityMetrics { [key: string]: any; }
export interface TraceabilityInfo { [key: string]: any; }
export interface CertificationChain { [key: string]: any; }
export interface QualityCheckpoint { [key: string]: any; }
export interface RiskAssessment { [key: string]: any; }
export interface ComplianceStatus { [key: string]: any; }
export interface ResponsibleParty { [key: string]: any; }
export interface QualityMetrics { [key: string]: any; }
export interface EnvironmentalConditions { [key: string]: any; }
export interface Document { [key: string]: any; }
export interface APIEndpoint { [key: string]: any; }
export interface AuthenticationInfo { [key: string]: any; }
export interface RateLimit { [key: string]: any; }
export interface APIPricing { [key: string]: any; }
export interface ReliabilityMetrics { [key: string]: any; }
export interface ComplianceInfo { [key: string]: any; }
export interface IntegrationConfig { [key: string]: any; }
export interface MonitoringConfig { [key: string]: any; }
export interface APIError { [key: string]: any; }
export interface InsurancePolicyType { [key: string]: any; }
export interface CoverageInfo { [key: string]: any; }
export interface EligibilityChecker { [key: string]: any; }
export interface ClaimProcess { [key: string]: any; }
export interface PreauthorizationProcess { [key: string]: any; }
export interface ReimbursementInfo { [key: string]: any; }
export interface NetworkProvider { [key: string]: any; }
export interface ClaimedService { [key: string]: any; }
export interface ClaimStatus { [key: string]: any; }
export interface ClaimDocument { [key: string]: any; }
export interface PaymentMethod { [key: string]: any; }
export interface FeeStructure { [key: string]: any; }
export interface SecurityFeatures { [key: string]: any; }
export interface PaymentCompliance { [key: string]: any; }
export interface PaymentIntegration { [key: string]: any; }
export interface FraudDetection { [key: string]: any; }
export interface PaymentReporting { [key: string]: any; }
export interface PaymentStatus { [key: string]: any; }
export interface PaymentMetadata { [key: string]: any; }
export interface TransactionFee { [key: string]: any; }
export interface RefundInfo { [key: string]: any; }
export interface DisputeInfo { [key: string]: any; }
export interface LogisticsServiceType { [key: string]: any; }
export interface DeliveryCoverage { [key: string]: any; }
export interface LogisticsPricing { [key: string]: any; }
export interface TrackingCapabilities { [key: string]: any; }
export interface LogisticsInsurance { [key: string]: any; }
export interface SpecialHandlingOptions { [key: string]: any; }
export interface LogisticsSustainability { [key: string]: any; }
export interface DeliveryItem { [key: string]: any; }
export interface PickupInfo { [key: string]: any; }
export interface DeliveryInfo { [key: string]: any; }
export interface DeliveryStatus { [key: string]: any; }
export interface TrackingInfo { [key: string]: any; }
export interface DeliveryPricing { [key: string]: any; }
export interface DeliveryInsurance { [key: string]: any; }
export interface DeliveryTimeline { [key: string]: any; }
export interface DeliveryProof { [key: string]: any; }
export interface StoreBasicInfo { [key: string]: any; }
export interface ProductCategory { [key: string]: any; }
export interface InventoryManagement { [key: string]: any; }
export interface StoreOrder { [key: string]: any; }
export interface StoreCustomer { [key: string]: any; }
export interface StoreAnalytics { [key: string]: any; }
export interface MarketingTools { [key: string]: any; }
export interface StoreSettings { [key: string]: any; }
export interface StoreIntegration { [key: string]: any; }
export interface StoreCompliance { [key: string]: any; }
export interface ProductVariant { [key: string]: any; }
export interface ProductInventory { [key: string]: any; }
export interface ProductMarketing { [key: string]: any; }
export interface ProductSEO { [key: string]: any; }
export interface ProductRecommendation { [key: string]: any; }
export interface OrderItem { [key: string]: any; }
export interface OrderPricing { [key: string]: any; }
export interface OrderPayment { [key: string]: any; }
export interface OrderShipping { [key: string]: any; }
export interface OrderStatus { [key: string]: any; }
export interface OrderTimeline { [key: string]: any; }
export interface OrderCommunication { [key: string]: any; }
export interface OrderFulfillment { [key: string]: any; }
export interface ReturnInfo { [key: string]: any; }
export interface OrderFeedback { [key: string]: any; }
export interface RecommendationAlgorithm { [key: string]: any; }
export interface UserBehaviorData { [key: string]: any; }
export interface ContextualFactor { [key: string]: any; }
export interface RecommendationFeedback { [key: string]: any; }
export interface RecommendationPerformance { [key: string]: any; }
export interface PersonalizationFactor { [key: string]: any; }
export interface RecommendationTiming { [key: string]: any; }
export interface RecommendationContext { [key: string]: any; }
export interface AlternativeRecommendation { [key: string]: any; }
export interface ServiceResponse { [key: string]: any; }
export interface DoctorPreferences { [key: string]: any; }
export interface PatientInfo { [key: string]: any; }
export interface AppointmentAction { [key: string]: any; }
export interface AppointmentManagementResult { [key: string]: any; }
export interface HealthData { [key: string]: any; }
export interface SubscriptionPlan { [key: string]: any; }
export interface ServiceCustomization { [key: string]: any; }
export interface ServiceSubscription { [key: string]: any; }
export interface SubscriptionAction { [key: string]: any; }
export interface SubscriptionManagementResult { [key: string]: any; }
export interface ProductSearchQuery { [key: string]: any; }
export interface ProductFilters { [key: string]: any; }
export interface ProductCustomization { [key: string]: any; }
export interface CustomizedProduct { [key: string]: any; }
export interface DeliveryPreferences { [key: string]: any; }
export interface DeliveryAddress { [key: string]: any; }
export interface InsurancePolicyInfo { [key: string]: any; }
export interface InsuranceIntegrationResult { [key: string]: any; }
export interface InsuranceClaimInfo { [key: string]: any; }
export interface PaymentIntegrationResult { [key: string]: any; }
export interface PaymentRequest { [key: string]: any; }
export interface LogisticsConfig { [key: string]: any; }
export interface LogisticsIntegrationResult { [key: string]: any; }
export interface StoreAction { [key: string]: any; }
export interface StoreManagementResult { [key: string]: any; }
export interface ProductAddResult { [key: string]: any; }
export interface InventoryUpdate { [key: string]: any; }
export interface InventoryUpdateResult { [key: string]: any; }
export interface OrderAction { [key: string]: any; }
export interface OrderProcessingResult { [key: string]: any; }
export interface HealthProductRecommendation { [key: string]: any; }
export interface RecommendationType { [key: string]: any; }
export interface AgentTask { [key: string]: any; }
export interface AgentCoordinationResult { [key: string]: any; }
export interface AgentType { [key: string]: any; }
export interface SharedContext { [key: string]: any; }
export interface AgentHealthStatus { [key: string]: any; }
export interface PersonalityTraits { [key: string]: any; } 