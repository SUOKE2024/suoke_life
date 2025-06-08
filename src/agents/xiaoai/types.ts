// 诊断服务类型定义
// 基础数据类型
export interface ImageData {
  data: ArrayBuffer;
  format: string;
  width: number;
  height: number;
  metadata?: Record<string, any>;
}
export interface AudioData {
  data: ArrayBuffer;
  format: string;
  duration: number;
  sampleRate: number;
  channels?: number;
  metadata?: Record<string, any>;
}
export interface PalpationData {
  type: 'pulse' | 'touch' | 'pressure';
  sensorData: Record<string, any>;
  metadata?: Record<string, any>;
}
// 诊断结果类型
export interface InquiryResult {
  sessionId: string;
  response: string;
  extractedSymptoms: string[];
  confidence: number;
  nextQuestions: string[];
  isComplete: boolean;
}
export interface LookResult {
  analysisId: string;
  faceFeatures?: Record<string, any>;
  complexionAnalysis?: Record<string, any>;
  tongueAnalysis?: Record<string, any>;
  overallAssessment: string;
  confidence: number;
  recommendations?: string[];
}
export interface ListenResult {
  analysisId: string;
  voiceFeatures?: Record<string, any>;
  breathingPattern?: Record<string, any>;
  overallAssessment: string;
  confidence: number;
}
export interface PalpationResult {
  analysisId: string;
  pulseAnalysis?: Record<string, any>;
  abdominalAnalysis?: Record<string, any>;
  skinAnalysis?: Record<string, any>;
  overallAssessment: string;
  confidence: number;
}
// 服务客户端接口
export interface InquiryServiceClient {
  startSession(userId: string): Promise<string>;
  askQuestion(sessionId: string, question: string): Promise<InquiryResult>;
  getSymptomAnalysis(sessionId: string): Promise<any>;
}
export interface LookServiceClient {
  analyzeFace(imageData: ImageData): Promise<LookResult>;
  analyzeTongue(imageData: ImageData): Promise<LookResult>;
}
export interface ListenServiceClient {
  analyzeVoice(audioData: AudioData): Promise<ListenResult>;
  analyzeBreathing(audioData: AudioData): Promise<ListenResult>;
}
export interface PalpationServiceClient {
  analyzePalpation(data: PalpationData): Promise<PalpationResult>;
  startRealTimeMonitoring(userId: string): Promise<string>;
}
export interface DiagnosisServiceClient {
  inquiry: InquiryServiceClient;
  look: LookServiceClient;
  listen: ListenServiceClient;
  palpation: PalpationServiceClient;
  healthCheck(): Promise<{ [key: string]: boolean;
}>;
  comprehensiveDiagnosis(data: {,
  userId: string;
    imageData?: ImageData;
    audioData?: AudioData;
    palpationData?: PalpationData;
    symptoms?: string[];
  }): Promise<any>;
  clearCache(): void;
}