// 小艾智能体核心类型定义
export interface ChatContext {
  userId: string;
  sessionId: string;
  conversationHistory: ChatMessage[];
  hasImages?: boolean;
  images?: ImageData[];
  hasAudio?: boolean;
  audio?: AudioData[];
  hasPalpationData?: boolean;
  palpationData?: PalpationData[];
  userProfile?: UserProfile;
  timestamp: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  metadata?: {
    diagnosisIntent?: DiagnosisIntent;
    diagnosisResults?: FourDiagnosisResults;
    suggestions?: string[];
  };
}

export interface ChatResponse {
  text: string;
  actions?: DiagnosisAction[];
  suggestions?: string[];
  followUp?: string;
  diagnosisResults?: FourDiagnosisResults;
  timestamp: number;
}

export interface DiagnosisIntent {
  needsInquiry: boolean;
  needsLookDiagnosis: boolean;
  needsListenDiagnosis: boolean;
  needsPalpationDiagnosis: boolean;
  confidence: number;
  extractedSymptoms: string[];
  urgencyLevel: 'low' | 'medium' | 'high' | 'emergency';
}

export interface DiagnosisAction {
  type: 'inquiry' | 'look' | 'listen' | 'palpation';
  prompt: string;
  autoStart?: boolean;
  optional?: boolean;
  priority: number;
}

export interface FourDiagnosisResults {
  inquiry?: InquiryResult;
  look?: LookResult;
  listen?: ListenResult;
  palpation?: PalpationResult;
  integrated?: IntegratedDiagnosis;
}

// 四诊服务结果类型
export interface InquiryResult {
  sessionId: string;
  detectedSymptoms: SymptomInfo[];
  tcmPatterns: TCMPattern[];
  healthProfile: HealthProfile;
  recommendations: string[];
  confidence: number;
}

export interface LookResult {
  analysisId: string;
  faceAnalysis?: FaceAnalysis;
  tongueAnalysis?: TongueAnalysis;
  bodyAnalysis?: BodyAnalysis;
  overallAssessment: string;
  confidence: number;
}

export interface ListenResult {
  analysisId: string;
  voiceFeatures: VoiceFeatures;
  emotionalState: EmotionalState;
  respiratoryAnalysis?: RespiratoryAnalysis;
  overallAssessment: string;
  confidence: number;
}

export interface PalpationResult {
  analysisId: string;
  pulseAnalysis?: PulseAnalysis;
  abdominalAnalysis?: AbdominalAnalysis;
  skinAnalysis?: SkinAnalysis;
  overallAssessment: string;
  confidence: number;
}

export interface IntegratedDiagnosis {
  overallAssessment: string;
  tcmDiagnosis: TCMDiagnosis;
  healthRecommendations: HealthRecommendation[];
  riskFactors: RiskFactor[];
  followUpActions: FollowUpAction[];
  confidence: number;
}

// 健康相关类型
export interface SymptomInfo {
  name: string;
  severity: 'mild' | 'moderate' | 'severe' | 'extreme';
  duration: number; // 持续时间（小时）
  description: string;
  confidence: number;
}

export interface TCMPattern {
  patternName: string;
  description: string;
  symptoms: string[];
  confidence: number;
}

export interface HealthProfile {
  constitution: TCMConstitution;
  lifestyle: LifestyleCharacteristics;
  riskFactors: RiskFactor[];
}

export interface TCMConstitution {
  type: 'balanced' | 'qi_deficiency' | 'yang_deficiency' | 'yin_deficiency' | 
        'phlegm_dampness' | 'damp_heat' | 'blood_stasis' | 'qi_stagnation' | 'special';
  score: number;
  description: string;
}

export interface LifestyleCharacteristics {
  diet: string[];
  exercise: string[];
  sleep: string[];
  stress: string[];
}

export interface RiskFactor {
  factor: string;
  level: 'low' | 'medium' | 'high';
  description: string;
  preventionSuggestions: string[];
}

// 多模态数据类型
export interface ImageData {
  id: string;
  type: 'face' | 'tongue' | 'body' | 'other';
  uri: string;
  base64?: string;
  metadata?: {
    width: number;
    height: number;
    timestamp: number;
  };
}

export interface AudioData {
  id: string;
  type: 'voice' | 'cough' | 'breathing' | 'other';
  uri: string;
  base64?: string;
  metadata?: {
    duration: number;
    sampleRate: number;
    timestamp: number;
  };
}

export interface PalpationData {
  id: string;
  type: 'pulse' | 'abdominal' | 'skin' | 'other';
  sensorData: any;
  metadata?: {
    duration: number;
    timestamp: number;
  };
}

// 分析结果详细类型
export interface FaceAnalysis {
  complexion: string;
  expression: string;
  eyeCondition: string;
  overallHealth: string;
}

export interface TongueAnalysis {
  tongueBody: string;
  tongueCoating: string;
  moisture: string;
  tcmAssessment: string;
}

export interface BodyAnalysis {
  posture: string;
  movement: string;
  overallVitality: string;
}

export interface VoiceFeatures {
  pitch: number;
  tone: string;
  clarity: string;
  strength: string;
}

export interface EmotionalState {
  mood: string;
  stress: string;
  energy: string;
  confidence: number;
}

export interface RespiratoryAnalysis {
  breathingPattern: string;
  lungSounds: string;
  assessment: string;
}

export interface PulseAnalysis {
  rate: number;
  rhythm: string;
  strength: string;
  tcmPulseType: string;
}

export interface AbdominalAnalysis {
  tenderness: string;
  tension: string;
  temperature: string;
}

export interface SkinAnalysis {
  texture: string;
  temperature: string;
  moisture: string;
  elasticity: string;
}

// 中医诊断类型
export interface TCMDiagnosis {
  syndrome: string;
  pathogenesis: string;
  treatment: string;
  prognosis: string;
}

export interface HealthRecommendation {
  category: 'diet' | 'exercise' | 'lifestyle' | 'medication' | 'therapy';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  timeframe: string;
}

export interface FollowUpAction {
  action: string;
  timeframe: string;
  priority: 'low' | 'medium' | 'high';
  description: string;
}

// 用户相关类型
export interface UserProfile {
  id: string;
  basicInfo: {
    age: number;
    gender: 'male' | 'female' | 'other';
    height: number;
    weight: number;
  };
  medicalHistory: MedicalRecord[];
  preferences: UserPreferences;
  accessibilityNeeds?: AccessibilityNeeds;
}

export interface MedicalRecord {
  condition: string;
  diagnosisDate: number;
  treatment: string;
  status: 'active' | 'resolved' | 'chronic';
}

export interface UserPreferences {
  language: string;
  communicationStyle: 'formal' | 'casual' | 'caring';
  diagnosisPreferences: {
    autoStartDiagnosis: boolean;
    preferredDiagnosisTypes: string[];
    privacyLevel: 'low' | 'medium' | 'high';
  };
}

export interface AccessibilityNeeds {
  visual: boolean;
  hearing: boolean;
  motor: boolean;
  cognitive: boolean;
  preferences: {
    fontSize: 'small' | 'medium' | 'large' | 'extra-large';
    highContrast: boolean;
    voiceOutput: boolean;
    simplifiedInterface: boolean;
  };
}

// 小艾智能体接口
export interface XiaoaiAgent {
  // 基础对话功能
  chat(message: string, context: ChatContext): Promise<ChatResponse>;
  analyzeHealthData(data: any): Promise<any>;
  generateSuggestions(profile: UserProfile): Promise<HealthRecommendation[]>;
  setPersonality(traits: any): void;
  
  // 四诊功能集成
  startInquirySession(userId: string): Promise<any>;
  analyzeImage(imageData: ImageData, type: 'face' | 'tongue' | 'body'): Promise<LookResult>;
  analyzeAudio(audioData: AudioData, type: 'voice' | 'sound'): Promise<ListenResult>;
  processPalpationData(data: PalpationData): Promise<PalpationResult>;
  performFourDiagnosisIntegration(data: FourDiagnosisResults): Promise<IntegratedDiagnosis>;
  
  // 无障碍功能
  enableAccessibilityFeature(feature: any): Promise<void>;
  getAccessibilityStatus(): Promise<any>;
  adaptInterfaceForDisability(disability: any): Promise<any>;
}

// 服务客户端接口
export interface DiagnosisServiceClient {
  inquiry: InquiryServiceClient;
  look: LookServiceClient;
  listen: ListenServiceClient;
  palpation: PalpationServiceClient;
}

export interface InquiryServiceClient {
  startSession(userId: string): Promise<any>;
  interact(sessionId: string, message: string): Promise<any>;
  endSession(sessionId: string): Promise<InquiryResult>;
}

export interface LookServiceClient {
  analyzeImage(imageData: ImageData): Promise<LookResult>;
  batchAnalyze(images: ImageData[]): Promise<LookResult[]>;
}

export interface ListenServiceClient {
  analyzeAudio(audioData: AudioData): Promise<ListenResult>;
  analyzeVoiceFeatures(audioData: AudioData): Promise<VoiceFeatures>;
}

export interface PalpationServiceClient {
  analyzePalpation(data: PalpationData): Promise<PalpationResult>;
  startRealTimeMonitoring(userId: string): Promise<string>;
} 