import React from "react";";
wav" | "mp3" | "aac" | "opus",";
sampleRate: number,;
duration: number,";,"";
const channels = number;";,"";
quality?: "low" | "medium" | "high";";,"";
metadata?: AudioMetadata}
export interface ImageData {";,}data: ArrayBuffer | string,";,"";
format: "jpg" | "png" | "webp" | "raw",width: number,height: number;";,"";
quality?: number;";,"";
metadata?: ImageMetadata;";"";
}
}
  type?: "face" | "tongue" | "body" | "other"}"";"";
}
export interface VideoData {";,}data: ArrayBuffer | string,";,"";
format: "mp4" | "webm" | "avi";",";
width: number,;
height: number,;
duration: number,";,"";
const frameRate = number;";,"";
quality?: "low" | "medium" | "high";";"";
}
}
  metadata?: VideoMetadata;}
}";,"";
export interface PalpationData {";,}id: string,type: "pulse" | "abdominal" | "skin" | "acupoint" | "other",sensorData: unknown;";,"";
pressure?: number;
temperature?: number;
const duration = number;
location?: string;
metadata?: {const timestamp = number;,}deviceId?: string;
}
}
    calibration?: unknown;}
};
}
// 用户相关类型 * export interface UserProfile {/;,}id: string,;,/g,/;
  basicInfo: BasicUserInfo,;
healthProfile: HealthProfile,preferences: UserPreferences,medicalHistory: MedicalHistoryItem[];
constitution?: ConstitutionResult;
accessibilityNeeds?: AccessibilityNeeds;
}
}
  culturalBackground?: CulturalBackground;}
}";,"";
export interface BasicUserInfo {";,}name: string,age: number,gender: "male" | "female" | "other";";,"";
height?: number;
weight?: number;
location?: Location;
timezone?: string;
const language = string;
}
}
  dialects?: string[];}
}
export interface HealthProfile {chronicConditions: string[]}allergies: string[],;
medications: Medication[],;
vitalSigns: VitalSigns,;
constitution: ConstitutionType,;
riskFactors: RiskFactor[],;
}
}
  const healthGoals = HealthGoal[];}
}";,"";
export interface UserPreferences {";,}communicationStyle: "formal" | "casual" | "medical" | "friendly";",";
language: string,";,"";
voicePreferences: VoiceProfile,";,"";
privacyLevel: "low" | "medium" | "high";",";
notificationPreferences: NotificationPreferences,;
accessibilityPreferences: AccessibilityPreferences,;
}
}
  const culturalPreferences = CulturalPreferences;}
}
// 聊天相关类型 * export interface ChatContext {/;,}userId: string,;,/g,/;
  sessionId: string,conversationHistory: ChatMessage[],userProfile: UserProfile;
currentSymptoms?: string[];
healthContext?: HealthContext;
accessibilityNeeds?: AccessibilityNeeds;
language?: string;
dialect?: string;
emotionalState?: EmotionalState;
}
}
  environmentContext?: EnvironmentContext;}
}
export interface ChatMessage {";,}id: string,";,"";
role: "user" | "assistant",content: string,timestamp: number;";"";
}
}
  metadata?: unknown;}
}
export interface ChatResponse {;,}const text = string;
audioUrl?: string;
suggestions?: string[];
actions?: ChatAction[];
followUpQuestions?: string[];
diagnosticRecommendations?: DiagnosticRecommendation[];
healthInsights?: HealthInsight[];
accessibilitySupport?: AccessibilitySupport;
}
}
  emotionalSupport?: EmotionalSupport;}
}
export interface ChatAction {;,}type: string,label: string;
}
}
  data?: unknown;}
}
// 语音相关类型 * export interface VoiceResponse {/;};,/g,/;
  transcription: string,   ;
confidence: number,language: string;
dialect?: string;
emotionalTone?: EmotionalTone;
healthIndicators?: VoiceHealthIndicators;
}
}
  const response = ChatResponse;}
}";,"";
export interface VoiceProfile {";,}gender: "male" | "female" | "neutral";",";
age: "child" | "adult" | "elderly";",";
tone: "warm" | "professional" | "friendly" | "calm",speed: "slow" | "normal" | "fast",language: string;";"";
}
}
  dialect?: string;}
}
export interface VoiceHealthIndicators {;,}stressLevel?: number;
fatigueLevel?: number;
respiratoryHealth?: string;
emotionalState?: string;
}
}
  voiceQuality?: string;}
}
// 四诊结果集合 * export interface FourDiagnosisResults {/;};/g/;
    ;
/    ;/;,/g/;
inquiry?: InquiryResult;
look?: LookResult;
listen?: ListenResult;
palpation?: PalpationResult;
}
}
  integrated?: IntegratedDiagnosis;}
}
// 中医诊断相关类型 * export interface LookResult {/;};/g/;
    ;
/    ;/;,/g/;
faceAnalysis?: FaceAnalysis;
tongueAnalysis?: TongueAnalysis;
bodyAnalysis?: BodyAnalysis;
overallAssessment: string,;
confidence: number,;
recommendations: string[],;
}
}
  const tcmFindings = TCMFindings;}
}
export interface FaceAnalysis {complexion: string}colorAnalysis: ColorAnalysis,;
}
}
  facialFeatures: FacialFeatures,emotionalState: string,healthIndicators: string[];}
}
export interface TongueAnalysis {tongueBody: TongueBodyAnalysis}tongueCoating: TongueCoatingAnalysis,;
tongueShape: TongueShapeAnalysis,;
tongueMovement: TongueMovementAnalysis,;
}
}
  const overallCondition = string;}
}
export interface BodyAnalysis {posture: string}movement: string,;
vitality: string,;
}
}
  skinCondition: string,overallHealth: string;}
};
export interface ListenResult {;,}const voiceAnalysis = VoiceAnalysis;
breathingPattern?: BreathingAnalysis;
coughAnalysis?: CoughAnalysis;
heartSounds?: HeartSoundAnalysis;
overallAssessment: string,;
confidence: number,;
}
}
  const tcmFindings = TCMFindings;}
}
export interface InquiryResult {symptoms: SymptomAnalysis[]}constitutionType: ConstitutionType,;
healthConcerns: HealthConcern[],;
riskFactors: RiskFactor[],recommendations: string[],followUpQuestions: string[];
}
}
  tcmSyndrome?: TCMSyndrome;}
}
export interface PalpationResult {pulseAnalysis: PulseAnalysis}pressurePoints: PressurePointAnalysis[],;
overallAssessment: string,;
confidence: number,;
}
}
  const tcmFindings = TCMFindings;}
}
export interface IntegratedDiagnosis {lookFindings: LookResult}listenFindings: ListenResult,;
inquiryFindings: InquiryResult,;
palpationFindings: PalpationResult,integratedAssessment: string,tcmDiagnosis: TCMDiagnosis;
westernMedicineCorrelation?: WesternMedicineCorrelation;
treatmentPrinciples: string[],;
recommendedTreatments: Treatment[],;
lifestyleRecommendations: LifestyleRecommendation[],;
followUpPlan: FollowUpPlan,;
}
}
  const confidence = number;}
}
// 健康数据相关类型 * export interface HealthDataInput {/;};/g/;
    ;
/    ;/;,/g/;
vitalSigns?: VitalSigns;
symptoms?: string[];
lifestyle?: LifestyleData;
medicalHistory?: MedicalHistoryItem[];
labResults?: LabResult[];
deviceData?: DeviceData[];
}
}
  environmentalData?: EnvironmentalData;}
}
export interface HealthAnalysis {summary: string}insights: HealthInsight[],;
riskAssessment: RiskAssessment,;
trends: HealthTrend[],recommendations: HealthRecommendation[],alerts: HealthAlert[];
}
}
  tcmAssessment?: TCMHealthAssessment;}
}
export interface HealthTrends {timeRange: TimeRange}trends: HealthTrend[],;
patterns: HealthPattern[],;
predictions: HealthPrediction[],;
}
}
  const recommendations = string[];}
}";,"";
export interface HealthRecommendation {";,}const category = | "diet"| "exercise"| "lifestyle";";"";
    | "medical"";"";
    | "tcm"";"";
    | "mental_health";
title: string,";,"";
description: string,priority: "low" | "medium" | "high" | "urgent",timeframe: string;";,"";
evidence?: string;
tcmRationale?: string;
}
}
  implementation?: ImplementationGuide;}
}";"";
// 无障碍服务相关类型 * export interface AccessibilityFeature {/;}";,"/g"/;
const type = "visual" | "auditory" | "motor" | "cognitive" | "speech";";"";
/"/;,"/g"/;
subtype?: string;";"";
}
}
  severity: "mild" | "moderate" | "severe",preferences: AccessibilityPreferences;"}"";"";
};
export interface NavigationGuidance {;,}const instructions = string[];
audioGuidance?: string;
hapticFeedback?: HapticPattern[];
visualCues?: VisualCue[];
}
}
  landmarks?: Landmark[];}
}
export interface SignLanguageResult {;,}recognizedSigns: RecognizedSign[],confidence: number,translation: string;
}
}
  response?: ChatResponse;}
}
export interface InterfaceAdaptation {visualAdaptations: VisualAdaptation[],;}}
}
  audioAdaptations: AudioAdaptation[],interactionAdaptations: InteractionAdaptation[],contentAdaptations: ContentAdaptation[];}
}
// 体质评估相关类型 * export interface ConstitutionAssessmentData {/;,}physicalCharacteristics: PhysicalCharacteristics,;,/g,/;
  psychologicalTraits: PsychologicalTraits,;
lifestyle: LifestyleData,;
symptoms: string[],;
medicalHistory: MedicalHistoryItem[],;
}
}
  const environmentalFactors = EnvironmentalFactors;}
}
export interface ConstitutionResult {primaryConstitution: ConstitutionType}secondaryConstitutions: ConstitutionType[],;
constitutionScore: ConstitutionScore,;
characteristics: string[],;
strengths: string[],;
}
}
  weaknesses: string[],recommendations: ConstitutionRecommendation[],seasonalGuidance: SeasonalGuidance[];}
}
export interface CalculationResult {diagnosis: string}confidence: number,;
reasoning: string[],;
differentialDiagnosis: string[],;
treatmentPrinciples: string[],;
prescriptionRecommendations: PrescriptionRecommendation[],;
}
}
  const prognosisAssessment = PrognosisAssessment;}
}
// 智能体协作相关类型 * export interface AgentTask {/;}";,"/g,"/;
  taskId: string,";,"";
type: "diagnosis" | "recommendation" | "education" | "service" | "lifestyle";",";
priority: "low" | "medium" | "high" | "urgent";",";
requiredAgents: AgentType[],;
data: unknown,;
const context = TaskContext;
}
}
  deadline?: Date;}
}
export interface AgentCoordinationResult {";,}taskId: string,";,"";
status: "pending" | "in_progress" | "completed" | "failed";",";
const results = AgentTaskResult[];
aggregatedResult?: unknown;
}
}
  recommendations?: string[]}";"";
}";,"";
export type AgentType = "xiaoai" | "xiaoke" | "laoke" | "so;e;";";,"";
r;";"";
// 其他支持类型 * export interface PersonalityTraits {/;}";,"/g,"/;
  style: "caring" | "professional" | "friendly" | "authoritative";",";
tone: "warm" | "neutral" | "energetic" | "calm";",";
expertise: "health" | "medical" | "wellness" | "general";",";
patience: "low" | "medium" | "high";",";
empathy: "low" | "medium" | "high";","";"";
}
}
  const culturalSensitivity = "low" | "medium" | "high";"}"";"";
}";,"";
export interface AgentHealthStatus {";,}status: "healthy" | "degraded" | "error";",";
uptime: number,;
responseTime: number,;
accuracy: number,;
lastUpdate: Date,;
activeConnections: number,;
memoryUsage: number,;
}
}
  const errors = AgentError[];}
}
// 中医相关类型 * export interface TCMFindings {/;};/g/;
    ;
/    ;/;,/g/;
syndrome?: string;
pattern?: string;
organSystems?: string[];
pathogenesis?: string;
treatmentPrinciple?: string;
}
}
  prognosis?: string;}
}
export interface TCMDiagnosis {mainSyndrome: string}secondarySyndromes: string[],;
organSystems: string[],;
pathogenesis: string,;
treatmentPrinciples: string[],;
}
}
  prognosis: string,confidence: number;}";"";
};";,"";
export type ConstitutionType = | "balanced"  | "qi_deficiency"  / 气虚质*  阳虚质*  阴虚质*  痰湿质*  湿热质*  血瘀质*  气郁质* // | "special_diathesi;";"/;,"/g"/;
s";  * / 特禀质* ///     ""/;"/g"/;
// 错误处理 * export interface AgentError {/;}";,"/g,"/;
  code: string,";,"";
message: string,timestamp: Date,severity: "low" | "medium" | "high" | "critical";";"";
}
}
  context?: unknown;}
}
// 时间相关 * export interface TimeRange {/;,}start: Date,";,"/g"/;
const end = Date;";"";
}
}
  granularity?: "hour" | "day" | "week" | "month" | "year"}"";"";
}
// 小艾智能体接口 * export interface XiaoaiAgent {/;}/;/;,/g/;
chat(message: string, context: ChatContext): Promise<ChatResponse  /     >;/;,/g/;
processVoiceInput();
audioData: AudioData,language?: string;dialect?: string;
  ): Promise<VoiceResponse /    >;/;,/g/;
synthesizeVoice();
const text = string;
language?: string;
voice?: VoiceProfile;
  );: Promise<AudioData /    >/;,/g/;
performLookDiagnosis()";,"";
imageData: ImageData,";,"";
const type = "face" | "tongue" | "body"): Promise<LookResult /    >;"/;,"/g"/;
performListenDiagnosis()";,"";
audioData: AudioData,";,"";
const type = "voice" | "cough" | "breathing" | "other");: Promise<ListenResult /    >;"/;,"/g"/;
performInquiryDiagnosis();
const userId = string;
symptoms?: string[];
  );: Promise<InquiryResult /    >;/;,/g/;
performPalpationDiagnosis(data: PalpationData);: Promise<PalpationResult /    >;/;,/g/;
integrateFourDiagnosis();
const results = FourDiagnosisResults);: Promise<IntegratedDiagnosis /    >;/;,/g/;
analyzeHealthData(data: HealthDataInput): Promise<HealthAnalysis  /     >;/;,/g/;
generateHealthRecommendations();
const profile = UserProfile);: Promise<HealthRecommendation[] /    >;/;,/g/;
trackHealthTrends();
userId: string,;
const timeRange = TimeRange);: Promise<HealthTrends /    >;/;,/g/;
createMedicalRecord(data: MedicalRecordInput): Promise<MedicalRecord  /     >;/;,/g/;
updateMedicalRecord();
recordId: string,;
updates: Partial<MedicalRecord  />);: Promise<MedicalRecord  />;/      getMedicalHistory(, )/;,/g/;
const userId = string;);
filters?: MedicalHistoryFilters;);
  );: Promise<MedicalRecord[] /    >;/;,/g/;
generateHealthReport(userId: string, type: ReportType);: Promise<HealthReport /    >;/;,/g/;
enableAccessibilityFeature(feature: AccessibilityFeature): Promise<void>;
provideNavigationAssistance();
const context = NavigationContext);: Promise<NavigationGuidance /    >;/;,/g/;
recognizeSignLanguage(videoData: VideoData);: Promise<SignLanguageResult /    >;/;,/g/;
adaptInterfaceForDisability();
const disability = DisabilityType);: Promise<InterfaceAdaptation /    >;/;,/g/;
provideElderlyFriendlyInterface(): Promise<ElderlyInterfaceConfig /    >;/;,/g/;
assessConstitution();
const data = ConstitutionAssessmentData): Promise<ConstitutionResult /    >;/;,/g/;
performCalculationDiagnosis();
symptoms: string[],;
const context = DiagnosisContext);: Promise<CalculationResult /    >;/;,/g/;
generateTreatmentPlan();
diagnosis: IntegratedDiagnosis,;
const userProfile = UserProfile);: Promise<TreatmentPlan /    >;/;,/g/;
coordinateWithOtherAgents(task: AgentTask): Promise<AgentCoordinationResult  /     >;/;,/g/;
shareUserContext();
targetAgent: AgentType,;
const context = SharedContext);: Promise<void>;
setPersonality(traits: PersonalityTraits): void;
getPersonality(): PersonalityTraits;
getHealthStatus(): Promise<AgentHealthStatus  /     >/;/g/;
}
}
  cleanup(userId: string);: Promise<void>}
}
// 占位符类型定义 - 需要在其他文件中完整定义 * export interface AudioMetadata {/;}/;/;/g/;
}
}
  [key: string]: unknown;}
}
export interface ImageMetadata {;}}
}
  [key: string]: unknown;}
}
export interface VideoMetadata {;}}
}
  [key: string]: unknown;}
}
export interface HealthContext {;}}
}
  [key: string]: unknown;}
}
export interface AccessibilityNeeds {;}}
}
  [key: string]: unknown;}
}
export interface EmotionalState {;}}
}
  [key: string]: unknown;}
}
export interface EnvironmentContext {;}}
}
  [key: string]: unknown;}
}
export interface DiagnosticRecommendation {;}}
}
  [key: string]: unknown;}
}
export interface HealthInsight {;}}
}
  [key: string]: unknown;}
}
export interface AccessibilitySupport {;}}
}
  [key: string]: unknown;}
}
export interface EmotionalSupport {;}}
}
  [key: string]: unknown;}
}
export interface EmotionalTone {;}}
}
  [key: string]: unknown;}
}
export interface ColorAnalysis {;}}
}
  [key: string]: unknown;}
}
export interface FacialFeatures {;}}
}
  [key: string]: unknown;}
}
export interface TongueBodyAnalysis {;}}
}
  [key: string]: unknown;}
}
export interface TongueCoatingAnalysis {;}}
}
  [key: string]: unknown;}
}
export interface TongueShapeAnalysis {;}}
}
  [key: string]: unknown;}
}
export interface TongueMovementAnalysis {;}}
}
  [key: string]: unknown;}
}
export interface VoiceAnalysis {;}}
}
  [key: string]: unknown;}
}
export interface BreathingAnalysis {;}}
}
  [key: string]: unknown;}
}
export interface CoughAnalysis {;}}
}
  [key: string]: unknown;}
}
export interface HeartSoundAnalysis {;}}
}
  [key: string]: unknown;}
}
export interface SymptomAnalysis {;}}
}
  [key: string]: unknown;}
}
export interface HealthConcern {;}}
}
  [key: string]: unknown;}
}
export interface RiskFactor {;}}
}
  [key: string]: unknown;}
}
export interface TCMSyndrome {;}}
}
  [key: string]: unknown;}
}
export interface PulseAnalysis {;}}
}
  [key: string]: unknown;}
}
export interface PressurePointAnalysis {;}}
}
  [key: string]: unknown;}
}
export interface WesternMedicineCorrelation {;}}
}
  [key: string]: unknown;}
}
export interface Treatment {;}}
}
  [key: string]: unknown;}
}
export interface LifestyleRecommendation {;}}
}
  [key: string]: unknown;}
}
export interface FollowUpPlan {;}}
}
  [key: string]: unknown;}
}
export interface VitalSigns {;}}
}
  [key: string]: unknown;}
}
export interface LifestyleData {;}}
}
  [key: string]: unknown;}
}
export interface MedicalHistoryItem {;}}
}
  [key: string]: unknown;}
}
export interface LabResult {;}}
}
  [key: string]: unknown;}
}
export interface DeviceData {;}}
}
  [key: string]: unknown;}
}
export interface EnvironmentalData {;}}
}
  [key: string]: unknown;}
}
export interface RiskAssessment {;}}
}
  [key: string]: unknown;}
}
export interface HealthTrend {;}}
}
  [key: string]: unknown;}
}
export interface HealthAlert {;}}
}
  [key: string]: unknown;}
}
export interface TCMHealthAssessment {;}}
}
  [key: string]: unknown;}
}
export interface HealthPattern {;}}
}
  [key: string]: unknown;}
}
export interface HealthPrediction {;}}
}
  [key: string]: unknown;}
}
export interface ImplementationGuide {;}}
}
  [key: string]: unknown;}
}
export interface AccessibilityPreferences {;}}
}
  [key: string]: unknown;}
}
export interface HapticPattern {;}}
}
  [key: string]: unknown;}
}
export interface VisualCue {;}}
}
  [key: string]: unknown;}
}
export interface Landmark {;}}
}
  [key: string]: unknown;}
}
export interface RecognizedSign {;}}
}
  [key: string]: unknown;}
}
export interface VisualAdaptation {;}}
}
  [key: string]: unknown;}
}
export interface AudioAdaptation {;}}
}
  [key: string]: unknown;}
}
export interface InteractionAdaptation {;}}
}
  [key: string]: unknown;}
}
export interface ContentAdaptation {;}}
}
  [key: string]: unknown;}
}
export interface PhysicalCharacteristics {;}}
}
  [key: string]: unknown;}
}
export interface PsychologicalTraits {;}}
}
  [key: string]: unknown;}
}
export interface EnvironmentalFactors {;}}
}
  [key: string]: unknown;}
}
export interface ConstitutionScore {;}}
}
  [key: string]: unknown;}
}
export interface ConstitutionRecommendation {;}}
}
  [key: string]: unknown;}
}
export interface SeasonalGuidance {;}}
}
  [key: string]: unknown;}
}
export interface PrescriptionRecommendation {;}}
}
  [key: string]: unknown;}
}
export interface PrognosisAssessment {;}}
}
  [key: string]: unknown;}
}
export interface TaskContext {;}}
}
  [key: string]: unknown;}
}
export interface AgentTaskResult {;}}
}
  [key: string]: unknown;}
}
export interface Location {;}}
}
  [key: string]: unknown;}
}
export interface Medication {;}}
}
  [key: string]: unknown;}
}
export interface HealthGoal {;}}
}
  [key: string]: unknown;}
}
export interface NotificationPreferences {;}}
}
  [key: string]: unknown;}
}
export interface CulturalPreferences {;}}
}
  [key: string]: unknown;}
}
export interface CulturalBackground {;}}
}
  [key: string]: unknown;}
}
export interface MedicalRecord {;}}
}
  [key: string]: unknown;}
}
export interface MedicalRecordInput {;}}
}
  [key: string]: unknown;}
}
export interface MedicalHistoryFilters {;}}
}
  [key: string]: unknown;}
}
export interface ReportType {;}}
}
  [key: string]: unknown;}
}
export interface HealthReport {;}}
}
  [key: string]: unknown;}
}
export interface NavigationContext {;}}
}
  [key: string]: unknown;}
}
export interface DisabilityType {;}}
}
  [key: string]: unknown;}
}
export interface ElderlyInterfaceConfig {;}}
}
  [key: string]: unknown;}
}
export interface DiagnosisContext {;}}
}
  [key: string]: unknown;}
}
export interface TreatmentPlan {;}}
}
  [key: string]: unknown;}
}
export interface SharedContext {;}}
}
  [key: string]: unknown;}";"";
};""";