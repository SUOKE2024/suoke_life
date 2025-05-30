// 小艾智能体类型定义 - 健康助手 & 首页聊天频道版主
// 基于README.md智能体描述全面更新

// 基础数据类型
export interface AudioData {
  data: ArrayBuffer | string;
  format: "wav" | "mp3" | "aac" | "opus";
  sampleRate: number;
  duration: number;
  channels: number;
  quality?: "low" | "medium" | "high";
  metadata?: AudioMetadata;
}

export interface ImageData {
  data: ArrayBuffer | string;
  format: "jpg" | "png" | "webp" | "raw";
  width: number;
  height: number;
  quality?: number;
  metadata?: ImageMetadata;
  type?: "face" | "tongue" | "body" | "other";
}

export interface VideoData {
  data: ArrayBuffer | string;
  format: "mp4" | "webm" | "avi";
  width: number;
  height: number;
  duration: number;
  frameRate: number;
  quality?: "low" | "medium" | "high";
  metadata?: VideoMetadata;
}

export interface PalpationData {
  id: string;
  type: "pulse" | "abdominal" | "skin" | "acupoint" | "other";
  sensorData: any;
  pressure?: number;
  temperature?: number;
  duration: number;
  location?: string;
  metadata?: {
    timestamp: number;
    deviceId?: string;
    calibration?: any;
  };
}

// 用户相关类型
export interface UserProfile {
  id: string;
  basicInfo: BasicUserInfo;
  healthProfile: HealthProfile;
  preferences: UserPreferences;
  medicalHistory: MedicalHistoryItem[];
  constitution?: ConstitutionResult;
  accessibilityNeeds?: AccessibilityNeeds;
  culturalBackground?: CulturalBackground;
}

export interface BasicUserInfo {
  name: string;
  age: number;
  gender: "male" | "female" | "other";
  height?: number;
  weight?: number;
  location?: Location;
  timezone?: string;
  language: string;
  dialects?: string[];
}

export interface HealthProfile {
  chronicConditions: string[];
  allergies: string[];
  medications: Medication[];
  vitalSigns: VitalSigns;
  constitution: ConstitutionType;
  riskFactors: RiskFactor[];
  healthGoals: HealthGoal[];
}

export interface UserPreferences {
  communicationStyle: "formal" | "casual" | "medical" | "friendly";
  language: string;
  voicePreferences: VoiceProfile;
  privacyLevel: "low" | "medium" | "high";
  notificationPreferences: NotificationPreferences;
  accessibilityPreferences: AccessibilityPreferences;
  culturalPreferences: CulturalPreferences;
}

// 聊天相关类型
export interface ChatContext {
  userId: string;
  sessionId: string;
  conversationHistory: ChatMessage[];
  userProfile: UserProfile;
  currentSymptoms?: string[];
  healthContext?: HealthContext;
  accessibilityNeeds?: AccessibilityNeeds;
  language?: string;
  dialect?: string;
  emotionalState?: EmotionalState;
  environmentContext?: EnvironmentContext;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  metadata?: any;
}

export interface ChatResponse {
  text: string;
  audioUrl?: string;
  suggestions?: string[];
  actions?: ChatAction[];
  followUpQuestions?: string[];
  diagnosticRecommendations?: DiagnosticRecommendation[];
  healthInsights?: HealthInsight[];
  accessibilitySupport?: AccessibilitySupport;
  emotionalSupport?: EmotionalSupport;
}

export interface ChatAction {
  type: string;
  label: string;
  data?: any;
}

// 语音相关类型
export interface VoiceResponse {
  transcription: string;
  confidence: number;
  language: string;
  dialect?: string;
  emotionalTone?: EmotionalTone;
  healthIndicators?: VoiceHealthIndicators;
  response: ChatResponse;
}

export interface VoiceProfile {
  gender: "male" | "female" | "neutral";
  age: "child" | "adult" | "elderly";
  tone: "warm" | "professional" | "friendly" | "calm";
  speed: "slow" | "normal" | "fast";
  language: string;
  dialect?: string;
}

export interface VoiceHealthIndicators {
  stressLevel?: number;
  fatigueLevel?: number;
  respiratoryHealth?: string;
  emotionalState?: string;
  voiceQuality?: string;
}

// 四诊结果集合
export interface FourDiagnosisResults {
  inquiry?: InquiryResult;
  look?: LookResult;
  listen?: ListenResult;
  palpation?: PalpationResult;
  integrated?: IntegratedDiagnosis;
}

// 中医诊断相关类型
export interface LookResult {
  faceAnalysis?: FaceAnalysis;
  tongueAnalysis?: TongueAnalysis;
  bodyAnalysis?: BodyAnalysis;
  overallAssessment: string;
  confidence: number;
  recommendations: string[];
  tcmFindings: TCMFindings;
}

export interface FaceAnalysis {
  complexion: string;
  colorAnalysis: ColorAnalysis;
  facialFeatures: FacialFeatures;
  emotionalState: string;
  healthIndicators: string[];
}

export interface TongueAnalysis {
  tongueBody: TongueBodyAnalysis;
  tongueCoating: TongueCoatingAnalysis;
  tongueShape: TongueShapeAnalysis;
  tongueMovement: TongueMovementAnalysis;
  overallCondition: string;
}

export interface BodyAnalysis {
  posture: string;
  movement: string;
  vitality: string;
  skinCondition: string;
  overallHealth: string;
}

export interface ListenResult {
  voiceAnalysis: VoiceAnalysis;
  breathingPattern?: BreathingAnalysis;
  coughAnalysis?: CoughAnalysis;
  heartSounds?: HeartSoundAnalysis;
  overallAssessment: string;
  confidence: number;
  tcmFindings: TCMFindings;
}

export interface InquiryResult {
  symptoms: SymptomAnalysis[];
  constitutionType: ConstitutionType;
  healthConcerns: HealthConcern[];
  riskFactors: RiskFactor[];
  recommendations: string[];
  followUpQuestions: string[];
  tcmSyndrome?: TCMSyndrome;
}

export interface PalpationResult {
  pulseAnalysis: PulseAnalysis;
  pressurePoints: PressurePointAnalysis[];
  overallAssessment: string;
  confidence: number;
  tcmFindings: TCMFindings;
}

export interface IntegratedDiagnosis {
  lookFindings: LookResult;
  listenFindings: ListenResult;
  inquiryFindings: InquiryResult;
  palpationFindings: PalpationResult;
  integratedAssessment: string;
  tcmDiagnosis: TCMDiagnosis;
  westernMedicineCorrelation?: WesternMedicineCorrelation;
  treatmentPrinciples: string[];
  recommendedTreatments: Treatment[];
  lifestyleRecommendations: LifestyleRecommendation[];
  followUpPlan: FollowUpPlan;
  confidence: number;
}

// 健康数据相关类型
export interface HealthDataInput {
  vitalSigns?: VitalSigns;
  symptoms?: string[];
  lifestyle?: LifestyleData;
  medicalHistory?: MedicalHistoryItem[];
  labResults?: LabResult[];
  deviceData?: DeviceData[];
  environmentalData?: EnvironmentalData;
}

export interface HealthAnalysis {
  summary: string;
  insights: HealthInsight[];
  riskAssessment: RiskAssessment;
  trends: HealthTrend[];
  recommendations: HealthRecommendation[];
  alerts: HealthAlert[];
  tcmAssessment?: TCMHealthAssessment;
}

export interface HealthTrends {
  timeRange: TimeRange;
  trends: HealthTrend[];
  patterns: HealthPattern[];
  predictions: HealthPrediction[];
  recommendations: string[];
}

export interface HealthRecommendation {
  category:
    | "diet"
    | "exercise"
    | "lifestyle"
    | "medical"
    | "tcm"
    | "mental_health";
  title: string;
  description: string;
  priority: "low" | "medium" | "high" | "urgent";
  timeframe: string;
  evidence?: string;
  tcmRationale?: string;
  implementation?: ImplementationGuide;
}

// 无障碍服务相关类型
export interface AccessibilityFeature {
  type: "visual" | "auditory" | "motor" | "cognitive" | "speech";
  subtype?: string;
  severity: "mild" | "moderate" | "severe";
  preferences: AccessibilityPreferences;
}

export interface NavigationGuidance {
  instructions: string[];
  audioGuidance?: string;
  hapticFeedback?: HapticPattern[];
  visualCues?: VisualCue[];
  landmarks?: Landmark[];
}

export interface SignLanguageResult {
  recognizedSigns: RecognizedSign[];
  confidence: number;
  translation: string;
  response?: ChatResponse;
}

export interface InterfaceAdaptation {
  visualAdaptations: VisualAdaptation[];
  audioAdaptations: AudioAdaptation[];
  interactionAdaptations: InteractionAdaptation[];
  contentAdaptations: ContentAdaptation[];
}

// 体质评估相关类型
export interface ConstitutionAssessmentData {
  physicalCharacteristics: PhysicalCharacteristics;
  psychologicalTraits: PsychologicalTraits;
  lifestyle: LifestyleData;
  symptoms: string[];
  medicalHistory: MedicalHistoryItem[];
  environmentalFactors: EnvironmentalFactors;
}

export interface ConstitutionResult {
  primaryConstitution: ConstitutionType;
  secondaryConstitutions: ConstitutionType[];
  constitutionScore: ConstitutionScore;
  characteristics: string[];
  strengths: string[];
  weaknesses: string[];
  recommendations: ConstitutionRecommendation[];
  seasonalGuidance: SeasonalGuidance[];
}

export interface CalculationResult {
  diagnosis: string;
  confidence: number;
  reasoning: string[];
  differentialDiagnosis: string[];
  treatmentPrinciples: string[];
  prescriptionRecommendations: PrescriptionRecommendation[];
  prognosisAssessment: PrognosisAssessment;
}

// 智能体协作相关类型
export interface AgentTask {
  taskId: string;
  type: "diagnosis" | "recommendation" | "education" | "service" | "lifestyle";
  priority: "low" | "medium" | "high" | "urgent";
  requiredAgents: AgentType[];
  data: any;
  context: TaskContext;
  deadline?: Date;
}

export interface AgentCoordinationResult {
  taskId: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  results: AgentTaskResult[];
  aggregatedResult?: any;
  recommendations?: string[];
}

export type AgentType = "xiaoai" | "xiaoke" | "laoke" | "soer";

// 其他支持类型
export interface PersonalityTraits {
  style: "caring" | "professional" | "friendly" | "authoritative";
  tone: "warm" | "neutral" | "energetic" | "calm";
  expertise: "health" | "medical" | "wellness" | "general";
  patience: "low" | "medium" | "high";
  empathy: "low" | "medium" | "high";
  culturalSensitivity: "low" | "medium" | "high";
}

export interface AgentHealthStatus {
  status: "healthy" | "degraded" | "error";
  uptime: number;
  responseTime: number;
  accuracy: number;
  lastUpdate: Date;
  activeConnections: number;
  memoryUsage: number;
  errors: AgentError[];
}

// 中医相关类型
export interface TCMFindings {
  syndrome?: string;
  pattern?: string;
  organSystems?: string[];
  pathogenesis?: string;
  treatmentPrinciple?: string;
  prognosis?: string;
}

export interface TCMDiagnosis {
  mainSyndrome: string;
  secondarySyndromes: string[];
  organSystems: string[];
  pathogenesis: string;
  treatmentPrinciples: string[];
  prognosis: string;
  confidence: number;
}

export type ConstitutionType =
  | "balanced" // 平和质
  | "qi_deficiency" // 气虚质
  | "yang_deficiency" // 阳虚质
  | "yin_deficiency" // 阴虚质
  | "phlegm_dampness" // 痰湿质
  | "damp_heat" // 湿热质
  | "blood_stasis" // 血瘀质
  | "qi_stagnation" // 气郁质
  | "special_diathesis"; // 特禀质

// 错误处理
export interface AgentError {
  code: string;
  message: string;
  timestamp: Date;
  severity: "low" | "medium" | "high" | "critical";
  context?: any;
}

// 时间相关
export interface TimeRange {
  start: Date;
  end: Date;
  granularity?: "hour" | "day" | "week" | "month" | "year";
}

// 小艾智能体接口
export interface XiaoaiAgent {
  // 核心聊天功能
  chat(message: string, context: ChatContext): Promise<ChatResponse>;

  // 多语种语音交互
  processVoiceInput(
    audioData: AudioData,
    language?: string,
    dialect?: string
  ): Promise<VoiceResponse>;
  synthesizeVoice(
    text: string,
    language?: string,
    voice?: VoiceProfile
  ): Promise<AudioData>;

  // 中医四诊合参功能
  performLookDiagnosis(
    imageData: ImageData,
    type: "face" | "tongue" | "body"
  ): Promise<LookResult>;
  performListenDiagnosis(
    audioData: AudioData,
    type: "voice" | "cough" | "breathing" | "other"
  ): Promise<ListenResult>;
  performInquiryDiagnosis(
    userId: string,
    symptoms?: string[]
  ): Promise<InquiryResult>;
  performPalpationDiagnosis(data: PalpationData): Promise<PalpationResult>;
  integrateFourDiagnosis(
    results: FourDiagnosisResults
  ): Promise<IntegratedDiagnosis>;

  // 健康数据分析
  analyzeHealthData(data: HealthDataInput): Promise<HealthAnalysis>;
  generateHealthRecommendations(
    profile: UserProfile
  ): Promise<HealthRecommendation[]>;
  trackHealthTrends(
    userId: string,
    timeRange: TimeRange
  ): Promise<HealthTrends>;

  // 医疗记录管理
  createMedicalRecord(data: MedicalRecordInput): Promise<MedicalRecord>;
  updateMedicalRecord(
    recordId: string,
    updates: Partial<MedicalRecord>
  ): Promise<MedicalRecord>;
  getMedicalHistory(
    userId: string,
    filters?: MedicalHistoryFilters
  ): Promise<MedicalRecord[]>;
  generateHealthReport(userId: string, type: ReportType): Promise<HealthReport>;

  // 无障碍服务
  enableAccessibilityFeature(feature: AccessibilityFeature): Promise<void>;
  provideNavigationAssistance(
    context: NavigationContext
  ): Promise<NavigationGuidance>;
  recognizeSignLanguage(videoData: VideoData): Promise<SignLanguageResult>;
  adaptInterfaceForDisability(
    disability: DisabilityType
  ): Promise<InterfaceAdaptation>;
  provideElderlyFriendlyInterface(): Promise<ElderlyInterfaceConfig>;

  // 体质评估与算诊
  assessConstitution(
    data: ConstitutionAssessmentData
  ): Promise<ConstitutionResult>;
  performCalculationDiagnosis(
    symptoms: string[],
    context: DiagnosisContext
  ): Promise<CalculationResult>;
  generateTreatmentPlan(
    diagnosis: IntegratedDiagnosis,
    userProfile: UserProfile
  ): Promise<TreatmentPlan>;

  // 智能体协作
  coordinateWithOtherAgents(task: AgentTask): Promise<AgentCoordinationResult>;
  shareUserContext(
    targetAgent: AgentType,
    context: SharedContext
  ): Promise<void>;

  // 个性化设置
  setPersonality(traits: PersonalityTraits): void;
  getPersonality(): PersonalityTraits;

  // 状态管理
  getHealthStatus(): Promise<AgentHealthStatus>;
  cleanup(userId: string): Promise<void>;
}

// 占位符类型定义 - 需要在其他文件中完整定义
export interface AudioMetadata {
  [key: string]: any;
}
export interface ImageMetadata {
  [key: string]: any;
}
export interface VideoMetadata {
  [key: string]: any;
}
export interface HealthContext {
  [key: string]: any;
}
export interface AccessibilityNeeds {
  [key: string]: any;
}
export interface EmotionalState {
  [key: string]: any;
}
export interface EnvironmentContext {
  [key: string]: any;
}
export interface DiagnosticRecommendation {
  [key: string]: any;
}
export interface HealthInsight {
  [key: string]: any;
}
export interface AccessibilitySupport {
  [key: string]: any;
}
export interface EmotionalSupport {
  [key: string]: any;
}
export interface EmotionalTone {
  [key: string]: any;
}
export interface ColorAnalysis {
  [key: string]: any;
}
export interface FacialFeatures {
  [key: string]: any;
}
export interface TongueBodyAnalysis {
  [key: string]: any;
}
export interface TongueCoatingAnalysis {
  [key: string]: any;
}
export interface TongueShapeAnalysis {
  [key: string]: any;
}
export interface TongueMovementAnalysis {
  [key: string]: any;
}
export interface VoiceAnalysis {
  [key: string]: any;
}
export interface BreathingAnalysis {
  [key: string]: any;
}
export interface CoughAnalysis {
  [key: string]: any;
}
export interface HeartSoundAnalysis {
  [key: string]: any;
}
export interface SymptomAnalysis {
  [key: string]: any;
}
export interface HealthConcern {
  [key: string]: any;
}
export interface RiskFactor {
  [key: string]: any;
}
export interface TCMSyndrome {
  [key: string]: any;
}
export interface PulseAnalysis {
  [key: string]: any;
}
export interface PressurePointAnalysis {
  [key: string]: any;
}
export interface WesternMedicineCorrelation {
  [key: string]: any;
}
export interface Treatment {
  [key: string]: any;
}
export interface LifestyleRecommendation {
  [key: string]: any;
}
export interface FollowUpPlan {
  [key: string]: any;
}
export interface VitalSigns {
  [key: string]: any;
}
export interface LifestyleData {
  [key: string]: any;
}
export interface MedicalHistoryItem {
  [key: string]: any;
}
export interface LabResult {
  [key: string]: any;
}
export interface DeviceData {
  [key: string]: any;
}
export interface EnvironmentalData {
  [key: string]: any;
}
export interface RiskAssessment {
  [key: string]: any;
}
export interface HealthTrend {
  [key: string]: any;
}
export interface HealthAlert {
  [key: string]: any;
}
export interface TCMHealthAssessment {
  [key: string]: any;
}
export interface HealthPattern {
  [key: string]: any;
}
export interface HealthPrediction {
  [key: string]: any;
}
export interface ImplementationGuide {
  [key: string]: any;
}
export interface AccessibilityPreferences {
  [key: string]: any;
}
export interface HapticPattern {
  [key: string]: any;
}
export interface VisualCue {
  [key: string]: any;
}
export interface Landmark {
  [key: string]: any;
}
export interface RecognizedSign {
  [key: string]: any;
}
export interface VisualAdaptation {
  [key: string]: any;
}
export interface AudioAdaptation {
  [key: string]: any;
}
export interface InteractionAdaptation {
  [key: string]: any;
}
export interface ContentAdaptation {
  [key: string]: any;
}
export interface PhysicalCharacteristics {
  [key: string]: any;
}
export interface PsychologicalTraits {
  [key: string]: any;
}
export interface EnvironmentalFactors {
  [key: string]: any;
}
export interface ConstitutionScore {
  [key: string]: any;
}
export interface ConstitutionRecommendation {
  [key: string]: any;
}
export interface SeasonalGuidance {
  [key: string]: any;
}
export interface PrescriptionRecommendation {
  [key: string]: any;
}
export interface PrognosisAssessment {
  [key: string]: any;
}
export interface TaskContext {
  [key: string]: any;
}
export interface AgentTaskResult {
  [key: string]: any;
}
export interface Location {
  [key: string]: any;
}
export interface Medication {
  [key: string]: any;
}
export interface HealthGoal {
  [key: string]: any;
}
export interface NotificationPreferences {
  [key: string]: any;
}
export interface CulturalPreferences {
  [key: string]: any;
}
export interface CulturalBackground {
  [key: string]: any;
}
export interface MedicalRecord {
  [key: string]: any;
}
export interface MedicalRecordInput {
  [key: string]: any;
}
export interface MedicalHistoryFilters {
  [key: string]: any;
}
export interface ReportType {
  [key: string]: any;
}
export interface HealthReport {
  [key: string]: any;
}
export interface NavigationContext {
  [key: string]: any;
}
export interface DisabilityType {
  [key: string]: any;
}
export interface ElderlyInterfaceConfig {
  [key: string]: any;
}
export interface DiagnosisContext {
  [key: string]: any;
}
export interface TreatmentPlan {
  [key: string]: any;
}
export interface SharedContext {
  [key: string]: any;
}
